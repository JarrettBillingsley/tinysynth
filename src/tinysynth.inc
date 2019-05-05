; ----------------------------------------------------------------------------
; Constant defines

#define NUM_CHANNELS               8
#define SIZEOF_CHANNEL             7
#define DISABLED_CHANNEL_SKIP (SIZEOF_CHANNEL - 1)
#define DISABLED_PHASE_SKIP        3
#define RAM_START               0x60
#define SAMPLE_RAM_START      (0x100 - RAM_START)
#define SAMPLE_RAM_SIZE        0x100
#define VOLUME_TABLE_SIZE      0x100

; these are the bit numbers for each state
#define CMD_STATE_WAIT_OP_BIT    0
#define CMD_STATE_WAIT_ARG1_BIT  1
#define CMD_STATE_WAIT_ARG2_BIT  2
#define CMD_STATE_WAIT_ARG3_BIT  3
#define CMD_STATE_READY_BIT      4

; command state value is "one-hot"
#define CMD_STATE_WAIT_OP        (1 << CMD_STATE_WAIT_OP_BIT)
#define CMD_STATE_WAIT_ARG1      (1 << CMD_STATE_WAIT_ARG1_BIT)
#define CMD_STATE_WAIT_ARG2      (1 << CMD_STATE_WAIT_ARG2_BIT)
#define CMD_STATE_WAIT_ARG3      (1 << CMD_STATE_WAIT_ARG3_BIT)
#define CMD_STATE_READY          (1 << CMD_STATE_READY_BIT)

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

; IO REGISTERS AND IO REGISTER BITS
#define SIM_OUTPUT   IO(GPIOR0)    // used to output debugging info in the simulator (simavr)
#define sample_ready IO(GPIOR1), 0 // 1 when main loop has produced a sample, 0 when ISR needs one
#define cmd_ready    IO(PORTB), 3  // 1 when ready to accept commands, 0 when processing

; LOW REGISTERS
#define ZERO         0     // always holds 0.
#define sreg_save    1     // saves status reg in ISR.
#define sample_buf   2     // 16-bit sample accumulator; ISR outputs low byte when sample_ready=1
#define noise_vol    4     // volume of noise channel (0..15)
#define noise_lfsr   5     // 16-bit linear feedback shift reg for noise channel
#define noise_ctr    7     // how many samples until next noise channel update
#define noise_reload 8     // what to reload noise_ctr with after update (controls its pitch)
#define flags        9     // channel flags, currently only used for "enable"
#define phase        10    // position in the sample; high byte becomes offset
#define offset       phase // ^
#define volume       phase // channel volume
#define rate         11    // added to phase every update
#define len_mask     rate  // length of sample as a mask
#define sample       rate  // the sample loaded from sample RAM (and then scaled from vol table)
#define start        rate  // the address in sample RAM where the sample starts
#define I            12    // loop counter for the main update loop (0 .. NUM_CHANNELS)
#define sreg_save2   13    // saves status reg in USI ISR; it allows nested interrupt for timer ISR
; 14-15 unused
#define temp         16    // free to use as a temp reg.
#define temp_ISR     17    // temp reg only used in ISR.
#define mix_shift    18    // how much to shift the final mixed sample
#define cmd_state    19    // command state machine state
#define cmd_op       20    // what command to execute
#define cmd_arg1     21    // 1st argument byte
#define cmd_arg2     22    // 2nd argument byte
#define cmd_arg3     23    // 3rd argument byte

; 24-25 unused
; x: unused
; y: channel data pointer
; z: sample RAM/volume table pointer