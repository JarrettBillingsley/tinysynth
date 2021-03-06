#include <avr/io.h>

#include "tinysynth.inc"

; ----------------------------------------------------------------------------
; USI overflow vector

.global	USI_OVF_vect
USI_OVF_vect:
	; acknowledge interrupt and input SREG (+3 = 3)
	in	sreg_save2, IO(SREG)
	sbi	IO(USISR), USIOIF

	; re-enable interrupts so that a nested timer interrupt can happen (+1 = 4)
	sei

	; all paths are (+8 = 12)
	sbrc	cmd_state, CMD_STATE_WAIT_OP_BIT
	in	cmd_op, IO(USIBR)              ; got op
	sbrc	cmd_state, CMD_STATE_WAIT_ARG1_BIT
	in	cmd_arg1, IO(USIBR)            ; got arg1
	sbrc	cmd_state, CMD_STATE_WAIT_ARG2_BIT
	in	cmd_arg2, IO(USIBR)            ; got arg2
	sbrc	cmd_state, CMD_STATE_WAIT_ARG3_BIT
	in	cmd_arg3, IO(USIBR)            ; got arg3

	; (+1 = 13)
	; note: if we were in CMD_STATE_READY, this enters an invalid state
	; but we're assuming the host will play nice.
	lsl	cmd_state

	; (+2/3 = 15/16)
	sbrc	cmd_state, CMD_STATE_READY_BIT
	cbi	cmd_ready

	; (+5 = 20/21)
	out	IO(SREG), sreg_save2
	reti

; ----------------------------------------------------------------------------
; pin change vector (for sync)
; not likely to happen often, so let's not worry about it interrupting other stuff

.global	PCINT0_vect
PCINT0_vect:
	in	sreg_save, IO(SREG)

	; don't fuck up a command that's in progress
	sbic	cmd_ready
	ldi	cmd_state, CMD_STATE_WAIT_OP

	; but reset the USI regs regardless
	out	IO(USIDR), ZERO
	out	IO(USISR), ZERO

	out	IO(SREG), sreg_save
	reti

; ----------------------------------------------------------------------------
; setup

.global cmd_setup
cmd_setup:
	; USIOIE == 1 (enable counter overflow interrupt)
	; USIWM == 01 (three-wire/SPI mode)
	; USICS == 10 (external clock; register clocked on positive edge)
	ldi	temp, _BV(USIOIE) | _BV(USIWM0) | _BV(USICS1)
	out	IO(USICR), temp

	; set up state machine
	ldi	cmd_state, CMD_STATE_WAIT_OP
	out	IO(USIDR), ZERO
	out	IO(USISR), ZERO ; clear USI counter too

	; turn on pin change interrupt for PB1 (sync signal)
	ldi	temp, _BV(PCINT1)
	out	IO(PCMSK), temp
	ldi	temp, _BV(PCIE)
	out	IO(GIMSK), temp

	; tell host we are ready to accept commands
	sbi	cmd_ready
	ret

; ----------------------------------------------------------------------------
; command processing

.global cmd_process
cmd_process:
	; using z for indirect jump in this function
	push	zh

	; dispatch based on the top bit
	sbrc	cmd_op, 7
	rjmp	.channel_cmds    ; top bit set, must be channel command

	; must be a global command; let's dispatch
	ldi	zh, pm_hi8(.global_cmd_jumptable)
	ldi	zl, pm_lo8(.global_cmd_jumptable)
	add	zl, cmd_op
	adc	zl, ZERO
	ijmp
.global_cmd_jumptable:
	rjmp	.cmd_silence
	rjmp	.cmd_commit
	rjmp	.cmd_mix_shift
	rjmp	.cmd_noise_vol
	rjmp	.cmd_noise_reload
	rjmp	.cmd_sample_1
	rjmp	.cmd_sample_2
	rjmp	.cmd_channel_enable

.cmd_silence:
	; silence all channels
	sts	shadow_enable, ZERO
	sts	shadow_noise_vol, ZERO
	sts	channel_enable, ZERO
	clr	noise_vol
	rjmp	.finish_command

.cmd_commit:
	; commit changes made to shadow state into the real state
	rcall	copy_shadow
	rjmp	.finish_command

.cmd_mix_shift:
	; set mix shift
	andi	cmd_arg1, 3
	sts	shadow_mix_shift, cmd_arg1
	rjmp	.finish_command

.cmd_noise_vol:
	; set noise volume
	andi	cmd_arg1, 15
	sts	shadow_noise_vol, cmd_arg1
	rjmp	.finish_command

.cmd_noise_reload:
	; set noise reload
	sts	shadow_noise_reload, cmd_arg1
	rjmp	.finish_command

.cmd_sample_1:
	; store 1 sample
	mov	xl, cmd_arg1
	st	x, cmd_arg2
	rjmp	.finish_command

.cmd_sample_2:
	; store 2 samples
	mov	xl, cmd_arg1
	st	x+, cmd_arg2
	st	x, cmd_arg3
	rjmp	.finish_command

.cmd_channel_enable:
	; set enabled channels mask
	sts	shadow_enable, cmd_arg1
	rjmp	.finish_command

	;---------------------------------------------------------
.channel_cmds:
	; separate channel number (in upper nybble) from command (lower nybble)
	mov	temp, cmd_op
	andi	temp, 0x70
	andi	cmd_op, 0xF

	; compute channel base addresses
	swap	temp     ; temp = ch
	mov	I, temp  ; stash channel number away in I
	mov	xl, temp ; xl = ch
	lsl	temp     ; temp = 2ch
	add	xl, temp ; xl = ch + 2ch = 3ch
	mov	yl, temp ; yl = 2ch
	lsl	temp     ; temp = 4ch
	add	yl, temp ; yl = 2ch + 4ch = 6ch
	ldi	temp, lo8(shadow_channels)
	add	yl, temp
	ldi	temp, lo8(shadow_phases)
	add	xl, temp

	; let's dispatch
	ldi	zh, pm_hi8(.channel_cmd_jumptable)
	ldi	zl, pm_lo8(.channel_cmd_jumptable)
	add	zl, cmd_op
	adc	zl, ZERO
	ijmp
.channel_cmd_jumptable:
	rjmp	.channel_rate
	rjmp	.channel_phase
	rjmp	.channel_rate_reset
	rjmp	.channel_sample
	rjmp	.channel_vol

.channel_rate:
	; set rate
	st	y+, cmd_arg1
	st	y+, cmd_arg2
	st	y+, cmd_arg3
	rjmp	.finish_command

.channel_phase:
	; set phase
	st	x+, cmd_arg1
	st	x+, cmd_arg2
	st	x+, cmd_arg3
	rjmp	.mark_phase_dirty

.channel_rate_reset:
	; set rate and reset phase
	st	y+, cmd_arg1
	st	y+, cmd_arg2
	st	y+, cmd_arg3
	st	x+, ZERO
	st	x+, ZERO
	st	x+, ZERO

.mark_phase_dirty:
	; this seems a little cycle-wasteful, but it doesn't matter --
	; these commands are eclipsed by the commit command.
	ldi	temp, 1
	rjmp	1f
0:	lsl	temp
	dec	I
1:	tst	I
	brne	0b

	; temp now contains 1 << channel num
	lds	I, shadow_phase_update
	or	I, temp
	sts	shadow_phase_update, I

	out	SIM_OUTPUT, ZERO
	out	SIM_OUTPUT, I
	rjmp	.finish_command

.channel_sample:
	; set sample
	subi	yl, -3 ;add 3
	st	y+, cmd_arg2 ; len
	st	y+, cmd_arg1 ; start
	rjmp	.finish_command

.channel_vol:
	; set volume
	subi	yl, -5; add 5
	andi	cmd_arg1, 0xF
	st	y, cmd_arg1
	rjmp	.finish_command

.finish_command:
	; reset state machine and tell host we're accepting commands
	ldi	cmd_state, CMD_STATE_WAIT_OP
	sbi	cmd_ready
	pop	zh
	ret

; ----------------------------------------------------------------------------
; shadow data copying
; we've got TONSA FLASH so whatever, let's unroll these loops!

.global copy_shadow
copy_shadow:
	SIM_SHADOW_START

	; setup pointers (+2 = 2)
	ldi	xl, lo8(channels)
	ldi	yl, lo8(shadow_channels)

	; unrolled loop (+192 = 194)
.rept NUM_CHANNELS * SIZEOF_CHANNEL
	ld	temp, y+
	st	x+, temp
.endr

	; other vars (+10 = 204)
	lds	temp, shadow_enable
	sts	channel_enable, temp
	lds	noise_vol, shadow_noise_vol
	lds	noise_reload, shadow_noise_reload
	lds	mix_shift, shadow_mix_shift

	; phase updating time! (+4 = 208)
	lds	I, shadow_phase_update
	sts	shadow_phase_update, ZERO

.rept NUM_CHANNELS
	; this channel need updating? (+2 = 2)
	lsr	I
	brcs	1f

	; nah, skip (+6 = 8)
	adiw	xl, 3
	adiw	yl, 3
	rjmp	2f

1:	; yeah, copy (+1+12 = 15)
	ld	temp, y+
	st	x+, temp
	ld	temp, y+
	st	x+, temp
	ld	temp, y+
	st	x+, temp
2:
.endr
	SIM_SHADOW_END

	; phase update can take up to 120 cycles; return (208+120+4 = 332)
	ret