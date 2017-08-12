; this code is based on the usi_i2c_slave.c driver written by Adam Honse:
; https://github.com/CalcProgrammer1/Stepper-Motor-Controller/blob/master/UnipolarStepperDriver/usi_i2c_slave.c

#include <avr/io.h>

#include "tinysynth.inc"

.global cmd_setup
cmd_setup:
	ldi	temp, _BV(USIWM0) | _BV(USICS1)
	out	IO(USICR), temp
	ret

.global spi_send
spi_send:
	out IO(USIDR), temp
	ldi temp, (1<<USIWM0)|(0<<USICS0)|(1<<USITC)
	ldi i2c_state, (1<<USIWM0)|(0<<USICS0)|(1<<USITC)|(1<<USICLK)
	out IO(USICR), temp ; MSB
	out IO(USICR), i2c_state
	out IO(USICR), temp
	out IO(USICR), i2c_state
	out IO(USICR), temp
	out IO(USICR), i2c_state
	out IO(USICR), temp
	out IO(USICR), i2c_state
	out IO(USICR), temp
	out IO(USICR), i2c_state
	out IO(USICR), temp
	out IO(USICR), i2c_state
	out IO(USICR), temp
	out IO(USICR), i2c_state
	out IO(USICR), temp ; LSB
	out IO(USICR), i2c_state
	in temp, IO(USIDR)
	ret

;------------------------------------------------------------------------------------------------
;------------------------------------------------------------------------------------------------
;------------------------------------------------------------------------------------------------
;------------------------------------------------------------------------------------------------

#if 0
#define PORTB_SDA PB0
#define PORTB_SCL PB2
#define PIN_SDA   PINB0
#define PIN_SCL   PINB2

#define STATE_CHECK_ADDRESS       0
#define STATE_SEND_DATA           1
#define STATE_SEND_DATA_ACK_WAIT  2
#define STATE_SEND_DATA_ACK_CHECK 3
#define STATE_RECV_DATA_WAIT      4
#define STATE_RECV_DATA_ACK_SEND  5

#define USISR_COUNT_ACK      0b01110000 | (0x0E << USICNT0)
#define USISR_COUNT_BYTE     0b01110000 | (0x00 << USICNT0)
#define USISR_CLEAR_START    0b11110000 | (0x00 << USICNT0)
#define USISR_SET_START_COND 0b01110000 | (0x00 << USICNT0)
#define USICR_SET_START_COND 0b10101000
#define USICR_STOP_DID_OCCUR 0b10111000
#define USICR_STOP_NOT_OCCUR 0b11101000

.macro SET_SDA_OUTPUT
	sbi	IO(DDRB), PORTB_SDA
.endm

.macro SET_SDA_INPUT
	cbi	IO(DDRB), PORTB_SDA
.endm

.macro SET_SCL_OUTPUT
	sbi	IO(DDRB), PORTB_SCL
.endm

.macro SET_SCL_INPUT
	cbi	IO(DDRB), PORTB_SCL
.endm

.macro SET_BOTH_OUTPUT
	SET_SCL_OUTPUT
	SET_SDA_OUTPUT
.endm

.macro SET_BOTH_INPUT
	SET_SCL_INPUT
	SET_SDA_INPUT
.endm

.globl i2c_setup
i2c_setup:
	in	temp, IO(PORTB)
	andi	temp, ~(_BV(PORTB_SCL) | _BV(PORTB_SDA))
	out	IO(PORTB), temp

	SET_BOTH_INPUT

	ldi	temp, USICR_SET_START_COND
	out	IO(USICR), temp

	ldi	temp, USISR_CLEAR_START
	out	IO(USISR), temp

	ret

.global USI_START_vect
USI_START_vect:
	in	sreg_save, IO(SREG)

	ldi	i2c_state, STATE_CHECK_ADDRESS
	SET_SDA_INPUT

0:	sbis	IO(PINB), PIN_SCL
	rjmp	1f
	sbic	IO(PINB), PIN_SDA
	rjmp	1f
	rjmp	0b

1:	ldi	temp, USICR_STOP_DID_OCCUR
	sbis	IO(PINB), PIN_SDA
	ldi	temp, USICR_STOP_NOT_OCCUR
	out	IO(USICR), temp

	ldi	temp, USISR_CLEAR_START
	out	IO(USISR), temp

	out	IO(SREG), sreg_save
	reti

#endif