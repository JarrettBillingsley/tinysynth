; ----------------------------------------------------------------------------
; Constant defines

#define NUM_CHANNELS               4
#define SIZEOF_CHANNEL            16
#define DISABLED_CHANNEL_SKIP     15
#define ENABLED_CHANNEL_SKIP       6
#define RAM_START               0x60
#define SAMPLE_RAM_START       0x100 - RAM_START
#define SAMPLE_RAM_SIZE        0x100
#define VOLUME_TABLE_START    0x0300 - 0x30
#define VOLUME_TABLE_SIZE      0x100

; ----------------------------------------------------------------------------
; General defines

; no more screamy registers!!!
#define xl XL
#define xh XH
#define yl YL
#define yh YH
#define zl ZL
#define zh ZH

#define IO(X) _SFR_IO_ADDR(X)

; ----------------------------------------------------------------------------
; Register defines

; LOW REGISTERS

; ZERO:         always holds 0.
; sreg_save:    saves status reg in ISR.
; sample_ready: 1 when the main loop has produced a sample, 0 when ISR needs one
; sample_buf:   16-bit accumulator for mixing samples; ISR outputs low byte when sample_ready=1
; noise_vol:    volume of noise channel (0..15)
; noise_lfsr:   16-bit linear feedback shift reg for noise channel
; noise_ctr:    how many samples until next noise channel update
; noise_reload: what to reload noise_ctr with after update (controls its pitch)
; flags:        channel flags, currently only used for "enable"
; phase:        position in the sample; high byte becomes offset
; offset:       ^
; volume:       channel volume
; rate:         added to phase every update
; len_mask:     length of sample as a mask
; sample:       the actual sample loaded from sample RAM (and then scaled from vol table)
; start:        the address in sample RAM where the sample starts
; I:            loop counter for the main update loop (0 .. NUM_CHANNELS)

#define ZERO         0
#define sreg_save    1
#define sample_ready 2
#define sample_buf   3
; ^ 16-bit
#define noise_vol    5
#define noise_lfsr   6
; ^ 16-bit
#define noise_ctr    8
#define noise_reload 9
#define flags        10
#define phase        11
#define offset       phase
#define volume       phase
#define rate         12
#define len_mask     rate
#define sample       rate
#define start        rate
#define I            13

; 14-15 unused

; HIGH REGISTERS

; temp:         free to use as a temp reg.
; temp_ISR:     temp reg only used in ISR.
; mix_shift:    how much to shift the final mixed sample (hireg: must be compared to immediate)
#define temp         16
#define temp_ISR     17
#define mix_shift    18

; 19-25 unused

; x: sample ram pointer
; y: channel data pointer
; z: volume table pointer