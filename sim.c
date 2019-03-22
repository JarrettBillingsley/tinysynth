#include <avr/io.h>
#include <avr/interrupt.h>
#include "avr_mcu_section.h"

AVR_MCU(F_CPU, "attiny85");

AVR_MCU_VCD_IRQ(TIMER1_OVF)

const struct avr_mmcu_vcd_trace_t _mytrace[]  _MMCU_ = {
    { AVR_MCU_VCD_SYMBOL("OUT"), .mask = (1 << PB0), .what = (void*)&PORTB, },
    { AVR_MCU_VCD_SYMBOL("UPD"), .mask = (1 << PB1), .what = (void*)&PORTB, },
    { AVR_MCU_VCD_SYMBOL("PB2"), .mask = (1 << PB2), .what = (void*)&PORTB, },
    { AVR_MCU_VCD_SYMBOL("PB3"), .mask = (1 << PB3), .what = (void*)&PORTB, },
    { AVR_MCU_VCD_SYMBOL("PB4"), .mask = (1 << PB4), .what = (void*)&PORTB, },
    { AVR_MCU_VCD_SYMBOL("OCR1B"), .what = (void*)&OCR1B, },
};