# this module will be imported in the into your flowgraph
import os
import ephem
import json
import math
import numpy
import time


then = time.time()

def cur_sidereal(longitude):
    longstr = "%02d" % int(longitude)
    longstr = longstr + ":"
    longitude = abs(longitude)
    frac = longitude - int(longitude)
    frac *= 60
    mins = int(frac)
    longstr += "%02d" % mins
    longstr += ":00"
    x = ephem.Observer()
    x.date = ephem.now()
    x.long = longstr
    jdate = ephem.julian_date(x)
    tokens=str(x.sidereal_time()).split(":")
    hours=int(tokens[0])
    minutes=int(tokens[1])
    seconds=int(float(tokens[2]))
    sidt = "%02d,%02d,%02d" % (hours, minutes, seconds)
    return (sidt)
    
count = 0
def log(fft,longitude,latitude,local,remote,expname,freq,bw):
    global then
    global count
    
    #first shift the fft output
    lfft = len(fft)
    newfft = fft[lfft/2:lfft]
    newfft += fft[0:lfft/2]
    
    #
    # Scale by FFT size
    #
    newfft = numpy.divide (newfft, [lfft]*lfft)
    
    tpower = numpy.sum(newfft)
    
    newfft = numpy.add(newfft,[1.0e-10]*lfft)
    newfft = numpy.log10(newfft)
    newfft = numpy.multiply (newfft, [10.0]*lfft)
    
    ltp = time.gmtime()
    sidt = cur_sidereal (longitude)
    
    dprefix = "%04d%02d%02d" % (ltp.tm_year, ltp.tm_mon, ltp.tm_mday)
    
    tfn = expname + "-" + dprefix + "-tp.csv"
    sfn = expname + "-" + dprefix + "-spec.csv"
    
    #
    #
    # PLACEHOLDER!!!!!!
    #
    #
    declination = latitude

    # Form the buffer we're going to log to files
    #

    tlogbuf = "%02d,%02d,%02d," % (ltp.tm_hour, ltp.tm_min, ltp.tm_sec)
    tlogbuf += "%s," % sidt
    tlogbuf += "%9.4f," % (freq/1.0e6)
    tlogbuf += "%5.2f," % declination
    tlogbuf += "%e\n" % tpower
    
    
    slogbuf = "%02d,%02d,%02d," % (ltp.tm_hour, ltp.tm_min, ltp.tm_sec)
    slogbuf += "%s," % sidt
    slogbuf += "%9.4f," % (freq/1.0e6)
    slogbuf += "%5.2f," % declination
    for i in range(0,len(newfft)):
        slogbuf += "%5.2f" % newfft[i]
        if (i < len(newfft)-1):
            slogbuf += ","
    slogbuf += "\n"
       
    now = time.time()
    swritten = False
    if (local != "" and local != None):
        if (os.path.exists(local)):
            tfp = open (os.path.join(local,tfn), "a")
            tfp.write (tlogbuf)
            tfp.close()
            
            if (now-then >= 30):
                sfp = open(os.path.join(local,sfn), "a")
                sfp.write (slogbuf)
                sfp.close()
                swritten = True
    
    if (remote != "" and remote != None):
        if (os.path.exists(remote)):
            tfp = open (os.path.join(remote,tfn), "a")
            tfp.write (tlogbuf)
            tfp.close()
            
            if (now-then >= 30):
                sfp = open(os.path.join(remote,sfn), "a")
                sfp.write (slogbuf)
                sfp.close()
                swritten = True
    
    if (swritten == True):
        then = now
            
    #
    # Handle json file for total power
    #
    ltp = time.gmtime()
    
    lupdate = "%04d%02d%02d-%02d:%02d:%02d" % (ltp.tm_year, ltp.tm_mon,
        ltp.tm_mday, ltp.tm_hour, ltp.tm_min, ltp.tm_sec)
    
    js = {"value" : tpower, "expname" : expname, "lmst" : sidt.replace(",", ":"), "dec" : declination,
        "latitude" : latitude, "longitude" : longitude, "updated" : lupdate}
    jstring = json.dumps(js, indent=4)
    
    try:
        jfp = open(os.path.join(local,"tpower.json"), "w")
        jfp.write(jstring+"\n")
        jfp.close()
    except:
        pass
    
    
    #
    # Handle json file for spectral
    #
    
    if ((count % 2) == 0):
        js = {"values" : list(newfft), "frequency" : freq, "bandwidth" : bw, "fftsize" : lfft}
        jstring = json.dumps(js, indent=4)
        
        try:
            jfp = open(os.path.join(local,"spectral.json"), "w")
            jfp.write(jstring+"\n")
            jfp.close()
        except:
            pass
    
    
    
    #
    #
    # Handle old data
    #
    DAY=86400
    WEEK=7
    
    #
    # Roughly once a minute, handle old-data removal
    #
    if ((count % 30) == 0):
        ltp = time.gmtime((time.time()-DAY*WEEK))
        dprefix = "%04d%02d%02d" % (ltp.tm_year, ltp.tm_mon, ltp.tm_mday)
        
        tfn = expname + "-" + dprefix + "-tp.csv"
        sfn = expname + "-" + dprefix + "-spec.csv"
        if (os.path.exists(tfn)):
            os.remove(tfn)
        if (os.path.exists(sfn)):
            os.remove(sfn)
        
    count += 1
    return True
    
    
    
    
    
    
