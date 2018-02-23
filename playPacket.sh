#!/bin/sh
##########
# playPacket.sh - Play packet wav files over the radio on a Pi Zero W
##########

# 44100 hz stereo (NOTE: divided sampling rate by two!)
#SAMP_RATE=22050
#FORMAT="stereo"

# 44100 hz mono
SAMP_RATE=44100
FORMAT="mono"

# Frequency in Megahertz (Mhz)
#   E.G. 144.390 = Mhz FM (+/- a little offset...?)
#FREQ=144.39415		# EVER, EVER, ever so slightly low...
FREQ=144.394157		# Seems (visually on waterfall) properly centered
#FREQ=144.390		# Did *NOT* get decoded on direwolf...
#FREQ=102.3


# 44100 hz sample rate, 16-bit files -
#  packet.16bit.wav

# NOTE: FOR NOW - DO NOT - raise the volume above 4!
VOLUME=4


echo

#for FREQ in 144.394 102.3
#do
    for A in `ls packet*.wav`
    do
	echo "Playing file  ${A} on ${FREQ} Mhz..."
	cmd=`echo pifm $A ${FREQ} ${SAMP_RATE} ${FORMAT} ${VOLUME}`
	echo "Command Line: [$cmd]"
	$cmd
#	sleep 2
    done
#done

echo

exit 0

