
######################
# makePacket.sh - Create the audio output file for an APRS position report
######################

AUDIO_FILE="packet.Loc.wav"

# Your callsign (MANDATORY!)
CALLSIGN="KA9CQL-2"

# Time in Zulu, format: ddhhmm
TIME_Z="072256"

# Latitude, format: hhmm.ssN (or  hhmm.ssS)
LAT="3429.57N"

# Longitude, format: hhh.mmssssss.00W (or hhh.mmssssss.00E)
LON="117.40867600.00W"

# Altitude in feet ASL, format: nnnnnn
ALT="003285"

# Course (heading), in degrees format: ddd
HDG="090"

# Speed in MPH, format: sss
SPD="001"

# Message, freeform: "This is a message"
MSG="WarPig-II Position report"


rm -f $AUDIO_FILE


## USING APRS (can't yet get or build it for Pi Zero...) -
## aprs -c ${CALLSIGN} -o AUDIO_FILE "/${TIME_Z}z${LAT}/${LON}>${HDG}/${SPD}${MSG}/A=${ALT}"


## Using direwolf -
## NOTE: MUST HAVE direwolf.conf FILE SET UP WITH YOUR CALL, etc.!!!
########
##gen_packets -o packet.Loc.wav -r 44100 aprs.dat
gen_packets -o packet.Loc.wav -r 44100 aprs.dat


# Test the result to see if it worked -
echo
echo "Testing encoding..."
atest packet.Loc.wav
echo


# Reset the screen (direwolf insists on changing its fg/bg colors!)
#tput reset

exit 0

Usage: gen_packets [options] [file]
Options:
  -a <number>   Signal amplitude in range of 0 - 200%.  Default 50.
  -b <number>   Bits / second for data.  Default is 1200.
  -B <number>   Bits / second for data.  Proper modem selected for 300, 1200, 2400, 4800, 9600.
  -g            Scrambled baseband rather than AFSK.
  -m <number>   Mark frequency.  Default is 1200.
  -s <number>   Space frequency.  Default is 2200.
  -r <number>   Audio sample Rate.  Default is 44100.
  -n <number>   Generate specified number of frames with increasing noise.
  -o <file>     Send output to .wav file.
  -8            8 bit audio rather than 16.
  -2            2 channels (stereo) audio rather than one channel.

An optional file may be specified to provide messages other than
the default built-in message. The format should correspond to
the standard packet monitoring representation such as,

    WB2OSZ-1>APDW12,WIDE2-2:!4237.14NS07120.83W#

Example:  gen_packets -o x.wav 

    With all defaults, a built-in test message is generated
    with standard Bell 202 tones used for packet radio on ordinary
    VHF FM transceivers.

Example:  gen_packets -o x.wav -g -b 9600
Shortcut: gen_packets -o x.wav -B 9600

    9600 baud mode.

Example:  gen_packets -o x.wav -m 1600 -s 1800 -b 300
Shortcut: gen_packets -o x.wav -B 300

    200 Hz shift, 300 baud, suitable for HF SSB transceiver.

Example:  echo -n "WB2OSZ>WORLD:Hello, world!" | gen_packets -a 25 -o x.wav -

    Read message from stdin and put quarter volume sound into the file x.wav.

