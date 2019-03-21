#include <avr/io.h>

#include "tinysynth.inc"

.global cmd_setup
cmd_setup:
	;ldi	temp, _BV(USIWM0) | _BV(USICS1)
	;out	IO(USICR), temp
	ret