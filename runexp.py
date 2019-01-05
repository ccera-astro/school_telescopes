#!/usr/bin/env python2
import json
import subprocess
import os
import sys
import time


def float_vert(v):
    try:
        x = float(v)
    except:
        return ("BAD")
    return x

def varsub(x,vl):
    for v in vl:
        x = x.replace("@@"+v, str(vl[v]))
    return x

def runner(experiments, sysconfig, profile, writer):

        me = sysconfig["hwtype"]
        commands = experiments["commands"]
        hlist = experiments["hwtypes"]
        if (me not in hlist):
            writer("Internal error -- hwtype %s not in database" % me)
            return
        
        varlist = {}
        
        hwtype = hlist[me]
        frange = hwtype["freqs"]
        slist = hwtype["rates"]
        grange = hwtype["rfgains"]
        
        freq = profile["freq"]
        varlist["freq"] = profile["freq"]
        
        srate = profile["srate"]
        varlist["srate"] = srate
        varlist["abw"] = (srate*0.90)*1.0e6
        
        
        varlist["alpha"] = profile["alpha"]
        varlist["longitude"] = profile["longitude"]
        
        varlist["latitude"] = profile["latitude"]
        
        varlist["rfgain"] = profile["rfgain"]
        
        varlist["declination"] = profile["declination"]
        
        varlist["rmount"] = profile["rmount"]
        varlist["ruser"] = profile["ruser"]
        varlist["rpassword"] = profile["rpassword"]
        varlist["expname"] = profile["expname"]
        varlist["excl"] = profile["excl"]

        if (varlist["excl"] == ""):
            varlist["excl"] = "none"
        
        specbool = int(profile["speclog"])
        varlist["speclog"] = profile["speclog"]
        
        
        for key in hwtype:
            if (type(hwtype[key]) is not list):
                varlist[key] = hwtype[key]
        
        etypes = ["radiometer", "fast", "d1", "pulsar"]
        etype = profile["etype"]
        if (etype not in etypes):
            writer ("Experiment type %s is unknown" % etype)
            return
        
        key = etype
        if (key not in hwtype):
            writer ("Experiment type %s is not supported by this hardware" % key)
            return

        softconfig = hwtype[key]
  
        rv = 0
        try:
            f = open ("experiment.pid", "r")
            l = f.readline().strip('\n')
            f.close()
            if (killit(int(l)) == -1):
                writer ("Failed to kill previous process: %d\n" % int(l))
            time.sleep(1.0)
        except:
            pass
            
        cmdstr = ""
        saved_commands = ""
        for x in commands[softconfig]:
            cmdstr = ""
            cls = experiments[x]
            for l in cls:
                cmdstr = cmdstr + varsub(l,varlist) + " "
              
            p = subprocess.Popen (cmdstr, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            outs = p.communicate()
            r = p.wait()
            if (r != 0):
                writer ("Process failed to start correctly")
                writer (outs[0])
                writer (outs[1])
            
            saved_commands += cmdstr
            saved_commands += "\n"
            
        f = open ("experiment.pid", "r")
        pid = int(f.readline().strip('\n'))
        f.close()
        writer ("Experiment %s started with PID %d\n<br>" % (varlist["expname"], pid))
        return

if __name__ == '__main__':

    fp = open(sys.argv[1]+".json", "r")
    profile = json.load(fp)
    fp.close()
    
    fp = open("experiments.json", "r")
    experiments = json.load(fp)
    fp.close()
    
    fp = open("sysconfig.json", "r")
    sysconfig = json.load(fp)
    fp.close()
    
    runner(experiments, sysconfig, profile, sys.stdout.write)


