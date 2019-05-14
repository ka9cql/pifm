#!/usr/bin/env python
"""
Reads & Prints KISS frames from a TCP Socket.

"""

import aprs
import kiss
import re
import binascii
import subprocess
import sys


# The callsign the payload will respond to (can be overridden on command-line)
CALLSIGN="N0CALL"

def print_frame3(f):
    print("Raw Frame={}".format(f[1:]))

    pf = aprs.parse_frame(f)
    src = pf.source
    dst = pf.destination
    path = pf.path
    info = pf.info.data.decode('UTF-8')
    info = info.replace("\n"," ")
    info = info.replace("\r"," ")
    info = info.replace("\t"," ")

    print("Src:  [%s]" % src)
    print("Dst:  [%s]" % dst)
    print("Path: [%s]" % path)
    print("(PRE) Info: [%s]" % info)

    mf=""
    mt=""
    msg=""
    mid=""

    # FROM     }N0CALL-8>
    # PATH     >APRS,TCPIP,N6KMA*::
    # TO       ::N0CALL-11:
    # MESSAGE  (last-index-of):This is message 461 {
    # MSG_ID   {461$

    a=b=c=d=e=0

    try:
        a = info.index("}")
        b = info.index(">")
        c = info.index(":")+1
        d = info[c+1:].index(":")+c+1
        e = info.index("{")
    except:
        pass

    if d > 0:
        mf = info[a+1:b]
        mt = info[c+1:d]
        msg = info[d+1:e]
        mid = info[e+1:]


    print("\nINFO:      [%s]\n" % info)
    print("MSG-FROM   [%s]" % mf)
    print("MSG-TO     [%s]" % mt)
    print("MSG        [%s]" % msg)
    print("MSG_ID     [%s]" % mid)

    print("\n")



def process_frame(f):
    #print("Raw Frame={}".format(f[1:]))

    src=""
    dst=""
    path=""
    info=""

    try:
        pf = aprs.parse_frame(f)
        src = pf.source
        dst = pf.destination
        path = pf.path
        #info = pf.info 	# THIS IS AN OBJECT, NOT A STRING! >:{
        try:
            info = pf.info.data.decode('UTF-8')	# This is stringified object ;)
            info = info.replace("\n"," ")
            info = info.replace("\r"," ")
            info = info.replace("\t"," ")
        except:
            # In case we can't convert data
            info=""
            pass
    except:
        # In case frame can't be parsed
        pass

    #print("Src:  [%s]" % src)
    #print("Dst:  [%s]" % dst)
    #print("Path: [%s]" % path)
    #print("Info: [%s]" % info)

    print("Src:[%s]  Dst:[%s]  Path:[%s]  Info:[%s]" % (src,dst,path,info))

    # Start with frame from/to/info and message id of zero
    mf=src
    mt=dst
    msg=info
    mid="0"

    try:
        # First, try parsing the entire thing, just to ensure it's in the correct format
        # m1 = re.search(r'}.*>.*::.*:.*{.*', info) # This format REQUIRES a message ID
        m1 = re.search(r'}.*>.*::.*:.*', info)	    # This format DOES NOT require a message ID
        if m1:

            # Now try parsing each section
            m1 = re.search(r'}(.+?)>', info)
            if m1:
                mf = m1.group(1)

            m1 = re.search(r'::(.+?):', info)
            if m1:
                mt = m1.group(1)

            m1 = re.search(r':(.+?){', info)
            if m1:
                m2 = re.search(r':.*:(.+?)$',m1.group(1))
                if m2:
                    msg = m2.group(1)

            m1 = re.search(r'{(.+?)$', info)
            if m1:
                mid = m1.group(1)
    except:
        pass

    # print("MSG-FROM   [%s]" % mf)
    # print("MSG-TO     [%s]" % mt)
    # print("MSG        [%s]" % msg)
    # print("MSG_ID     [%s]" % mid)

    # The message might have <CR> in it, so print it last on the line
    print("MSG-FROM:[%s]  MSG-TO:[%s]  MSG_ID:[%s]  MSG:[%s]" % (mf,mt,mid,msg))

    print("")

    # If message is TO payload, ack it and send a response
    if not mid == "" and mt == CALLSIGN:
        #cmd = "(/usr/bin/nohup /home/direwolf/sendmsgack " +  mf + " " + mid + ")&"
        #print("DEBUG: CMD: [%s]\n" % cmd)
        subprocess.run(["/home/direwolf/ackmsg", mf, mid, msg])




def encode_callsign1(full_callsign):
    encoded_callsign = b''
    ssid = '0'

    if '-' in full_callsign:
        full_callsign, ssid = full_callsign.split('-')

    full_callsign = "%-6s" % full_callsign

    for char in full_callsign:
        encoded_char = ord(char) << 1
        encoded_callsign += bytes([encoded_char])

    encoded_ssid = (int(ssid) << 1) | 0x60
    encoded_callsign += bytes([encoded_ssid])

    return encoded_callsign


def decode_callsign(encoded_callsign):
    ##assert(len(encoded_callsign) == 7)
    callsign = ''
    # To determine the encoded SSID:
    # 1. Right-shift (or un-left-shift) the SSID bit [-1].
    # 2. mod15 the bit (max SSID of 15).
    #
    ssid = str((encoded_callsign[-1] >> 1) & 15) # aka 0x0F
    for char in encoded_callsign[:-1]:
        callsign += chr(char >> 1)
    if ssid == '0':
        return callsign.strip()
    else:
        return '-'.join([callsign.strip(), ssid])


def encode_callsign2(callsign):
    callsign = callsign.upper()
    ssid = '0'
    encoded_callsign = b''

    if '-' in callsign:
        callsign, ssid = callsign.split('-')

    if 10 <= int(ssid) <= 15:
        # We have to call ord() on ssid here because we're receiving ssid as
        # a str() not bytes().
        ssid = chr(ord(ssid[1]) + 10)
        # chr(int('15') + 10)

    ##assert(len(ssid) == 1)
    ##assert(len(callsign) <= 6)

    callsign = "{callsign:6s}{ssid}".format(callsign=callsign, ssid=ssid)

    for char in callsign:
        encoded_char = ord(char) << 1
        encoded_callsign += bytes([encoded_char])
    return encoded_callsign


def print_frame(frame):
    print(aprs.Frame(frame[1:]))

def main():

    # If a callsign was provided on the command-line, pick it up
    global CALLSIGN

    print("Default callsign: %s" % CALLSIGN)
    if len(sys.argv) > 1:
        CALLSIGN = sys.argv[1]
    print("Callsign: %s" % CALLSIGN)


    ki = kiss.TCPKISS(host='localhost', port=8001)
    ki.start()
    ki.read(callback=process_frame)




if __name__ == '__main__':
    main()
