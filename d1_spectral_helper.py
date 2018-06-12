# this module will be imported in the into your flowgraph
import os
import ephem
import json
import math
import numpy
import time

#
# Get current sidereal time
#
# Only required input for our purposes is longitude
#
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
curr_diff = -99.00
curr_sky = -99.00
curr_ref = -99.00
curr_corr_real = -99.00
curr_corr_imag = -99.00

then = time.time()
avgd_ffts = []
def log(ffts,longitude,latitude,local,freq,bw,alpha,declination,expname):
    global then
    global count
    global avgd_ffts
    
    #
    # We write data every INTERVAL seconds
    #
    INTERVAL = 600
    
    #
    # Rate at which we take incoming new data into the averager
    #
    RATE = 2
    

    #
    # Protect against getting called too often
    #
    if ((time.time() - then) < RATE):
        return False
    else:
        then = time.time()

    sffts = []
    lfft = len(ffts[0])
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
    # Check for "fresh" avgd_ffts
    #
    if len(avgd_ffts) < len(sffts):
        for ff in sffts:
            avgd_ffts.append(ff)
    
    beta = 1.0-alpha
    stime = cur_sidereal(longitude)
    #
    # We apply an averaging filter here using a single-pole-IIR filter
    #
    for ind in range(0,len(avgd_ffts)):
        t1 = numpy.multiply(sffts[ind],[alpha]*lfft)
        t2 = numpy.multiply(avgd_ffts[ind],[beta]*lfft)
        avgd_ffts[ind] = numpy.add(t1,t2)
        #
        # Time to write out FFT data?
        #
        if ((count % (INTERVAL/RATE)) == 0 and os.path.exists(local)):
            #
            # Might as well log in this loop, too
            #
            ltp = time.gmtime()
            fn = "%s-%04d%02d%02d-spec%d.csv" % (expname, ltp.tm_year, ltp.tm_mon, ltp.tm_mday, ind)
            f = open(os.path.join(local,fn),"a")
            f.write("%02d,%02d,%02d," % (ltp.tm_hour, ltp.tm_min, ltp.tm_sec))
            f.write(stime+",")
            f.write("%f," % (freq/1.0e6))
            f.write("%f," % declination)
            f.write("%f," % (bw/1.0e6))
            for p in avgd_ffts[ind]:
                f.write("%e," % p)
            f.write("\n")
            f.close()

    count += 1
    
    #
    # Calculate total-power
    #
    tp1 = numpy.sum(avgd_ffts[0])
    tp2 = numpy.sum(avgd_ffts[1])
    tp3 = numpy.sum(avgd_ffts[2])
       
    #
    # Handle json file for total power
    #
    ltp = time.gmtime()
    
    lupdate = "%04d%02d%02d-%02d:%02d:%02d" % (ltp.tm_year, ltp.tm_mon,
        ltp.tm_mday, ltp.tm_hour, ltp.tm_min, ltp.tm_sec)
    
    js = {"values" : [tp1, tp2, tp3, 0.0, 0.0], "expname" : expname, "lmst" : stime.replace(",", ":"), "dec" : declination,
        "latitude" : latitude, "longitude" : longitude, "updated" : lupdate, "labels" : ["Sky1", "Sky2", "Sky3", "Inval-0", "Inval-1"]}
    jstring = json.dumps(js, indent=4)
    
    try:
        jfp = open(os.path.join(local,"tpower_temp"), "w")
        jfp.write(jstring+"\n")
        jfp.close()
        src = os.path.join(local,"tpower_temp")
        dst = os.path.join(local,"tpower.json")
        os.rename(src,dst)
    except:
        pass
    
    #
    # Handle json file for spectral
    #
    fft_labels = ["Sky1", "Sky2", "Sky3"]
    db_ffts = []
    for i in range(0,len(avgd_ffts)):
        dbt = numpy.add(avgd_ffts[i],[1.0e-15]*lfft)
        dbt = numpy.log10(dbt)
        dbt = numpy.multiply(dbt,[10.0]*lfft)
        db_ffts.append(dbt)
        
    js = {"frequency" : freq, "bandwidth" : bw, "fftsize" : lfft,
        fft_labels[0] : list(db_ffts[0]),
        fft_labels[1] : list(db_ffts[1]),
        fft_labels[2] : list(db_ffts[2])}
    jstring = json.dumps(js, indent=4)
    
    
        
    try:
        jfp = open(os.path.join(local,"spectral_temp"), "w")
        jfp.write(jstring+"\n")
        jfp.close()
        src = os.path.join(local,"spectral_temp")
        dst = os.path.join(local,"spectral.json")
        os.rename(src, dst)
    except:
        pass
    
    return True
    
    
    
    
    
    
