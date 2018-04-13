#!/usr/bin/env python
"""
A custom server for back-of-the-dish CCERA Radio Telescope System

"""


import os
import signal
import sys
from argparse import ArgumentParser
import pwd
import spwd
import crypt

import tornado.ioloop
import tornado.web
import tornado.template

class TopLevelHandler(tornado.web.RequestHandler):
    SUPPORTED_METHODS = ['GET']
    def set_extra_headers(self, path):
        # Disable cache
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
    def get(self):
        try:
            fp = open("/etc/hostname", "r")
            host=fp.readline().strip('\n')
            fp.close()
        except:
            host="Unknown"
            
        self.render("/home/astronomer/index.html", host=host)

class IndexHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")
    def set_extra_headers(self, path):
        # Disable cache
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
    SUPPORTED_METHODS = ['GET']
    @tornado.web.authenticated
    def get(self, path):
        """ GET method to list contents of directory or
        write index page if index.html exists."""

        # remove heading slash
        #path = path[1:]

        for index in ['index.html', 'index.htm']:
            index = os.path.join(path, index)
            if os.path.exists(index):
                with open(index, 'rb') as f:
                    self.write(f.read())
                    self.finish()
                    return
        html = self.generate_index(path)
        self.write(html)
        self.finish()

    def generate_index(self, path):
        """ generate index html page, list all files and dirs.
        """
        if path:
            files = os.listdir(path)
        else:
            files = os.listdir('.')
        files = [filename + '/'
                if os.path.isdir(os.path.join(path, filename))
                else filename
                for filename in files]
        html_template = """
        <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN"><html>
        <title>Directory listing for /{{ path }}</title>
        <body>
        <h2>Directory listing for /{{ path }}</h2>
        <hr>
        <ul>
        {% for filename in files %}
        <li><a href="{{ filename }}">{{ filename }}</a>
        {% end %}
        </ul>
        <hr>
        </body>
        </html>
        """
        t = tornado.template.Template(html_template)
        return t.generate(files=files, path=path)


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")


class Handler(tornado.web.StaticFileHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")
    @tornado.web.authenticated
    def set_extra_headers(self, path):
        # Disable cache
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
    def parse_url_path(self, url_path):
        if not url_path or url_path.endswith('/'):
            url_path = url_path + 'index.html'
        return url_path

class StartHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self,path):
        try:
            fp = open("/home/astronomer/experiments.json", "r")
        except:
            self.write("Internal Error -- experiment control file failed")
            return
        
        try:
            experiments = json.load(fp)
            fp.close()
        except:
            self.write("Internal error -- JSON load failed")
            return
        

class StopHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self,path):
        try:
            fp = open("/home/astronomer/radiometer.pid", "r")
        except:
            self.write("No Process to stop")
            return
    
        pid = fp.readline().strip("\n")
        fp.close()
        pid = int(pid)
        
        try:
            os.kill(pid, signal.SIGINT)
        except:
            self.write("No process to stop")
            os.remove("/home/astronomer/radiometer.pid", "r")
            return
        
        self.write ("Stopped process %d" % pid)
        return
        
        

class LoginHandler(BaseHandler):
    def get(self):
        n = self.get_argument ("next", "/")
        loginpage = ('<html><body bgcolor="lightgrey"><form action="/login" method="post">'
		'<h3>Radio Telescope Data System</h3>'
		'Username: <input type="text" name="name">'
		'<br>'
		'Password: <input type="password" name="pw">'
		'<input type="hidden" name="next" value="@@@@">'
		'<input type="submit" value="Sign in">'
		'</form></body></html>')
        loginpage = loginpage.replace('@@@@', n)
        self.write(loginpage)

    def post(self):
        
        #
        # Create trimmed versions of user/pw
        #
        user = self.get_argument("name")
        user = user[0:15]
        user = user.replace("/", "")
        user = user.replace("@", "")
        user = user.replace(":", "")
        user = user.replace("!", "")
        
        pw = self.get_argument("pw")
        pw = pw[0:63]
        
        #
        # Setup error / success HTML snipphttp://www.tornadoweb.org/en/stable/guide/security.htmets
        #
        errstr = "<html><body><h3>Unknown Username or Password</h3></body></html>"
        goodstr = "<html><body><h3>Login successful</h3></body></html>"
        
        #
        # First try to find in regular password file
        #
        try:
            pw_struct = pwd.getpwnam(user)
        except:
            self.write(errstr)
            return
        #
        # Has low UID?  Fuggedaboudid
        #
        if (pw_struct.pw_uid < 10):
            self.write(errstr)
            return
        
        #
        # Next, try to get password from shadow pw file
        #  On our system, we leave the file readable by everyone
        #  Low risk--this is an embedded system with one or two
        #    "users", and regular login isn't a normal thing.
        #   
        try:
            spw_struct = spwd.getspnam(user)
        except:
            self.write(errstr)
            return
        
        #
        # OK, now do the password check
        #
        # Encrypt the entered password using the salt from the
        #   shadow file.  Compare results.
        #  
        epassword = crypt.crypt(pw, spw_struct.sp_pwd)
        if (epassword != spw_struct.sp_pwd):
            self.write(errstr)
            return
        else:
            self.write(goodstr)
            self.set_secure_cookie("user", user)
            self.redirect(self.get_argument("next", u"/"))

def mkapp(cookie_secret):
    application = tornado.web.Application([
        (r"/index.html", TopLevelHandler),
        (r"/$", TopLevelHandler),
        (r"/login", LoginHandler),
        (r"/(.*)/$", IndexHandler),
        (r"/(astro_data)$", IndexHandler),
        (r"/astro_data/(.*)", Handler, {'path': "/home/astronomer/astro_data"}),
        (r"/(real-time\.html)", Handler, {'path' : "/home/astronomer"}),
        (r"/(expcontrol\.html)", Handler, {'path' : "/home/astronomer"}),
        (r"/(jquery.*\.js)", Handler, {'path' : "/home/astronomer"}),
        (r"/(experiment.*\.json)", Handler, {'path' : "/home/astronomer"}),
        (r"/(start\.html)", StartHandler),
        (r"/(stop\.html)", StopHandler)
    ], debug=False, cookie_secret=cookie_secret, login_url="/login")

    return application

import random
def start_server(port=8000):
    
    #
    # Deal with cookie secret
    #
    rf = open("/dev/urandom", "r")
    rv = rf.read(32)
    rv = rv.encode('hex')
    rf.close()
    
    try:
        f=open(".cookie_secret", "r")
    except:
        f=open(".cookie_secret", "w")
        f.write(rv+"\n")
        f.close()
        f=open(".cookie_secret", "r")
    
    cook = f.read()
    cook = cook.strip('\n')
    
    app = mkapp(cook)
    app.listen(port)
    tornado.ioloop.IOLoop.instance().start()


def main(args=None):
    print('Starting server on port 8000')
    start_server(port=8000)


if __name__ == '__main__':
    sys.exit(main())
