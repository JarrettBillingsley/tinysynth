DEVICE     = attiny85
CLOCK      = 16000000            # 16 Mhz
OBJECTS    = build/synth.o build/cmd.o build/sim.o build/voltab.o build/data.o
OBJ        = build/

COMPILE = avr-gcc -Wall -Werror -O -g -DF_CPU=$(CLOCK) -mmcu=$(DEVICE)
ASSEMBLE = $(COMPILE) -x assembler-with-cpp
SIMULATE = ~/src/simavr/simavr/obj-x86_64-apple-darwin18.5.0/run_avr.elf

all: $(OBJ)synth.hex

src/voltab.s: script/volgen.py
	python3 $< > $@

$(OBJ)%.o: src/%.s src/tinysynth.inc
	$(ASSEMBLE) -c $< -o $@

$(OBJ)sim.o: src/sim.c
	$(COMPILE) -c $< -o $@

$(OBJ)synth.elf: $(OBJECTS)
	$(COMPILE) -Wl,-Tsrc/script.ld,--undefined=_mmcu,--section-start=.mmcu=0x910000 -o $@ $(OBJECTS)

$(OBJ)synth.hex: $(OBJ)synth.elf
	rm -f $(OBJ)synth.hex
	avr-objcopy -j .text -j .data -O ihex $(OBJ)synth.elf $(OBJ)synth.hex
	avr-size --format=avr --mcu=$(DEVICE) $(OBJ)synth.elf

flash: all
	avrdude -v -pattiny85 -carduino -P$$(/bin/ls /dev/cu.usbmodem*) -b115200 -Uflash:w:$(OBJ)synth.hex:i

simulate: $(OBJ)synth.elf
	$(SIMULATE) -i traces/phase_test.vcd -v -v -v -v -v -v $(OBJ)synth.elf

clean:
	rm -f $(OBJ)synth.hex $(OBJ)synth.elf src/voltab.s $(OBJECTS)

