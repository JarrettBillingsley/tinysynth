DEVICE     = attiny85
CLOCK      = 16000000            # 16 Mhz
OBJECTS    = synth.o cmd.o sim.o voltab.o

UPLOAD = ./micronucleus --run
COMPILE = avr-gcc -Wall -Werror -O -g -DF_CPU=$(CLOCK) -mmcu=$(DEVICE)
ASSEMBLE = $(COMPILE) -x assembler-with-cpp
SIMULATE = ~/src/simavr/simavr/obj-x86_64-apple-darwin18.5.0/run_avr.elf

all: synth.hex

synth.o: synth.s tinysynth.inc
	$(ASSEMBLE) -c synth.s -o $@

cmd.o: cmd.s tinysynth.inc
	$(ASSEMBLE) -c cmd.s -o $@

voltab.o: voltab.s tinysynth.inc
	$(ASSEMBLE) -c voltab.s -o $@

sim.o: sim.c
	$(COMPILE) -c sim.c -o $@

synth.elf: $(OBJECTS)
	$(COMPILE) -Wl,-Tscript.ld,--undefined=_mmcu,--section-start=.mmcu=0x910000 -o $@ $(OBJECTS)

synth.hex: synth.elf
	rm -f synth.hex
	avr-objcopy -j .text -j .data -O ihex synth.elf synth.hex
	avr-size --format=avr --mcu=$(DEVICE) synth.elf

flash: all
	$(UPLOAD) synth.hex

arduflash: all
	avrdude -v -pattiny85 -carduino -P$$(/bin/ls /dev/cu.usbmodem*) -b19200 -Uflash:w:synth.hex:i

simulate: synth.elf
	$(SIMULATE) -v -v -v -v -v -v synth.elf

clean:
	rm -f synth.hex synth.elf $(OBJECTS)

