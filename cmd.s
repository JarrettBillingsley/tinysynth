#include <avr/io.h>

#include "tinysynth.inc"

; ----------------------------------------------------------------------------
; USI overflow vector

; receiving full 3-byte command 17 + 17 + 18 = 52 cyc
; update loop takes 239, so 291 cyc; leaves ~200 cyc for command processing (so ROOMY)

.global	USI_OVF_vect
USI_OVF_vect:
	; (+3 = 3)
	in	sreg_save, IO(SREG)
	sbi	IO(USISR), USIOIF   ; acknowledge interrupt

	; all paths are (+6 = 9)
	sbrc	cmd_state, CMD_STATE_WAIT_OP_BIT
	in	cmd_op, IO(USIBR)              ; got op
	sbrc	cmd_state, CMD_STATE_WAIT_ARG1_BIT
	in	cmd_arg1, IO(USIBR)            ; got arg1
	sbrc	cmd_state, CMD_STATE_WAIT_ARG2_BIT
	in	cmd_arg2, IO(USIBR)            ; got arg2

	; (+1 = 10)
	; note: if we were in CMD_STATE_READY, this enters an invalid state
	; but we're assuming the host will play nice.
	lsl	cmd_state

	; (+2/3 = 12/13)
	sbrc	cmd_state, CMD_STATE_READY_BIT
	cbi	cmd_ready

	;in	temp_ISR, IO(USIBR)
	;out	SIM_OUTPUT, temp_ISR

	; (+5 = 17/18)
	out	IO(SREG), sreg_save
	reti

; ----------------------------------------------------------------------------
; setup

.global cmd_setup
cmd_setup:
	; set up state machine
	ldi	cmd_state, CMD_STATE_WAIT_OP

	out	IO(USIDR), ZERO
	out	IO(USISR), ZERO ; clear USI counter too

	; USIOIE == 1 (enable counter overflow interrupt)
	; USIWM == 01 (three-wire/SPI mode)
	; USICS == 10 (external clock; register clocked on positive edge)
	ldi	temp, _BV(USIOIE) | _BV(USIWM0) | _BV(USICS1)
	out	IO(USICR), temp

	; tell host we are ready to accept commands
	sbi	cmd_ready
	ret

; ----------------------------------------------------------------------------
; command processing

.global cmd_process
cmd_process:
	; using z for indirect jump in this function (+2 = 2)
	push	zh

	; we've got a command ready. let's dispatch (+8 = 10)
	ldi	zh, pm_hi8(.jumptable) ; z = jumptable + 2*cmd_op
	ldi	zl, pm_lo8(.jumptable)
	add	zl, cmd_op
	adc	zl, ZERO
	ijmp
.jumptable:
	rjmp	.cmd_silence
	rjmp	.cmd_mix_shift
	rjmp	.cmd_write_reg
	rjmp	.cmd_write_sample

.cmd_silence:
	; silence all channels (+11)
	sts	(RAM_START + (0 * SIZEOF_CHANNEL)), ZERO
	sts	(RAM_START + (1 * SIZEOF_CHANNEL)), ZERO
	sts	(RAM_START + (2 * SIZEOF_CHANNEL)), ZERO
	sts	(RAM_START + (3 * SIZEOF_CHANNEL)), ZERO
	clr	noise_vol
	rjmp	.finish_command

.cmd_mix_shift:
	; set mix shift (+4)
	andi	cmd_arg1, 3
	mov	mix_shift, cmd_arg1
	rjmp	.finish_command

.cmd_write_reg:
	; write "register" (+7)
	cpi	cmd_arg1, 0x40
	brge	.write_noise
	mov	yl, cmd_arg1
	st	Y, cmd_arg2
	rjmp	.finish_command

	; 3 from cpi-brge above, overall (+9)
.write_noise:
	; 0x40 == noise_vol (3+5 = 8)
	; 0x41 == noise_reload (3+6 = 9)
	; others invalid (3+4 = 7)
	breq	0f ; equal to 0x40 (from the cpi above)
	cpi	cmd_arg1, 0x41
	brne	.finish_command
	mov	noise_reload, cmd_arg2
	rjmp	.finish_command
0:	mov	noise_vol, cmd_arg2
	rjmp	.finish_command

.cmd_write_sample:
	; write value to sample RAM (+3)
	mov	xl, cmd_arg1
	st	x, cmd_arg2

.finish_command:
	; longest command was silence all (+11 = 21)

	; reset state machine and tell host we're accepting commands (+3 = 24)
	ldi	cmd_state, CMD_STATE_WAIT_OP
	sbi	cmd_ready

	; restore zh and return (+6 = 30)
	pop	zh
	ret