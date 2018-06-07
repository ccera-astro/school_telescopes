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
def log(ffts,longitude,latitude,local,freq,bw,alpha,declination):
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
    RATE = 10
    

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
            fn = "%04d%02d%02d-spec%d.csv" % (ltp.tm_year, ltp.tm_mon, ltp.tm_mday, ind)
            f = open(os.path.join(local,fn),"a")
            stime = cur_sidereal(longitude)
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
    return True
    
    
    
    
    
    
