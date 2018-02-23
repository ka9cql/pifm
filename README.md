```diff
- Note: this project has been revived so that a Raspberry Pi Zero W can be used to natively send ham radio APRS packets, with no external transmitter!
```

## Turning the Raspberry Pi Zero W Into an APRS Transmitter

### Steps to play mono sound file:

*(Created by Oliver Mattos and Oskar Weigl. Code is GPL)*

```
sudo python
>>> import PiFm
>>> PiFm.play_sound("sound.wav")
```

Now connect a 19.2-inch (19-and-3/16 inch) piece of plain wire to GPIO 4 (which is pin 7 on [the Pi Zero W header](https://cdn.sparkfun.com/assets/learn_tutorials/6/7/6/PiZero_1.pdf)) to act as an antenna, and tune a 2-meter FM ham radio to 144.390Mhz

from a [post on MAKE](http://blog.makezine.com/2012/12/10/raspberry-pi-as-an-fm-transmitter/?parent=Electronics) by Matt Richardson

The sound file can be 16 bit mono or stereo wav format.

### Play a stereo file:

```
sudo ./pifm left_right.wav 144.390 22050 stereo

# Example command lines
# play an MP3
ffmpeg -i input.mp3 -f s16le -ar 22.05k -ac 1 - | sudo ./pifm -

# Broadcast from a usb microphone (see arecord manual page for config)
arecord -d0 -c2 -f S16_LE -r 22050 -twav -D copy | sudo ./pifm -
```

### How to change the broadcast frequency

Run the ./pifm binary with no command line arguments to find usage.

The second command line argument is the frequency to transmit on, as a number in Mhz. Eg. This will transmit on 144.390 Mhz

> sudo ./pifm sound.wav 144.390

It will work from about 1Mhz up to 250Mhz, although the 2-meter ham radio band in the USA is 144.0 Mhz to 146.0 Mhz

### The details of how it works

The code was hacked together over a few hours at the [Code Club pihack](http://blog.codeclub.org.uk/blog/brief/). It uses the hardware on the raspberry pi that is actually meant to generate spread-spectrum clock signals on the GPIO pins to output FM Radio energy. This means that all you need to do to turn the Raspberry-Pi into a (ridiculously powerful) FM Transmitter is to plug in a wire as the antenna (as little as 20cm will do) into GPIO pin 4 and run the code posted below. It transmits on 144.390 MHz.

When testing, the signal only started to break up after we went through several conference rooms with heavy walls, at least 50m away, and crouched behind a heavy metal cabinet. The sound quality is ok, but not amazing, as it currently plays some clicks when the CPU gets switched away to do anything else than play the music. We made a kernel mode driver that used the DMA controller to offload the CPU and play smooth music without loading the CPU. DMA from userspace is awesome and awful at the same time!


### Accessing Hardware

The python library calls a C program. The C program maps the Peripheral Bus (0x20000000) in physical memory into virtual address space using /dev/mem and mmap. To do this it needs root access, hence the sudo. Next it sets the clock generator module to enabled and sets it to output on GPIO4 (no other accessible pins can be used). It also sets the frequency to 103.3, which provides a carrier. At this point, radios will stop making a "fuzz" noise, and become silent.

Modulation is done by adjusting the frequency using the fractional divider between 103.325Mhz and 103.275Mhz, which makes the audio signal. The fractional divider can get full 16 bit quality sound, and it even does FM pre-emphasis so that the result doesn't sound bass-heavy. 

### Notes

This is a copy of the original material from 
http://www.icrobotics.co.uk/wiki/index.php/Turning_the_Raspberry_Pi_Into_an_FM_Transmitter, 

The changes here have been made in order to adapt this project for both the Pi Zero W, and for transmitting APRS on United States 2 meter ham radio frequencies.

NOTE: YOU CAN NOT USE THIS CODE UNLESS YOU ARE A LICENSED AMATEUR RADIO OPERATOR with operating privileges in the US 2 meter ham radio band.  PERIOD!

All rights of the original authors reserved.

### References

* http://www.icrobotics.co.uk/wiki/index.php/Turning_the_Raspberry_Pi_Into_an_FM_Transmitter

* http://blog.makezine.com/2012/12/10/raspberry-pi-as-an-fm-transmitter/?parent=Electronics

* http://www.youtube.com/v/ekcdAX53-S8#! 

* https://github.com/richardghirst/PiBits/pull/18
