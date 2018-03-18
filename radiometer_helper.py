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
curr_det = -99.00
def log(ffts,longitude,latitude,local,remote,expname,freq,bw,alpha,declination):
    global then
    global count
    global curr_det
    
    #
    # Protect against getting called too often
    #
    if ((time.time() - then) < 1.0):
        return False
    else:
        then = time.now()
    
    beta = 1.0-alpha
    
    sums = []
    sffts = []
    for fft in ffts:
        
        #first shift the fft output
        lfft = len(fft)
        newfft = fft[lfft/2:lfft]
        newfft += fft[0:lfft/2]
        
        #
        # Scale by FFT size
        #
        newfft = numpy.divide (newfft, [lfft]*lfft)
        sffts.append(newfft)
    
    #
    # Handle differencing of the two FFT arrays
    #
    if (len(ffts) == 1):
        sfft = sffts[0]
    else:
        sfft = numpy.subtract(sffts[0], sffts[1])
    
    #
    # Total power is the sum of the (possibly differenced) linear-form
    #   FFT magnitude output
    # I THINK THIS IS THE MOST NUMERICALLY-CORRECT APPROACH.  BUT I
    #   COULD BE WILDLY WRONG.
    #
    tpower = numpy.sum(sfft)
    
    #
    # Smooth total power estimate with single-pole IIR filter
    #
    #
    if (curr_det < -50.0):
        curr_det = tpower

    curr_det = (alpha*tpower) + (beta*curr_det)
    
    #
    # Scale into dB scale for logging
    #
    sfft = numpy.add(sfft,[1.0e-15]*lfft)
    sfft = numpy.log10(sfft)
    sfft = numpy.multiply (sfft, [10.0]*lfft)
        
   
    ltp = time.gmtime()
    sidt = cur_sidereal (longitude)
    
    dprefix = "%04d%02d%02d" % (ltp.tm_year, ltp.tm_mon, ltp.tm_mday)
    
    tfn = expname + "-" + dprefix + "-tp.csv"
    sfn = expname + "-" + dprefix + "-spec.csv"
  
    #
    # Form the buffer we're going to log to files
    #
    
    #
    # Total (or differential) power first
    #
    tlogbuf = "%02d,%02d,%02d," % (ltp.tm_hour, ltp.tm_min, ltp.tm_sec)
    tlogbuf += "%s," % sidt
    tlogbuf += "%9.4f," % (freq/1.0e6)
    tlogbuf += "%5.2f," % declination
    tlogbuf += "%e\n" % curr_det
    
    
    #
    # Then spectral
    #
    slogbuf = "%02d,%02d,%02d," % (ltp.tm_hour, ltp.tm_min, ltp.tm_sec)
    slogbuf += "%s," % sidt
    slogbuf += "%9.4f," % (freq/1.0e6)
    slogbuf += "%5.2f," % declination

    #
    # Spectral data--possibly differenced
    #
    for i in range(0,len(sfft)):
        slogbuf += "%5.2f" % sfft[i]
        if (i < len(sfft)-1):
            slogbuf += ","
    slogbuf += "\n"
       
    if (local != "" and local != None):
        if (os.path.exists(local)):
            if ((count % 5) == 0):
                tfp = open (os.path.join(local,tfn), "a")
                tfp.write (tlogbuf)
                tfp.close()
            
            if ((count % 30) == 0):
                sfp = open(os.path.join(local,sfn), "a")
                sfp.write (slogbuf)
                sfp.close()
                swritten = True
    
    if (remote != "" and remote != None):
        if (os.path.exists(remote)):          
            if ((count % 5) == 0):
                tfp = open (os.path.join(remote,tfn), "a")
                tfp.write (tlogbuf)
                tfp.close()
            
            if ((count % 30) == 0):
                sfp = open(os.path.join(remote,sfn), "a")
                sfp.write (slogbuf)
                sfp.close()
                swritten = True
    
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
        js = {"values" : list(sfft), "frequency" : freq, "bandwidth" : bw, "fftsize" : lfft}
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
    if ((count % 60) == 0):
        start = int(time.time()) - ((DAY*WEEK)*2)
        for tday in range(start,start+(DAY*WEEK),DAY):
            ltp = time.gmtime(tday)
            dprefix = "%04d%02d%02d" % (ltp.tm_year, ltp.tm_mon, ltp.tm_mday)
            tfn = expname + "-" + dprefix + "-tp.csv"
            sfn = expname + "-" + dprefix + "-spec.csv"
            if (os.path.exists(tfn)):
                os.remove(tfn)
            if (os.path.exists(sfn)):
                os.remove(sfn)
        
    count += 1
    return True
    
    
    
    
    
    
