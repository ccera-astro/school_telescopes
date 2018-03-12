#!/usr/bin/env python2
import hidraw
import hid
import os
import struct
import time
import serial
import math
import sys

dlist = hid.enumerate(0x0461, 0x0021)
devs = []
for dv in dlist:
    d = hidraw.device()
    d.open_path(dv["path"])
    devs.append(d)

buf=bytearray(64)

sernums = []
serh = serial.Serial (sys.argv[1], 38400, timeout=0)
serh.write("C,0,0,0,0\r")
serh.write("O,0,0,0\r")
junk=serh.read(100)
latitude=float(sys.argv[3])
desired=float(sys.argv[2]) + (90.0-latitude)
print "Desired elevation is %f for declination %f" % (desired, float(sys.argv[2]))
for d in devs:
    buf[0] = 0x00
    buf[1] = 0x00
    buf[2] = 0x01
    
    b = bytearray(4)
    
    d.write(buf)
    x = d.read(6)
    for i in range(0,len(b)):
        b[i] = x[i+2]
    ser = struct.unpack(">i", b)
    sernums.append(ser[0])
    
alpha=0.1
beta=1.0-alpha
avgangs=[-90000.0]*len(devs)
wait=10
then=time.time()
count = 0
done=False
while done==False:
    for dind in range(0,len(devs)):
        buf[0] = 0x00
        buf[1] = 0x00
        buf[2] = 0x05
        
        b = bytearray(4)
        devs[dind].write(buf)
        x = devs[dind].read(6)
        for i in range(0,len(b)):
            b[i] = x[i+2]
        
        angle = struct.unpack(">i", b)
        ang = float(angle[0])
        ang = ang/1000.0
        
        if (avgangs[dind] < -1000):
            avgangs[dind] = ang
        
        avgangs[dind] = (ang*alpha) + (avgangs[dind]*beta)
        
        print "Serial: %d angle %f" % (sernums[dind], avgangs[dind])
        now = time.time()
        if (now-then >= 5):
            count += 1
            if (count > (15*4)):
                print "Timed out waiting for motion"
                serh.write("O,0,0,0\r");
                serh.read(100)
                done=True
                break
            foo = avgangs[0] - desired
            if (abs(foo) > 0.2):
                if (foo < 0):
                    serh.write("PO,A,4,0\r")
                    serh.write("PO,A,5,1\r")
                    junk = serh.read(100);
                else:
                    serh.write("PO\,A,5,0\r")
                    serh.write("PO,A,4,1\r")
                    junk = serh.read(100)
            else:
                serh.write("PO,A,4,0\r")
                serh.write("PO,A,5,0\r")
                serh.write("O,0,0,0\r")
                done=True
                break
                
        time.sleep(0.25)
        
