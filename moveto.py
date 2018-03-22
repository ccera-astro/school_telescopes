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

serh.write("GO\r")
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
    
alpha=0.2
beta=1.0-alpha
avgangs=[-90000.0]*len(devs)
wait=10
then=time.time()
count = 0
done=False
current_rate=None
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
        lastang = avgangs[0]
        
        if ((count % 5) == 0):
            print "Serial: %d angle %f" % (sernums[dind], avgangs[dind])
        now = time.time()
        if (now-then >= 5):
            count += 1
            if ((count % 30) == 0):
                if (abs(lastang-avgangs[0]) < 0.15):
                    print "No apparent motion!"
                    serh.write("B25\r")
                    serh.read(100)
                    done=True
                    break
                else:
                    lastang = avgangs[0]
                    
            if (count > (600)):
                print "Timed out waiting for motion to complete"
                serh.write("B25\r");
                serh.read(100)
                done=True
                break
            foo = desired - avgangs[0]
            if (abs(foo) > 5):
                desired_rate = "50%"
            elif (abs(foo) > 0.5):
                desired_rate = "25%"
            else:
				desired_rate = "12%"
            if (abs(foo) > 0.1):
                if (foo < 0):
                    if (current_rate != desired_rate):
                        serh.write("F"+desired_rate+"\r")
                        print "Rate change to F%s" % desired_rate
                        junk = serh.read(100)
                        current_rate = desired_rate
                else:
                    if (current_rate != desired_rate):
                        serh.write("R"+desired_rate+"\r")
                        print "Rate change to R%s" % desired_rate
                        junk = serh.read(100)
                        current_rate = desired_rate
            else:
                serh.write("B25\r")
                done=True
                break
                
        time.sleep(0.1)
        
