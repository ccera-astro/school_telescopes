#!/usr/bin/env python2
from lxml import etree
import json
import sys
import os

top = etree.parse(sys.stdin)
for element in top.iter("*"):
    if "trkpt" in element.tag:
        latitude =  float(element.get("lat"))
        longitude = float(element.get("lon"))
        dicto = {"latitude" : latitude, "longitude" : longitude}
        print json.dumps(dicto)+"\n"
        break
