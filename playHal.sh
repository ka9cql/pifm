#!/bin/sh
##########
# playHal.sh - Play Hal 9000 wav files over the FM radio on a Pi Zero W
##########

# 11025 hz stereo divided by two
SAMP_RATE=5512

# Frequency in Megahertz (Mhz)
#   E.G. 107.1 = Mhz FM
#FREQ=107.1
FREQ=102.3

# 1102 hz sample rate, stereo, 16-bit files -
#  Hal.AllSystemsFunctional.16bit.wav
#  Hal.CompletelyOperational.16bit.wav

echo

for A in `ls sounds/Hal*.wav`
do
	echo "Playing file  ${A} on ${FREQ} Mhz..."
	pifm $A ${FREQ} ${SAMP_RATE} stereo
done

echo

exit 0

