#include <avr/io.h>

#include "tinysynth.inc"

#if 0
#define SIM_UPDATE_START sbi	SIM_OUTPUT, 0
#define SIM_UPDATE_END   cbi	SIM_OUTPUT, 0
#else
#define SIM_UPDATE_START
#define SIM_UPDATE_END
#endif

; ----------------------------------------------------------------------------
; test data

.data
.org 0
.type   channels, @object
.size   channels, NUM_CHANNELS * SIZEOF_CHANNEL
channels:
	;     en    rat0  phs0  rat1  phs1  rat2  phs2  len   start vol   (unused for now)
	.byte 0x01, 0x00, 0x00, 0x80, 0x00, 0x00, 0x00, 0x1F, 0x00, 0x0F, 0, 0, 0, 0, 0, 0
	.byte 0x01, 0x00, 0x00, 0xC0, 0x00, 0x00, 0x00, 0x1F, 0x00, 0x0F, 0, 0, 0, 0, 0, 0
	.byte 0x01, 0x00, 0x00, 0x20, 0x00, 0x01, 0x00, 0x1F, 0x00, 0x0F, 0, 0, 0, 0, 0, 0
	.byte 0x01, 0x00, 0x00, 0x40, 0x00, 0x02, 0x00, 0x1F, 0x00, 0x0F, 0, 0, 0, 0, 0, 0
	.byte 0x01, 0x00, 0x00, 0x40, 0x00, 0x00, 0x00, 0x1F, 0x20, 0x0F, 0, 0, 0, 0, 0, 0
	.byte 0x01, 0x00, 0x00, 0x60, 0x00, 0x00, 0x00, 0x1F, 0x20, 0x0F, 0, 0, 0, 0, 0, 0
	.byte 0x01, 0x00, 0x00, 0x90, 0x00, 0x00, 0x00, 0x1F, 0x20, 0x0F, 0, 0, 0, 0, 0, 0
	.byte 0x01, 0x00, 0x00, 0x20, 0x00, 0x01, 0x00, 0x1F, 0x20, 0x0F, 0, 0, 0, 0, 0, 0

.org SAMPLE_RAM_START

.type	sample_ram, @object
.size	sample_ram, SAMPLE_RAM_SIZE
sample_ram:
	; sine
	.byte 0x88, 0x9A, 0xBB, 0xCD, 0xDE, 0xEF, 0xFF, 0xFF
	.byte 0xFF, 0xFF, 0xFF, 0xEE, 0xDD, 0xCB, 0xBA, 0x98
	.byte 0x87, 0x65, 0x44, 0x32, 0x21, 0x11, 0x00, 0x00
	.byte 0x00, 0x00, 0x01, 0x11, 0x22, 0x34, 0x45, 0x67

	; saw
	.byte 0x00, 0x00, 0x11, 0x11, 0x22, 0x22, 0x33, 0x33
	.byte 0x44, 0x44, 0x55, 0x55, 0x66, 0x66, 0x77, 0x77
	.byte 0x88, 0x88, 0x99, 0x99, 0xAA, 0xAA, 0xBB, 0xBB
	.byte 0xCC, 0xCC, 0xDD, 0xDD, 0xEE, 0xEE, 0xFF, 0xFF

	; tri
	.byte 0x00, 0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77
	.byte 0x88, 0x99, 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF
	.byte 0xFF, 0xEE, 0xDD, 0xCC, 0xBB, 0xAA, 0x99, 0x88
	.byte 0x77, 0x66, 0x55, 0x44, 0x33, 0x22, 0x11, 0x00

	; square
	.byte 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
	.byte 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
	.byte 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF
	.byte 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF

	.zero 128
.text

; ----------------------------------------------------------------------------
; timer1 overflow ISR - likely 10 cycles, 9 on underrun

.global	TIMER1_OVF_vect
TIMER1_OVF_vect:
	in	sreg_save, IO(SREG)

	; any sample ready?
	sbis	sample_ready
	rjmp	.no_sample

	; clear the flag and output the sample buffer
	cbi	sample_ready
	out	IO(OCR1B), sample_buf

.no_sample:
	out	IO(SREG), sreg_save
	reti

; ----------------------------------------------------------------------------
; io setup

io_setup:
	; output on PB4 (sound) and PB3 (command ready)
	ldi	temp, _BV(DDB4) | _BV(DDB3)
	out	IO(DDRB), temp
	ret

; ----------------------------------------------------------------------------
; pwm setup (kinda important, since it generates the sound output!)

pwm_setup:
	; Set compare unit values
	ldi	temp, 0
	out	IO(OCR1B), temp
	ldi	temp, 255
	out	IO(OCR1A), temp
	out	IO(OCR1C), temp

	; Enable PWM mode on timer 1
	ldi	temp, _BV(PWM1B) | _BV(COM1B1)
	out	IO(GTCCR), temp

	; Enable timer overflow interrupt
	in	temp, IO(TIMSK)
	ori	temp, _BV(TOIE1)
	out	IO(TIMSK), temp

	; Hardware bug requires COM1A0 to be enabled as well.
	; "2" means clock timer with CK/2 (32KHz sample rate)
	ldi	temp, _BV(PWM1A) | _BV(COM1A1) | _BV(COM1A0) | 3
	out	IO(TCCR1), temp
	ret

; ----------------------------------------------------------------------------
; main

.global __do_copy_data ; durr, I don't have to write this myself
.global main
main:
	cli
	clr	ZERO

	; setup IO
	rcall	io_setup
	rcall	pwm_setup
	rcall	cmd_setup

	; default mix is /8
	ldi	mix_shift, 3

	; initialize noise shift reg to 1
	clr	noise_lfsr
	clr	noise_lfsr+1
	inc	noise_lfsr
	clr	noise_reload

	; SHUSH
	ldi	temp, 0
	mov	noise_vol, temp

	; setup pointers
	ldi	xh, hi8(sample_ram)
	ldi	yh, 0
	ldi	zh, hi8(volume_table)

	; let's go!
	sei

.main_loop:
	sbic	sample_ready
	rjmp	.main_loop

	SIM_UPDATE_START

	; reset regs (5 cycles)
	ldi	yl, RAM_START
	ldi	temp, NUM_CHANNELS
	mov	I, temp
	clr	sample_buf
	clr	sample_buf+1

.update_loop:
	; read flags (enabled) and skip to next channel if 0 (4 | 4)
	ld	flags, y+
	tst	flags
	brne	.chan_enabled

	; skip over the remaining bytes
	adiw	yl, DISABLED_CHANNEL_SKIP
	rjmp	.loop_next

.chan_enabled:
	; add rate to phase (22 | 26)
	ld	rate, y+
	ld	phase, y
	add	phase, rate
	st	y+, phase
	ld	rate, y+
	ld	phase, y
	adc	phase, rate
	st	y+, phase
	bst	phase, 7 ; save the top bit (9-bit phase)
	ld	rate, y+
	ld	phase, y
	adc	phase, rate
	st	y+, phase

	; read len_mask, and with top byte of phase to give offset (same reg as phase) (3 | 29)
	ld	len_mask, y+
	and	offset,   len_mask

	; read start, add to offset, and that's the sample address (4 | 33)
	ld	start,  y+
	add	offset, start
	mov	xl,     offset

	; read sample (picking correct nybble using bit we saved earlier) (5 | 38)
	ld	zl, x
	brts	1f
	swap	zl
1:	andi	zl, 0xF

	; read volume and get scaled sample from volume table (7 | 45)
	ld	volume, y+
	swap	volume
	or	zl, volume
	lpm	sample, z

	; accumulate (2 | 47)
	add	sample_buf, sample
	adc	sample_buf+1, ZERO

	; neeeext (1 | 48)
	adiw	yl, ENABLED_CHANNEL_SKIP

.loop_next:
	; decrement counter, loop if not 0 (3 | 51)
	dec	I
	brne	.update_loop

	; at this point, the loop has taken (51 x 4 - 1 + 5) = 412 cycles.

	; might seem silly to always update the noise channel, but we're optimizing for fastest
	; worst-case cycle times, and the additional check for disabled adds a few cycles.

	; need to update LFSR? (2/3, added to if/else branches below)
	tst	noise_ctr
	breq	.noise_update

	; update counter (7+2 = 9)
	dec	noise_ctr
	bst	noise_lfsr, 0
	clr	sample
	brtc	.noise_output
	mov	sample, noise_vol
	rjmp	.noise_output

.noise_update:
	; update LFSR (10+3 = 13)
	mov	noise_ctr, noise_reload
	mov	sample, noise_lfsr
	lsr	noise_lfsr+1
	ror	noise_lfsr
	eor	sample, noise_lfsr

	bst	sample, 0
	clr	sample
	brtc	.noise_output
	mov	sample, noise_vol
	bld	noise_lfsr+1, 6

.noise_output:
	; output noise sample (13 from above + 5 here = 18 | 430)
	mov	volume, sample
	swap	volume
	or	sample, volume
	add	sample_buf, sample
	adc	sample_buf+1, ZERO

	; shift sample (cycles needed: 8 for 0, 9 for all others) (9 | 439)
	cpi	mix_shift, 3
	breq	3f
	cpi	mix_shift, 2
	breq	2f
	cpi	mix_shift, 1
	breq	1f
	rjmp	0f
3:	lsr	sample_buf+1
	ror	sample_buf
2:	lsr	sample_buf+1
	ror	sample_buf
1:	lsr	sample_buf+1
	ror	sample_buf

	; tell the ISR it's ready (2 | 441)
0:	SIM_UPDATE_END
	sbi	sample_ready

	; look for commands! (2/3 | 443/444)
	sbrc	cmd_state, CMD_STATE_READY_BIT
	rcall	cmd_process

	; loop (2 | 445/446)
	rjmp	.main_loop