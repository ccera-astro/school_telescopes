# this module will be imported in the into your flowgraph
import os
import ephem
import json
import math
import numpy
import time


then = time.time()

#
# Avoid the middle 4% of the FFT (DC offset) when calculating sum over bins
#
def fftsum(vec):
	l = len(vec)
	first = l/2 - int(l*0.02)
	second = l/2 + int(l*0.02)
	sum1  = numpy.sum(vec[0:first])
	sum1 += numpy.sum(vec[second:l])
	return sum1

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


def log(ffts,longitude,latitude,local,remote,expname,freq,bw,alpha,declination,speclog):
    global then
    global count
    global curr_diff
    global curr_sky
    global curr_ref
    global curr_corr_real
    global curr_corr_imag
    SKY = 0
    REF = 1
    CORR_REAL = 2
    CORR_IMAG = 3
    
    
    #
    # Protect against getting called too often
    #
    if ((time.time() - then) < 1.0):
        return False
    else:
        then = time.time()
    
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
        sfft = sffts[SKY]
    else:
        sfft = numpy.subtract(sffts[SKY], sffts[REF])
        sfft = numpy.absolute(sfft)
    
    #
    # Total power is the sum of the (possibly differenced) linear-form
    #   FFT magnitude output
    # I THINK THIS IS THE MOST NUMERICALLY-CORRECT APPROACH.  BUT I
    #   COULD BE WILDLY WRONG.
    #
    tpower = fftsum(sffts[SKY]) - fftsum(sffts[REF])
    
    #
    # Sky
    #
    skypower = fftsum(sffts[SKY])
    if (curr_sky < -50.0):
        curr_sky = skypower
    curr_sky = (alpha*skypower) + (beta*curr_sky)
    
    #
    # Ref
    #
    if (len(ffts) > 1):
        refpower = fftsum(sffts[REF])
        if (curr_ref < -50.0):
            curr_ref = refpower
        curr_ref = (alpha*refpower) + (beta*curr_ref)
    
    #
    # Correlation
    #
    if(len(ffts) > 1):
        corrpower_real = fftsum(sffts[CORR_REAL])
        corrpower_imag = fftsum(sffts[CORR_IMAG])
        if (curr_corr_real < -50.0):
            curr_corr_real = corrpower_real
            curr_corr_imag = corrpower_imag
        curr_corr_real = (alpha*corrpower_real) + (beta*curr_corr_real)
        curr_corr_imag = (alpha*corrpower_imag) + (beta*curr_corr_imag)
    
    #
    # Smooth total power estimate with single-pole IIR filter
    #
    #
    if (curr_diff < -50.0):
        curr_diff = tpower

    curr_diff = (alpha*tpower) + (beta*curr_diff)
    
    fft_labels = ["Diff", "Sky", "Ref", "Corr-Real", "Corr-Imag","Corr-Angle"]
    db_ffts = []
    lndx = 0
    corr_ffts = []
    for ufft in [sfft]+sffts:
        #
        # Scale into dB scale for logging
        #
        scaled_fft = numpy.add(ufft,[1.0e-15]*lfft)
        fftype = fft_labels[lndx]
        lndx = lndx+1
        if not ("Corr-" in fftype):
            scaled_fft = numpy.log10(scaled_fft)
            scaled_fft = numpy.multiply (scaled_fft, [10.0]*lfft)
        else:
            corr_ffts.append(scaled_fft)
        db_ffts.append(scaled_fft)

    re = corr_ffts[0]
    im = corr_ffts[1]
    cplx_corr = re +1j*im
    
    db_ffts.append(numpy.angle(cplx_corr))
        
    ltp = time.gmtime()
    sidt = cur_sidereal (longitude)
    
    dprefix = "%04d%02d%02d" % (ltp.tm_year, ltp.tm_mon, ltp.tm_mday)
    
    tfn = expname + "-" + dprefix + "-tp.csv"
  
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
    tlogbuf += "%e,%e,%e,%e,%e\n" % (curr_diff,curr_sky,curr_ref,curr_corr_real,curr_corr_imag)
    
    
    slogbufs = []
    lndx = 0
    for db_fft in db_ffts:
        #
        # Then spectral
        #
        slogbuf = "%02d,%02d,%02d," % (ltp.tm_hour, ltp.tm_min, ltp.tm_sec)
        slogbuf += "%s," % sidt
        slogbuf += "%9.4f," % (freq/1.0e6)
        slogbuf += "%5.2f," % declination
        slogbuf += "%5.2f," % (bw/1.0e6)

        #
        # Spectral data--possibly differenced
        fftype = fft_labels[lndx]
        lndx = lndx + 1
        for i in range(0,len(db_fft)):
            if not ("Corr-" in fftype):
                slogbuf += "%7.3f" % db_fft[i]
            else:
                slogbuf += "%e" % db_fft[i]
                
            if (i < len(sfft)-1):
                slogbuf += ","
        slogbuf += "\n"
        slogbufs.append(slogbuf)
    
       
    if (local != "" and local != None):
        if (os.path.exists(local)):
            if ((count % 5) == 0):
                tfp = open (os.path.join(local,tfn), "a")
                tfp.write (tlogbuf)
                tfp.close()
            
            if ((count % 45) == 0 and speclog != 0):
                l = 0
                for slogbuf in slogbufs:
                    sfn = expname + "-" + dprefix + "-" + fft_labels[l]
                    sfn += "-spec.csv"
                    sfp = open(os.path.join(local,sfn), "a")
                    sfp.write (slogbuf)
                    sfp.close()
                    swritten = True
                    l += 1
    
    if (remote != "" and remote != None):
        if (os.path.exists(remote)):          
            if ((count % 5) == 0):
                tfp = open (os.path.join(remote,tfn), "a")
                tfp.write (tlogbuf)
                tfp.close()
            
            if ((count % 45) == 0 and speclog != 0):
                l = 0
                for slogbuf in slogbufs:
                    sfn = expname + "-" + dprefix + "-" + fft_labels[l]
                    sfn = "-spec.csv"
                    sfp = open(os.path.join(remote,sfn), "a")
                    sfp.write (slogbuf)
                    sfp.close()
                    swritten = True
                    l += 1
    
    #
    # Handle json file for total power
    #
    ltp = time.gmtime()
    
    lupdate = "%04d%02d%02d-%02d:%02d:%02d" % (ltp.tm_year, ltp.tm_mon,
        ltp.tm_mday, ltp.tm_hour, ltp.tm_min, ltp.tm_sec)
    
    js = {"values" : [curr_diff,curr_sky,curr_ref,curr_corr_real,curr_corr_imag], "expname" : expname, "lmst" : sidt.replace(",", ":"), "dec" : declination,
        "latitude" : latitude, "longitude" : longitude, "updated" : lupdate, "labels" : ["Diff", "Sky", "Ref", "Corr-Real", "Corr-Imag"]}
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
    
    if ((count % 5) == 0):
        js = {"frequency" : freq, "bandwidth" : bw, "fftsize" : lfft,
            fft_labels[0] : list(db_ffts[0]),
            fft_labels[1] : list(db_ffts[1]),
            fft_labels[2] : list(db_ffts[2]),
            fft_labels[3] : list(db_ffts[3]),
            fft_labels[4] : list(db_ffts[4])}
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

            if (os.path.exists(tfn)):
                os.remove(tfn)
            
            for lbl in fft_labels:
                sfn = expname + "-" + dprefix + "-" + lbl + "-spec.csv"             
                if (os.path.exists(sfn)):
                    os.remove(sfn)
        
    count += 1
    return True
    
    
    
    
    
    
