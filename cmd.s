#include <avr/io.h>

#include "tinysynth.inc"

; ----------------------------------------------------------------------------
; USI overflow vector

; receiving full 4-byte command 19 + 19 + 19 + 20 = 77 cyc
; update loop takes 239, so 316 cyc; leaves ~180 cyc for command processing (STILL so ROOMY)

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
	; using z for indirect jump in this function (+2 = 2)
	push	zh

	; dispatch based on the top bits
	sbrc	cmd_op, 7
	rjmp	.sample_ram_cmds ; top bit set, must be sample ram command
	sbrc	cmd_op, 6
	rjmp	.channel_cmds    ; second from top bit set, must be channel command

	; got here, (+4 = 6)
	; must be a global command; let's dispatch (+8 = 10)
	ldi	zh, pm_hi8(.global_cmd_jumptable) ; z = global_cmd_jumptable + 2*cmd_op
	ldi	zl, pm_lo8(.global_cmd_jumptable)
	add	zl, cmd_op
	adc	zl, ZERO
	ijmp
.global_cmd_jumptable:
	rjmp	.cmd_silence
	rjmp	.cmd_mix_shift
	rjmp	.cmd_noise_vol
	rjmp	.cmd_noise_reload

.cmd_silence:
	; silence all channels (+11 = 21)
	sts	(RAM_START + (0 * SIZEOF_CHANNEL)), ZERO
	sts	(RAM_START + (1 * SIZEOF_CHANNEL)), ZERO
	sts	(RAM_START + (2 * SIZEOF_CHANNEL)), ZERO
	sts	(RAM_START + (3 * SIZEOF_CHANNEL)), ZERO
	clr	noise_vol
	rjmp	.finish_command

.cmd_mix_shift:
	; set mix shift (+4 = 14)
	andi	cmd_arg1, 3
	mov	mix_shift, cmd_arg1
	rjmp	.finish_command

.cmd_noise_vol:
	; set noise volume (+4 = 14)
	andi	cmd_arg1, 15
	mov	noise_vol, cmd_arg1
	rjmp	.finish_command

.cmd_noise_reload:
	; set noise reload (+3 = 13)
	mov	noise_reload, cmd_arg1
	rjmp	.finish_command

	;---------------------------------------------------------

.sample_ram_cmds: ; (+3 = 5)

	; always store first arg (+3 = 8)
	mov	xl, cmd_arg1
	st	x+, cmd_arg2

	; optionally store second (+2/3 = 10/11)
	sbrc	cmd_op, 0
	st	x, cmd_arg3

	; finish (+2 = 12/13)
	rjmp	.finish_command

	;---------------------------------------------------------
.channel_cmds: ; (+5 = 7)
	; separate channel number (in upper nybble) from command (lower nybble) (+3 = 10)
	mov	temp, cmd_op
	andi	temp, 0x30
	andi	cmd_op, 0xF

	; compute channel base address (+2 = 12)
	ldi	yl, RAM_START
	add	yl, temp

	; let's dispatch (+8 = 20)
	ldi	zh, pm_hi8(.channel_cmd_jumptable) ; z = channel_cmd_jumptable + 2*cmd_op
	ldi	zl, pm_lo8(.channel_cmd_jumptable)
	add	zl, cmd_op
	adc	zl, ZERO
	ijmp
.channel_cmd_jumptable:
	rjmp	.channel_flags
	rjmp	.channel_rate
	rjmp	.channel_phase
	rjmp	.channel_rate_reset
	rjmp	.channel_sample
	rjmp	.channel_vol

.channel_flags: ; set flags (+3 = 23)
	st	y, cmd_arg1
	rjmp	.finish_command
.channel_rate:  ; set rate (+11 = 31)
	inc	yl
	st	y+, cmd_arg1
	inc	yl
	st	y+, cmd_arg2
	inc	yl
	st	y+, cmd_arg3
	rjmp	.finish_command
.channel_phase: ; set phase (+11 = 31)
	subi	yl, -2 ; add 2
	st	y+, cmd_arg1
	inc	yl
	st	y+, cmd_arg2
	inc	yl
	st	y+, cmd_arg3
	rjmp	.finish_command
.channel_rate_reset: ; set rate and reset phase (+15 = 35)
	inc	yl
	st	y+, cmd_arg1
	st	y+, ZERO
	st	y+, cmd_arg2
	st	y+, ZERO
	st	y+, cmd_arg3
	st	y+, ZERO
	rjmp	.finish_command
.channel_sample: ; set sample (+7 = 27)
	subi	yl, -7 ;add 7
	st	y+, cmd_arg2 ; len
	st	y+, cmd_arg1 ; start
	rjmp	.finish_command
.channel_vol: ; set volume (+6 = 26)
	subi	yl, -9; add 9
	andi	cmd_arg1, 0xF
	st	y, cmd_arg1
	rjmp	.finish_command

.finish_command:
	; longest command was set rate and reset phase (35)

	; reset state machine and tell host we're accepting commands (+3 = 38)
	ldi	cmd_state, CMD_STATE_WAIT_OP
	sbi	cmd_ready

	; restore zh and return (+6 = 44)
	pop	zh
	ret