#include <avr/io.h>
#include "tinysynth.inc"

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
; main

.global __do_copy_data ; durr, I don't have to write this myself
.global main
main:
	cli
	clr	ZERO

	; ----------------------------------------------------------------------------
	; io setup

	; output on PB4 (sound) and PB3 (command ready)
	ldi	temp, _BV(DDB4) | _BV(DDB3)
	out	IO(DDRB), temp

	; ----------------------------------------------------------------------------
	; pwm setup

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

	; ----------------------------------------------------------------------------
	; state setup

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
	ldi	xh, 0
	ldi	yh, 0
	ldi	zh, hi8(volume_table) ; same as hi8(sample_ram)... heh heh heh

	; ----------------------------------------------------------------------------
	; state/command processor setup
	rcall	copy_shadow
	rcall	cmd_setup

	; let's go!
	sei

.main_loop:
	sbic	sample_ready
	rjmp	.main_loop

	SIM_UPDATE_START

	; reset regs (5 cycles)
	ldi	xl, lo8(phases)
	ldi	yl, lo8(channels)
	ldi	temp, NUM_CHANNELS
	mov	I, temp
	clr	sample_buf
	clr	sample_buf+1
	lds	enabled, channel_enable

.update_loop:
	; skip to next channel if 0 (4 | 4)
	lsr	enabled
	brcs	.chan_enabled

	; skip over the remaining bytes
	adiw    xl, SIZEOF_PHASE
	adiw	yl, SIZEOF_CHANNEL
	rjmp	.loop_next

.chan_enabled:
	; add rate to phase (22 | 26)
	ld	rate, y+
	ld	phase, x
	add	phase, rate
	st	x+, phase
	ld	rate, y+
	ld	phase, x
	adc	phase, rate
	st	x+, phase
	bst	phase, 7 ; save the top bit (9-bit phase)
	ld	rate, y+
	ld	phase, x
	adc	phase, rate
	st	x+, phase

	; read len_mask, and with top byte of phase to give offset (same reg as phase) (3 | 29)
	ld	len_mask, y+
	and	offset,   len_mask

	; read start, add to offset, and that's the sample address (4 | 33)
	ld	start,  y+
	add	offset, start
	mov	zl,     offset

	; read sample (picking correct nybble using bit we saved earlier) (5 | 38)
	ld	zl, z
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