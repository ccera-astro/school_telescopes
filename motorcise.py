#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  motorcise.py
#  
#  Copyright 2018 Marcus D. Leech <mleech@localhost.localdomain>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
import serial
import os
import time
import sys

def main():
	
	serh = serial.Serial(sys.argv[1], 38400, timeout=0)
	serh.write("GO\r");
	serh.read(100);
	count = 0
	while True:
		serh.write("F30%\r")
		serh.read(100)
		
		time.sleep(5.0)
		serh.write("B20\r")
		serh.read(100)
		
		time.sleep(1.0)
		serh.write("R30%\r")
		serh.read(100)
		
		time.sleep(5.0)
		serh.write("B20\r")
		serh.read(100)
		
		count = count + 1
		print "Count %d" % count
		
		time.sleep(1.0)
	
	return 0

if __name__ == '__main__':
	main()

