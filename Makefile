DEVICE     = attiny85            # See avr-help for all possible devices
CLOCK      = 16500000            # 16.5Mhz
OBJECTS    = synth.o cmd.o sim.o # Add more objects for each .c file here

UPLOAD = ./micronucleus --run
COMPILE = avr-gcc -Wall -Werror -O -g -DF_CPU=$(CLOCK) -mmcu=$(DEVICE)
ASSEMBLE = avr-as --fatal-warnings -mmcu=$(DEVICE)
SIMULATE = ~/src/simavr/simavr/obj-x86_64-apple-darwin18.0.0/run_avr.elf

all:    synth.hex

synth.o: synth.s tinysynth.inc
	$(COMPILE) -x assembler-with-cpp -c synth.s -o synth.o

cmd.o: cmd.s tinysynth.inc
	$(COMPILE) -x assembler-with-cpp -c cmd.s -o cmd.o

sim.o: sim.c
	$(COMPILE) -c sim.c -o sim.o

flash: all
	$(UPLOAD) synth.hex

simulate: all
	$(SIMULATE) -i cmd_test_5.vcd -v -v -v -v -v -v synth.elf

clean:
	rm -f synth.hex synth.elf $(OBJECTS)

synth.elf: $(OBJECTS)
	$(COMPILE) -o synth.elf $(OBJECTS)

synth.hex: synth.elf
	rm -f synth.hex
	avr-objcopy -j .text -j .data -O ihex synth.elf synth.hex
	avr-size --format=avr --mcu=$(DEVICE) synth.elf