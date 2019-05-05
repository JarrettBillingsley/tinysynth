#include <avr/io.h>
#include <avr/interrupt.h>
#include "avr_mcu_section.h"

AVR_MCU(F_CPU, "attiny85");

AVR_MCU_VCD_FILE("traces/gtkwave_trace.vcd", 1000);

AVR_MCU_VCD_IRQ(USI_OVF)
AVR_MCU_VCD_IRQ(TIMER1_OVF)
AVR_MCU_VCD_IRQ(PCINT0)
// AVR_MCU_SIMAVR_CONSOLE(&GPIOR0);

FUSES = {
	.low = 0xE1,
	.high = 0xDF,
	.extended = EFUSE_DEFAULT,
};

const struct avr_mmcu_vcd_trace_t _mytrace[]  _MMCU_ = {
	{ AVR_MCU_VCD_SYMBOL("PB0/MOSI"),  .what = (void*)&PORTB, .mask = (1 << PB0), },
	{ AVR_MCU_VCD_SYMBOL("PB2/SCLK"),  .what = (void*)&PORTB, .mask = (1 << PB2), },
	{ AVR_MCU_VCD_SYMBOL("PB1/SYNC"),  .what = (void*)&PORTB, .mask = (1 << PB1), },
	{ AVR_MCU_VCD_SYMBOL("PB3/READY"), .what = (void*)&PORTB, .mask = (1 << PB3), },
	{ AVR_MCU_VCD_SYMBOL("PB4/OUT"),   .what = (void*)&PORTB, .mask = (1 << PB4), },
	{ AVR_MCU_VCD_SYMBOL("OCR1B"),     .what = (void*)&OCR1B, },
	{ AVR_MCU_VCD_SYMBOL("GPIOR0"),    .what = (void*)&GPIOR0, },
};