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
import numbers
import time

import tornado.ioloop
import tornado.web
import tornado.template
import json

import subprocess

def gethome():
    global  HOMEDIR
    return HOMEDIR

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
        f = open(gethome()+"/"+"sysconfig.json", "r")
        js = json.load(f)
        f.close()
           
        self.render(gethome()+"/"+"index.html", host=host, ipaddr=js["ipaddr"])

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
        <li><a href="{{ path }}/{{ filename }}">{{ filename }}</a>
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
    def float_vert(self,v):
        try:
            x = float(v)
        except:
            return ("BAD")
        return x

    def varsub(self,x,vl):
        for v in vl:
            x = x.replace("@@"+v, str(vl[v]))
        return x

    @tornado.web.authenticated
    def get(self,path):
        try:
            fp = open(gethome()+"/"+"experiments.json", "r")
        except:
            self.write("Internal Error -- experiment control file failed")
            return
        
        try:
            experiments = json.load(fp)
            fp.close()
        except:
            self.write("Internal error -- JSON load failed")
            return
        
        try:
            fp = open(gethome()+"/"+"sysconfig.json", "r")
        except:
            self.write("Internal Error -- cannot open sysconfig file")
            return
        
        try:
            sysconfig = json.load(fp)
        except:
            self.write("Internal error -- JSON load for sysconfig failed")
            return

            
        me = sysconfig["hwtype"]
        commands = experiments["commands"]
        hlist = experiments["hwtypes"]
        if (me not in hlist):
            self.write("Internal error -- hwtype %s not in database" % me)
            return
        
        varlist = {}
        
        hwtype = hlist[me]
        frange = hwtype["freqs"]
        slist = hwtype["rates"]
        grange = hwtype["rfgains"]
        
        freq = self.float_vert(self.get_argument ("freq", "1420.4058e6"))
        varlist["freq"] = freq
        
        srate = self.float_vert(self.get_argument ("srate", "1.0"))
        varlist["srate"] = srate*1.0e6
        varlist["abw"] = (srate*0.90)*1.0e6
        
        integration = self.float_vert(self.get_argument ("integration", "10"))
        varlist["alpha"] = 1.0/integration
        
        longitude = self.float_vert(self.get_argument ("longitude", "-76.03"))
        varlist["longitude"] = longitude
        
        latitude = self.float_vert(self.get_argument ("latitude", "44.9"))
        varlist["latitude"] = latitude
        
        rfgain = self.float_vert(self.get_argument ("rfgain", "20"))
        varlist["rfgain"] = rfgain
        
        declination = self.float_vert(self.get_argument("declination", "41.0"))
        varlist["declination"] = declination
        
        varlist["rmount"] = self.get_argument("rmount", "//NONE")
        varlist["ruser"] = self.get_argument("ruser", "nobody")
        varlist["rpassword"] = self.get_argument("rpassword", "GoopldyGock")
        varlist["expname"] = self.get_argument("expname", "UNKNOWN")
        
        speclog = self.get_argument("speclog", "False")
        if (speclog == "on"):
            specbool = 1
        else:
            specbool = 0
        varlist["speclog"] = specbool
        
        
        for key in hwtype:
            if (type(hwtype[key]) is not list):
                varlist[key] = hwtype[key]
        
        etypedict = {"pulsar" : "Pulsar", "radiometer" : "Combo-Radiometer"}
        etype = self.get_argument("etype", "radiometer")
        if (etype not in etypedict):
            self.write ("Experiment type %s is unknown" % etype)
            return
        
        key = etypedict[etype]
        if (key not in hwtype):
            self.write ("Experiment type %s is not supported by this hardware" % key)

        softconfig = hwtype[key]
        
        
        if "BAD" in [freq,srate,integration,longitude,latitude,rfgain,declination]:
            self.write("Invalid floating-point input")
            return
        
        if (not (frange[0]*1.0e6 <= freq and freq <= frange[1]*1.0e6)):
            self.write ("Error in frequency input: must be between %f and %f MHz" % (frange[0], frange[1]))
            return
         
        if (not (srate in slist)):
            self.write ("Error in sample rate--invalid rate, must be in %s" % str(slist))
            return
        
        if (not (-180.0 <= longitude and longitude <= 180.0)):
            self.write ("Error in longitude input -- out of range")
        
        if (not (-90 <= latitude and latitude <= 90)):
            self.write ("Error in latitude input -- out of range")
            return
        
        if (not (-90 <= declination and declination <= 90)):
            self.write ("Error in declination input -- out of range")
            return
        
        if (softconfig not in commands):
            self.write ("Command profile for %s not in configuration" % softconfig)
            return
            
        
        try:
            f = open (gethome()+"/"+"experiment.pid", "r")
            l = f.readline().strip('\n')
            os.kill(int(l),signal.SIGINT)
            time.sleep(0.5)
            os.kill(int(l),signal.SIGHUP)
            time.sleep(2.0)
        except:
            pass
            
        cmdstr = ""
        saved_commands = ""
        for x in commands[softconfig]:
            cmdstr = ""
            cls = experiments[x]
            for l in cls:
                cmdstr = cmdstr + self.varsub(l,varlist) + " "
              
            p = subprocess.Popen (cmdstr, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            outs = p.communicate()
            r = p.wait()
            if (r != 0):
                self.write ("Process failed to start correctly")
                self.write (outs[0])
                self.write (outs[1])
            
            saved_commands += cmdstr
            saved_commands += "\n"
            
        f = open (gethome()+"/"+"experiment.pid", "r")
        pid = int(f.readline().strip('\n'))
        f.close()
        self.write ("Experiment %s started with PID %d\n<br>" % (varlist["expname"], pid))
        
        print "save %s" % self.get_argument("save", "off")
        print "startup %s" % self.get_argument("startup", "off")
        
        if (self.get_argument("save", "off") == "on"):
            fn = "%s.sh" % varlist["expname"]
            f = open(fn, "w")
            f.write (saved_commands)
            f.close()
            os.chmod(fn, 0755)
            self.write("Saved experiment profile %s\n<br>" % fn)
            
        
        if (self.get_argument("startup", "off") == "on"):
            f = open("reboot_name.txt", "w")
            f.write(varlist["expname"]+"\n")
            f.close()
            self.write("Saved experiment profile %s to reboot\n<br>" % varlist["expname"])
        else:
            try:
                os.remove("reboot_name.txt")
            except:
                pass
        
        try:
            f = open(varlist["local"] + "/" + varlist["expname"] + "-notes.txt", "w")
            f.write(self.get_argument("notes", "None"))
            f.write("\n")
            f.close()
        except:
            pass
        return
        


class StopHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self,path):
        try:
            fp = open(gethome()+"/"+"experiment.pid", "r")
        except:
            self.write("No Process to stop")
            return
    
        pid = fp.readline().strip("\n")
        fp.close()
        pid = int(pid)
        
        try:
            os.kill(pid, signal.SIGINT)
            time.sleep(0.25)
            os.kill(pid, signal.SIGHUP)
        except:
            self.write("No process to stop")
            os.remove(gethome()+"/"+"experiment.pid")
            return
        
        self.write ("Stopped process %d" % pid)
        return
        
class RestartHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self,path):
        
        expname = self.get_argument("expname", "???")
        fn = expname+".sh"
        
        if not os.path.exists(fn):
            self.write ("Could not find experiment profile %s" % expname)
            return
        
        pidfile = False
        try:
            fp = open(gethome()+"/"+"experiment.pid", "r")
            pidfile = True
        except:
            pass
        
        if (pidfile != False):
            pid = fp.readline().strip("\n")
            fp.close()
            pid = int(pid)
            
            try:
                os.kill(pid, signal.SIGINT)
                time.sleep(0.25)
                os.kill(pid, signal.SIGHUP)
            except:
                pass
        
        p = subprocess.Popen(gethome()+"/"+fn, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        outs = p.communicate()
        r = p.wait()
        if r != 0:
            self.write(outs[0])
            self.write(outs[1])
            return
        
        f = open (gethome()+"/"+"experiment.pid", "r")
        pid = int(f.readline().strip('\n'))
        f.close()
        
        self.write ("Re-started experiment %s with pid %d" % (expname, pid))
        
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
        badchars = ['<', '>', '{', '}','@', ':', '!', '%', '#', '*', '(', ')']
        #
        # Create trimmed versions of user/pw
        #
        user = self.get_argument("name")
        user = user[0:15]
        for bad in badchars:
            user = user.replace(bad, "")
        
        
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
        (r"/(Documents)/$", IndexHandler),
        (r"/(Documents)$", IndexHandler),
        (r"/(astro_data)$", IndexHandler),
        (r"/(transparent-logo\.png)", Handler, {'path' : gethome()}),
        (r"/astro_data/(.*)", Handler, {'path': gethome()+"/"+"astro_data"}),
        (r"/Documents/(.*)", Handler, {'path' : gethome()+"/"+"Documents"}),
        (r"/(real-time\.html)", Handler, {'path' : gethome()}),
        (r"/(expcontrol\.html)", Handler, {'path' : gethome()}),
        (r"/(jquery.*\.js)", Handler, {'path' : gethome()}),
        (r"/(experiment.*\.json)", Handler, {'path' : gethome()}),
        (r"/(sysconfig\.json)", Handler, {'path' : gethome()}),
        (r"/(start\.html)", StartHandler),
        (r"/(stop\.html)", StopHandler),
        (r"/(restart\.html)", RestartHandler)
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
    global HOMEDIR
    
    HOMEDIR=os.path.realpath(".")
    
    try:
        f = open("experiments.json", "r")
    except:
        print "Could not open experiments.json"
        sys.exit()
    
    #
    # Jsonify
    #
    exp = json.load(f)
    f.close()
    
        
    p = subprocess.Popen("lsusb", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    outs = p.communicate()
    usblines = outs[0].split("\n")
    
    usbcount = 0
    usbtype = "Unknown"
    for t in exp["usbtypes"]:
        for l in usblines:
            if t in l:
                usbcount += 1
                usbtype = exp["usbtypes"][t]
        if (usbcount > 0):
            break
    
    hwtype = "%s-%d" % (usbtype, usbcount)
    
    p = subprocess.Popen("ifconfig eth0", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    outs = p.communicate()
    ethlines = outs[0].split("\n")
    
    for l in ethlines:
        if ("inet" in l):
            ethtoks = l.strip(" ").split(" ")
            break
    
    ipaddr = ethtoks[1]
    
    f = open("/etc/hostname", "r")
    l = f.readline()
    host = l.strip("\n")
    f.close()
    
    dic = {"hostname" : host, "ipaddr" : ipaddr, "hwtype" : hwtype} 
    
    f = open("sysconfig.json", "w")
    f.write(json.dumps(dic, indent=4))
    f.close()
    
    print('Starting server on port 8000')
    start_server(port=8000)


if __name__ == '__main__':
    sys.exit(main())
