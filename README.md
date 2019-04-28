# TinySynth

Ever wanted a very small wavetable synthesizer that you can control over SPI? No? Well TOO BAD, I MADE ONE.

## Idea

A small, grindy-sounding wavetable synth (much like the Namco N163) implemented entirely in software on an ATTiny85!

I'm developing it on a [Digispark](http://digistump.com/products/1) clone, but it should work fine on any ATTiny85, hardware revision C or newer.

## Specs

- **8 channels of wavetable goodness,** each with:
	- 24-bit frequency range
	- 16 linear volume levels
	- sample start at any byte boundary in sample RAM
	- sample length can be any power of 2 from 2 to 512
- **1 noise channel**
	- 8-bit frequency range
	- 16 linear volume levels
- **256 bytes of 4-bit-per-sample sample RAM**
	- 512 samples total
	- you better get creative!
- **Mixer master volume control**
	- no division, divide by 2, divide by 4, or divide by 8
	- keeps 8-bit output in range
		- ...or, crank the volume for fun distortion effects when using multiple channels!
- **16KHz PWM output**
	- combine with an RC low-pass filter (schematic below) for a headphone-level signal!
- **Controlled over SPI bus**
	- sort of... only MISO and SCK
	- plus a READY signal from synth to host
	- and a SYNC signal for... well... uh..........

## Circuit schematic

```
  ATTiny85
-------------
|VCC     PB0|-\
|GND     PB1|-| serial interface (TBD)       10uF
|        PB2|-|                       +-------|(------ to headphone jack
|        PB3|-/       1K              v      +
|RST     PB4|-------/\/\/\---+------/\/\/\-+
-------------                |       10K   |
                 0.22uF(224) =             |
                 (film cap)  |             |
                             V             V
```

The **resistor and capacitor on PB4** form a low-pass RC filter to convert the PWM output into a varying voltage. I uh, just kinda played around with values until it sounded nice. Maybe the cap value is too high! We'll see! I recommend a film capacitor due to its (pretty) flat frequency response.

The **10K potentiometer** is a volume knob. Pick a log or audio taper if you have one, but a linear one is probably fine too.

The **10uF electrolytic** is on the output because, uh... I think it's there to remove the DC component from the output signal but maybe it's doing something else in addition to/instead of that. I just see it a lot on headphone/speaker circuit diagrams!

The output is mono, so the output jack left and right channels **should be tied together.**

## Compiling

I'm developing this with the **AVR-GCC toolchain.** It works on both Linux and macOS for sure. I think the assembly syntax, at least the directives, differ from Atmel's official assembler, so it probably can't be compiled with that.

## Fuses

**This program requires a high speed clock, which requires programming the fuses to non-factory-default values.** If you are using a Digispark or clone, your fuses are probably already set to the right values unless you changed them.

If you turned PB5 into an IO pin instead of a reset pin, you'll have to use high-voltage programming to reprogram the fuses. [Here is a good guide for that](http://www.rickety.us/2010/03/arduino-avr-high-voltage-serial-programmer/).

### EFUSE

The extended fuse (EFUSE) value does not matter; it has no effect on the operation of the synth.

### HFUSE

The high fuse (HFUSE) should be programmed to the factory default value of `0xDF`.

- Programming it to `0x5F` as is typical for *real* Digisparks turns PB5 into another IO pin instead of a reset pin. This should be fine for now, but the reset pin might be useful in the future, so I'd say stick with `0xDF` like on the clones instead.

### LFUSE

Instead of the default value of `0x62`, the low fuse (LFUSE) should be programmed to `0xE1`:

- Setting the high bit to 1 disables the "divide system clock by 8" feature.
- Setting `CKSEL` to `0001` enables the high-frequency 64MHz internal PLL, which is then divided by 4 to yield a 16MHz system clock.

**If you use the default LFUSE value of `0x62`, the output pitch will be much lower than it should be, and it'll probably mess with communications too.**

## Flashing

The makefile uses micronucleus to flash the program to the MCU, since I'm developing it on a Digispark clone which uses "fake" USB to make flashing it easier. But you can flash the resulting `synth.hex` however you like - using an "arduino ISP" for example if you're using a "bare" ATTiny85.

## Testing

**If you are using a Digispark or clone, you must remove the programming cable after flashing.** It's awkward, but it's because pins PB3 and PB4 are used for the "software USB." PB3 is used as part of the serial communication protocol, and PB4 is the sound output. If the Digispark is still connected to your computer's USB port after flashing, the computer will be confusedly sending data down these wires, asking if your synth is a USB device, which will cause malfunctions and messed-up audio.