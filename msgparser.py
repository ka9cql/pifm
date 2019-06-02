#!/usr/bin/env python
"""
Reads KISS frames from a TCP Socket, looks for APRS messages destined for the given
callsign (specify on command-line), and calls an external parse/ack/respond program
(ackmsg) if the callsigns match.

2019-05-21  msipin  Added timestamp to output lines (thanks Eric!)
                    Added space between "ID:" and numeric value for that ID.

"""

import aprs
import kiss
import re
import binascii
import subprocess
import sys
from datetime import datetime, timezone



# The callsign the payload will respond to (can be overridden on command-line)
CALLSIGN="N0CALL"

def print_frame3(f):
    print("Raw Frame={}".format(f[1:]))

    pf = aprs.parse_frame(f)
    src = pf.source.callsign.decode(encoding='UTF-8')
    dst = pf.destination.callsign.decode(encoding='UTF-8')
    path = pf.path
    info = pf.info.data.decode('UTF-8')
    info = info.replace("\n","")
    info = info.replace("\r","")
    info = info.replace("\t","")

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
    global CALLSIGN

    #print("Raw Frame={}".format(f[1:]))

    src=""
    dst=""
    path=""
    info=""

    try:
        pf = aprs.parse_frame(f)
        src = pf.source.callsign.decode(encoding='UTF-8')
        dst = pf.destination.callsign.decode(encoding='UTF-8')
        path = pf.path
        #info = pf.info 	# THIS IS AN OBJECT, NOT A STRING! >:{
        try:
            info = pf.info.data.decode('UTF-8')	# This is stringified object ;)
            info = info.replace("\n","")
            info = info.replace("\r","")
            info = info.replace("\t","")
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

    #print("Src:[%s]  Dst:[%s]  Path:[%s]  Info:[%s]" % (src,dst,path,info))

    # Start with frame from/to/info and message id of zero
    mf=src
    mt=dst
    msg=info
    mid="0"

    try:
        # First, try parsing the entire thing, just to ensure it's in the correct format
        # m1 = re.search(r'}.*>.*::.*:.*{.*', info) # This format REQUIRES a message ID
        m1 = re.search(r'}.*>.*::.*:.*', info)	    # This format DOES NOT require a message ID
        m2 = re.search(r':.*:.*', info)	    # This format DOES NOT require a message ID
        if m1:
            # Try parsing "from" using close-curly-brace format
            m1 = re.search(r'}(.+?)>', info)
            if m1:
                # Found close-curly-brace, so use this field as FROM
                mf = m1.group(1)
            else:
                # Didn't have close-curly-brace, so use PACKET SOURCE as FROM
                mf = src
        else:
            if m2:
                m3 = re.search(r':(.+?):', info)
                if m3:
                    mt = m3.group(1)

        if m1 or m2:
            m1 = re.search(r'::(.+?):', info)
            if m1:
                mt = m1.group(1)

            m1 = re.search(r':.*:(.+?){', info)
            if m1:
                msg = m1.group(1)
            else:
                m2 = re.search(r':.*:(.+?)$', info)
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
    if not mf == "" and not mt == "":
        # '2019-05-21 07:15:58'
        ahora = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        print("%s %-9s > %-9s ID: %3s  MSG[%s]" % (ahora,mf,mt,mid,msg), flush=True)

    # If message is TO payload, ack it and send a response
    if (not mid == "") and (mt == CALLSIGN):
        try:
            #print("DEBUG: Calling ackmsg...")
            subprocess.run(["/home/direwolf/ackmsg", mt, mf, mid, msg])
            #print("DEBUG: Back from calling ackmsg...")
        except:
            print("DEBUG: *EXCEPTION* while trying to call ackmsg!")
            pass

    #print("")



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
    global CALLSIGN

    print("Default callsign: %s" % CALLSIGN)

    # If a callsign was provided on the command-line, pick it up
    if len(sys.argv) > 1:
        CALLSIGN = sys.argv[1]
    print("Callsign: %s" % CALLSIGN)


    ki = kiss.TCPKISS(host='localhost', port=8001)
    ki.start()
    ki.read(callback=process_frame)




if __name__ == '__main__':
    main()
