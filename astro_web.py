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
import struct

import tornado.ioloop
import tornado.web
import tornado.template
import json
import tempfile

import re
import socket

import subprocess

def gethome():
    global  HOMEDIR
    return HOMEDIR

def getluser():
    global USER
    return USER
    
def killit(pid):
    try:
        os.kill(pid, signal.SIGTERM)
    except:
        return(-1)
    
    time.sleep(0.5)
    
    #
    # Loop for a bit watching for the process to die
    # If it doesn't, then return a "can't seem to kill it"
    #   return code.
    #
    retval = -1
    trycnt = 0
    while trycnt <= 10 and retval == -1:
        try:
            retval = -1
            os.kill(pid, 0)
            time.sleep(0.25)
            trycnt += 1
        except:
            retval = 0
            pass
        
    return(retval)

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

class PwChangeHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")
    SUPPORTED_METHODS = ['GET']
    @tornado.web.authenticated
    def set_extra_headers(self, path):
        # Disable cache

        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
    def get(self,path):
        user = getluser()
        opw = self.get_argument("opassword", "???")
        npw1 = self.get_argument("npassword1", "???")
        npw2 = self.get_argument("npassword2", "???")
        
        if (npw1 != npw2):
            self.write ("<html><body><h3>New Passwords do not match</h3></body></html>")
            return
        
        #
        # Setup error / success HTML snipphttp://www.tornadoweb.org/en/stable/guide/security.htmets
        #
        errstr = "<html><body><h3>Unknown Username or Password</h3></body></html>"
        goodstr = "<html><body><h3>Password Update successful</h3></body></html>"
        
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
        if (pw_struct.pw_uid < 1000):
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
        epassword = crypt.crypt(opw, spw_struct.sp_pwd)
        if (epassword != spw_struct.sp_pwd):
            self.write(errstr)
            return
        #
        # We updated sudoers to allow astronomer to do anything via sudo
        #
        pip = subprocess.Popen("sudo chpasswd" % (user,npw2), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        outs = pip.communicate("%s:%s\n" % (user,npw2))
        r = pip.returncode
        if (r != 0):
            self.write(errstr)
            self.write("<html><body><pre>")
            self.write(outs[0])
            self.write(outs[1])
            self.write("</pre></body></html>")
        else:
            self.write(goodstr)
        
       
class ExpControlHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")
    SUPPORTED_METHODS = ['GET']
    def set_extra_headers(self, path):
        # Disable cache

        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
    def get(self,path):
        try:
            fp = open("/etc/hostname", "r")
            host=fp.readline().strip('\n')
            fp.close()
        except:
            host="Unknown"
        
        running = "None"
        plist = ""
        pid = -1
        try:
            f = open(gethome()+"/"+"experiment.pid", "r")
            l = f.readline().strip('\n')
            f.close()
            pid = int(l)
        except:
            pass
        
        if (pid != -1):
            try:
                os.kill (pid, 0)
            except:
                pid = -1
        
        if (pid != -1):
            try:
                f = open (gethome()+"/"+"astro_data/tpower.json")
                js = json.load(f)
                f.close()
                running = js["expname"]
            except:
                pass

        plist=""
        dls = os.listdir(gethome())
        
        for n in dls:
            if (".sh" in n):
                plist = plist + " " + n.replace(".sh", "")
        start_profile = "Not present"
        try:
            f = open(gethome()+"/"+"reboot_name.txt", "r")
            start_profile = f.readline().strip('\n')
            f.close()
        except:
            pass

        currlog = ""
        try:
            f = open (gethome()+"/astro_data/"+running+".log", "r")
            currlog=f.read()
            f.close()
        except:
            pass
            
        
        f = open(gethome()+"/"+"sysconfig.json", "r")
        js = json.load(f)
        f.close()
        self.render(gethome()+"/"+"expcontrol.html", host=host,
            ipaddr=js["ipaddr"],
            running=running,
            plist=plist,
            startup=start_profile,
            pid=str(pid), currlog=currlog)

import re         
class SysControlHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")
    SUPPORTED_METHODS = ['GET']
    def set_extra_headers(self, path):
        # Disable cache

        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
    def get(self,path):
        ntpservers=""
        f = open(gethome()+"/"+"sysconfig.json", "r")
        js = json.load(f)
        f.close()
        ntpconf = False
        try:
            f = open("/etc/systemd/timesyncd.conf", "r")
            ntplines=f.readlines()
            f.close()
            ntpconf = True
        except:
            pass
            
        gateway=""
        netmask=""
        dns=""
        
        netconf = False
        try:
            f = open ("/etc/systemd/network/eth0.network", "r")
            netlines = f.readlines()
            f.close()
            netconf = True
        except:
            pass
        
        if (ntpconf == True):
            for l in ntplines:
                if (re.match("NTP=..+", l)):
                    ntpservers = l[len("NTP="):]
                    ntpservers = ntpservers.strip("\n")
        
        if (netconf == True):
            for l in netlines:
                if (re.match("Gateway=..+", l)):
                    gateway = l[len("Gateway="):]
                    gateway = gateway.strip("\n")
                if (re.match("DNS=..+", l)):
                    dns = l[len("DNS="):]
                    dns = dns.strip("\n")
                if (re.match("Address=..+", l)):
                    a = l.strip('\n')
                    a = a.split("/")
                    a = int(a[1])
                    m = 0
                    for i in range(0,a):
                        m |= 1<<(31-i)
                    ml = struct.pack("I", m)
                    mask=[]
                    mask.append(struct.unpack('B', ml[3])[0])
                    mask.append(struct.unpack('B', ml[2])[0])
                    mask.append(struct.unpack('B', ml[1])[0])
                    mask.append(struct.unpack('B', ml[0])[0])
                    print mask[0]
                    netmask = "%d.%d.%d.%d" % (mask[0], mask[1], mask[2], mask[3])
                        

        self.render(gethome()+"/"+"syscontrol.html", hostname=js["hostname"],
            ipaddr=js["ipaddr"],ntpservers=ntpservers, gateway=gateway, netmask=netmask, dns=dns)

class IndexHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")
    
    def set_extra_headers(self, path):
        # Disable cache
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
    SUPPORTED_METHODS = ['GET']
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

    def get(self,path):
        try:
            fp = open(gethome()+"/"+"experiments.json", "r")
        except:
            self.write("Internal Error -- experiment control file open failed\n")
            return
        
        try:
            experiments = json.load(fp)
            fp.close()
        except:
            self.write("Internal error -- JSON load failed\n")
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
        varlist["excl"] = self.get_argument("excl", "none")
        
        if (varlist["excl"] == ""):
            varlist["excl"] = "none"
        
        speclog = self.get_argument("speclog", "False")
        if (speclog == "on"):
            specbool = 1
        else:
            specbool = 0
        varlist["speclog"] = specbool
        
        
        for key in hwtype:
            if (type(hwtype[key]) is not list):
                varlist[key] = hwtype[key]
        
        etypes = ["radiometer", "fast", "d1", "pulsar"]
        etype = self.get_argument("etype", "radiometer")
        if (etype not in etypes):
            self.write ("Experiment type %s is unknown" % etype)
            return
        
        key = etype
        if (key not in hwtype):
            self.write ("Experiment type %s is not supported by this hardware" % key)
            return

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
            
        rv = 0
        try:
            f = open (gethome()+"/"+"experiment.pid", "r")
            l = f.readline().strip('\n')
            f.close()
            if (killit(int(l)) == -1):
                self.write ("Failed to kill previous process: %d\n" % int(l))
            time.sleep(1.0)
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

class RebootHandler(BaseHandler):

    def get(self,path):
        self.write("Rebooting...")
        time.sleep(5)
        p = subprocess.Popen("sync; sudo reboot", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        outs = p.communicate()
        r = p.wait()
        
        return

class HaltHandler(BaseHandler):

    def get(self,path):
        self.write("Halting...")
        time.sleep(5)
        p = subprocess.Popen("sync; sudo halt", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        outs=p.communicate()
        r = p.wait()
        
        return

class SysUpdateHandler(BaseHandler):

    def get(self,path):
        newip = self.get_argument("newip", "")
        newmask = self.get_argument("newmask", "")
        newhost = self.get_argument("newhost", "")
        newdns = self.get_argument("newdns", "")
        newgateway = self.get_argument("newgateway", "")
        newntp = self.get_argument("ntpservers", "")
        reboot = self.get_argument("reboot", "off")
        
        if (newip != ""):
            try:
                t = socket.inet_aton(newip)
            except:
                self.write ("Invalid IP address entered (%s)" % newip)
                return
        if (newmask != ""):
            try:
                t = socket.inet_aton(newmask)
            except:
                self.write ("Invalid IP netmask entered (%s)" % newmask)
                return
        
        ti = struct.unpack('i', t)
        masklen = bin(ti[0]).count("1")
        
        if (newdns != ""):
            try:
                t = socket.inet_aton(newdns)
            except:
                self.write("Invalid DNS address entered (%s)" % newdns)
                return
                
        if (newgateway != ""):
            try:
                t = socket.inet_aton(newgateway)
            except:
                self.write("Invalid Gateway address entered (%s)" % newgateway)
                return

        newhost = newhost[0:32]
        if (not re.match("[a-zA-Z0-9-.]+",newhost)):
            self.write ("Invalid characters in hostname (%s)" % newhost)
            return
        
        
        #
        # Update /etc/hostname
        #
        tf = tempfile.mkstemp()
        tname = tf[1]
        f = os.fdopen(tf[0], "w")
        f.write(newhost+"\n")
        f.close()
        p = subprocess.Popen("sudo cp %s /etc/hostname" % tname, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        outs = p.communicate()
        os.remove(tname)
        r = p.wait()
        
        if (r != 0):
            self.write("Failed to update /etc/hostname")
        else:
            self.write("Updated /etc/hostname")
        
        #
        # Update /etc/systemd/network/eth0.network
        #
        
        tf = tempfile.mkstemp()
        tname = tf[1]
        f = os.fdopen(tf[0], "w")
        #
        # Write stuff
        #
        w="""
[Match]
Name=eth0

[Network]
DNS={newdns}
Address={newip}/{masklen}
Gateway={newgateway}

""".format(newip=newip, newgateway=newgateway, newdns=newdns, masklen=masklen)
        f.write(w+"\n")
        f.close()
        p = subprocess.Popen("sudo cp %s /etc/systemd/network/eth0.network" % tname, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        outs = p.communicate()
        os.remove(tname)
        r = p.wait()
        if (r != 0):
            self.write ("Failed to update eth0.network")
        else:
            self.write ("Updated eth0.network")
            
        
        #
        # Update /etc/systemd/timesyncd.conf
        #
        if (newntp != ""):
            
            ntpline="NTP="+newntp+"\n"
            f = open ("/etc/systemd/timesyncd.conf", "r")
            tslines = f.readlines()
            f.close()
            
            tf = tempfile.mkstemp ()
            tfname = tf[1]
            f = os.fdopen(tf[0], "w")
            
            ntpwritten = False
            for l in tslines:
                if (re.match("NTP=..+", l)):
                    f.write (ntpline)
                    ntpwritten = True
                else:
                    f.write(l)
                    
            if (ntpwritten != True):
                f.write(ntpline)         
            f.close()
            p = subprocess.Popen("sudo cp %s /etc/systemd/timesyncd.conf" % tname, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            outs = p.communicate()
            os.remove(tname)
            r = p.wait()
            if (r != 0):
                self.write ("Failed to updated timesyncd.conf")
            else:
                self.write ("Updated timesyncd.conf")
                
            
            if (reboot == "on"):
                self.write ("Rebooting system...")
                time.sleep(5)
                p = subprocess.Popen("sync; sudo reboot", shell=True, stdout=subprocess.PIPE, stderr=subprocess.pipe)
                outs = p.communicate()
                r = p.wait()
        return
     
class StopHandler(BaseHandler):

    def get(self,path):
        pfn = gethome()+"/"+"experiment.pid"
        try:
            fp = open(pfn, "r")
        except:
            self.write("No Process to stop\n")
            return
    
        pid = fp.readline().strip("\n")
        fp.close()
        pid = int(pid)
        
        rv = 0
        try:
            rv = killit(pid)
            time.sleep(1.0)
        except:
            self.write("No process to stop")
            os.remove(gethome()+"/"+"experiment.pid")
            return
        
        if (rv == 0):
            self.write ("Stopped process %d\n" % pid)
            os.remove(pfn)
        else:
            self.write ("Failed to stop process %d\n" % pid)
        return

class ProfileHandler(BaseHandler):

    def get(self,path):
        expname = self.get_argument("expname", "")
        action = self.get_argument("action", "none")
        actions = ["delete", "add", "startup"]
        
        if action not in actions:
            self.write ("No or invalid action selected, doing nothing")
            return
        
        if action == "startup" and expname != "":
            self.write ("Profile name must be blank for Remove from Startup")
            return
            
        pfn = gethome() + "/" + expname + ".sh"
        if expname != "":
            if action == "delete":
                if (os.path.exists(pfn)):
                    os.remove (pfn)
                    self.write ("Removed profile %s" % expname)
                else:
                    self.write ("No such experiment profile %s" % expname)
                    return
            if action == "add":
                if os.path.exists(pfn):
                    f = open (gethome() + "/reboot_name.txt", "w")
                    f.write(expname+"\n")
                    f.close()
                    self.write ("Added profile %s to system startup" % expname)
                else:
                    self.write ("No such experiment profile %s" % expname)
                    return
            return
        
        if action == "startup":
            pfn = gethome() + "/reboot_name.txt"
            if os.path.exists(pfn):
                os.remove(pfn)
                self.write ("Removed profile from system startup")
            else:
                self.write ("No startup file to remove")
        else:
            self.write ("Remove from startup must be the only option if selected")

        
class RestartHandler(BaseHandler):

    def get(self,path):
        
        expname = self.get_argument("expname", "???")
        fn = expname+".sh"
        
        if not os.path.exists(fn):
            self.write ("Could not find experiment profile %s" % expname)
            return
        
        pidfile = False
        pfn = gethome()+"/"+"experiment.pid"
        try:
            fp = open(pfn, "r")
            pidfile = True
        except:
            pass
        
        rv = 0
        if (pidfile != False):
            pid = fp.readline().strip("\n")
            fp.close()
            pid = int(pid)
            
            rv = 0
            try:
                rv = killit(pid)
                time.sleep(0.5)
            except:
                pass
            os.remove(pfn)
        
        if (rv != 0):
            self.write("Could not stop previous process %d\n" % pid)
            
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
        
        self.write ("Re-started experiment %s with pid %d\n" % (expname, pid))
        
        return
           

class LoginHandler(BaseHandler):
    def get(self):
        n = self.get_argument ("next", "/")
        loginpage = ('<html><body bgcolor="lightgrey"><form action="/login" method="post">'
        '<img  alt="ORION" src="/orion_logo.png" width="100" height="25">'
        '<hr>'
        '<h3>Radio Telescope Data System</h3>'
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
        # Create trimmed versions of pw
        #
        user = getluser()
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
        if (pw_struct.pw_uid < 1000):
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
            print "redirecting to %s" % self.get_argument("next")
            self.redirect(self.get_argument("next", u"/"))

def mkapp(cookie_secret):
    application = tornado.web.Application([
        (r"/index.html", TopLevelHandler),
        (r"/$", TopLevelHandler),
#       (r"/login", LoginHandler),
        (r"/(Documents)$", IndexHandler),
        (r"/(astro_data)$", IndexHandler),
        (r"/(.*\.png)", Handler, {'path' : gethome()}),
        (r"/astro_data/(.*)", Handler, {'path': gethome()+"/"+"astro_data"}),
        (r"/Documents/(.*)", Handler, {'path' : gethome()+"/"+"Documents"}),
        (r"/(real-time\.html)", Handler, {'path' : gethome()}),
        (r"/(syscontrol\.html)", SysControlHandler),
        (r"/(password\.html)", Handler, {'path' : gethome()}),
        (r"/(expcontrol\.html)", ExpControlHandler),
        (r"/(jquery.*\.js)", Handler, {'path' : gethome()}),
        (r"/(experiment.*\.json)", Handler, {'path' : gethome()}),
        (r"/(sysconfig\.json)", Handler, {'path' : gethome()}),
        (r"/(start\.html)", StartHandler),
        (r"/(stop\.html)", StopHandler),
        (r"/(restart\.html)", RestartHandler),
#       (r"/(pwchange\.html)", PwChangeHandler),
        (r"/(profiles\.html)", ProfileHandler),
        (r"/(sysupdate\.html)", SysUpdateHandler),
        (r"/(reboot\.html)", RebootHandler),
        (r"/(halt\.html)", HaltHandler)
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
    global USER
    
    HOMEDIR=os.path.realpath(".")
    pw_struct = pwd.getpwuid(os.getuid())
    USER = pw_struct.pw_name
    
    
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
    
      
    #
    # Because we may come up before all USB devices have
    #  reported in
    #
    usbtype = "Unknown"
    count = 0
    while usbtype == "Unknown" and count < 10:  
        p = subprocess.Popen("lsusb", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        outs = p.communicate()
        usblines = outs[0].split("\n")
        count += 1
        usbcount = 0
        for t in exp["usbtypes"]:
            for l in usblines:
                if t in l:
                    usbcount += 1
                    usbtype = exp["usbtypes"][t]
            if (usbcount > 0):
                break

        if (usbtype == "Unknown"):
            time.sleep(3)
    
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
