/* -------------------------------------------------------------------------------------------------

Arduino host for the tinysynth, kinda. Developed and tested on an Arduino Uno R3.

Based originally on the ArduinoISP program, then heavily modified.

When it starts, it acts as an Arduino ISP and can be used to program the ATTiny, as long as there's
a capacitor between RST and GND.

After a few seconds, it turns into a serial MIDI interface running at 115200baud, which can be
controlled with something like hairless MIDI.

Alternatively, in the period before it becomes a MIDI interface, you can use a serial terminal to
send a T (capital T) character, and it will go into a sort of interactive text console mode.

It's weird and hacky! Whatever! Proof of concept! GOD!

------------------------------------------------------------------------------------------------- */

#include "Arduino.h"
#include "SPI.h"
#include <MIDI.h>

// -------------------------------------------------------------------------------------------------
// Constants
// -------------------------------------------------------------------------------------------------

#define BAUDRATE	        115200
#define AVRISP_TIMEOUT      (500000)
#define STATE_WAIT          0
#define STATE_PROG          1
#define STATE_TS            2
#define STATE_MIDI          3

#define SPI_CLOCK           (1000000/6)
#define PIN_MOSI 	        MOSI
#define PIN_MISO 	        MISO
#define PIN_SCK 	        SCK
#define PIN_RESET           10
#define PIN_READY           9
#define PIN_SYNC            8
#define HWVER               2
#define SWMAJ               1
#define SWMIN               18
#define EECHUNK             32
#define PULSE_TIME          30

#define STK_OK              0x10
#define STK_FAILED          0x11  // Not used
#define STK_UNKNOWN         0x12  // Not used
#define STK_INSYNC          0x14
#define STK_NOSYNC          0x15  // Not used
#define CRC_EOP             0x20  // ' '
#define STK_GET_SYNC        0x30  // '0'
#define STK_GET_SIGN_ON     0x31  // '1'
#define STK_GET_PARAMETER   0x41  // 'A'
#define STK_SET_DEVICE      0x42  // 'B'
#define STK_SET_DEVICE_EXT  0x45  // 'E'
#define STK_ENTER_PROGMODE  0x50  // 'P'
#define STK_LEAVE_PROGMODE  0x51  // 'Q'
#define STK_LOAD_ADDRESS    0x55  // 'U'
#define STK_UNIVERSAL       0x56  // 'V'
#define STK_PROG_FLASH      0x60  // '`'
#define STK_PROG_DATA       0x61  // 'a'
#define STK_PROG_PAGE       0x64  // 'd'
#define STK_READ_PAGE       0x74  // 't'
#define STK_READ_SIGN       0x75  // 'u'

// -------------------------------------------------------------------------------------------------
// Macros
// -------------------------------------------------------------------------------------------------

#define beget16(addr)   (((addr)[0] << 8) | (addr)[1])
#define beget32(addr)   (((long)(addr)[16] << 24) |\
						((long)(addr)[17] << 16) |\
						((long)(addr)[18] << 8) |\
						 (long)(addr)[19])
#define delay_cycles(n) __builtin_avr_delay_cycles(n)

// -------------------------------------------------------------------------------------------------
// Variables
// -------------------------------------------------------------------------------------------------

uint8_t state = STATE_WAIT;
bool rst_active_high = false;
bool autocommit = false;
uint32_t here;
uint8_t buff[256];
uint32_t avrisp_timeout;
int32_t note_tuning = 0;

struct {
	uint8_t devicecode;
	uint8_t revision;
	uint8_t progtype;
	uint8_t parmode;
	uint8_t polling;
	uint8_t selftimed;
	uint8_t lockbytes;
	uint8_t fusebytes;
	uint8_t flashpoll;
	uint16_t eeprompoll;
	uint16_t pagesize;
	uint16_t eepromsize;
	uint32_t flashsize;
} param;

struct MySettings : public midi::DefaultSettings {
	static const long BaudRate = 115200;
};

MIDI_CREATE_CUSTOM_INSTANCE(HardwareSerial, Serial, MIDI, MySettings);
int notes_on = 0;

// -------------------------------------------------------------------------------------------------
// Helpers
// -------------------------------------------------------------------------------------------------

void pulse(int pin, int times) {
	do {
		digitalWrite(pin, HIGH);
		delay(PULSE_TIME);
		digitalWrite(pin, LOW);
		delay(PULSE_TIME);
	} while(times--);
}

unsigned int current_page() {
	if(param.pagesize == 32)  return here & 0xFFFFFFF0;
	if(param.pagesize == 64)  return here & 0xFFFFFFE0;
	if(param.pagesize == 128) return here & 0xFFFFFFC0;
	if(param.pagesize == 256) return here & 0xFFFFFF80;
	return here;
}

void set_device() {
	read_into_buffer(20);
	param.devicecode = buff[0];
	param.revision   = buff[1];
	param.progtype   = buff[2];
	param.parmode    = buff[3];
	param.polling    = buff[4];
	param.selftimed  = buff[5];
	param.lockbytes  = buff[6];
	param.fusebytes  = buff[7];
	param.flashpoll  = buff[8];
	param.eeprompoll = beget16(&buff[10]);
	param.pagesize   = beget16(&buff[12]);
	param.eepromsize = beget16(&buff[14]);
	param.flashsize =  beget32(&buff[16]);
	rst_active_high = (param.devicecode >= 0xe0);
	empty_reply();
}

const int8_t ch_hex_table[] = {
	 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, -1, -1, -1, -1, -1, -1,
	-1, 10, 11, 12, 13, 14, 15, -1, -1, -1, -1, -1, -1, -1, -1, -1,
	-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1,
	-1, 10, 11, 12, 13, 14, 15
};

int8_t parse_hex_digit(char ch) {
	if(ch >= '0' && ch <= 'f') {
		return ch_hex_table[ch - '0'];
	} else {
		return -1;
	}
}

// -------------------------------------------------------------------------------------------------
// Host communication
// -------------------------------------------------------------------------------------------------

uint8_t getch() {
	while(!Serial.available());
	return Serial.read();
}

void read_into_buffer(int n) {
	for(int i = 0; i < n; i++) {
		buff[i] = getch();
	}
}

void empty_reply() {
	if(getch() == CRC_EOP) {
		Serial.print((char)STK_INSYNC);
		Serial.print((char)STK_OK);
	} else {
		Serial.print((char)STK_NOSYNC);
	}
}

void reply(uint8_t b) {
	if(getch() == CRC_EOP) {
		Serial.print((char)STK_INSYNC);
		Serial.print((char)b);
		Serial.print((char)STK_OK);
	} else {
		Serial.print((char)STK_NOSYNC);
	}
}

void reply(const char* str) {
	if(getch() == CRC_EOP) {
		Serial.print((char)STK_INSYNC);
		Serial.print(str);
		Serial.print((char)STK_OK);
	} else {
		Serial.print((char)STK_NOSYNC);
	}
}

void get_parameter() {
	switch(getch()) {
		case 0x80: reply(HWVER);      break;
		case 0x81: reply(SWMAJ);      break;
		case 0x82: reply(SWMIN);      break;
		case 0x93: reply('S');        break;
		default:   reply((uint8_t)0); break;
	}
}

void dummy(int thicc) {
	read_into_buffer(thicc);
	empty_reply();
}

void load_address() {
	here = getch();
	here += (getch() << 8);
	empty_reply();
}

void get_sync() {
	empty_reply();
}

// -------------------------------------------------------------------------------------------------
// Target communication
// -------------------------------------------------------------------------------------------------

uint8_t spi_transaction(uint8_t a, uint8_t b, uint8_t c, uint8_t d) {
	SPI.transfer(a);
	SPI.transfer(b);
	SPI.transfer(c);
	return SPI.transfer(d);
}

void reset_target(bool reset) {
	digitalWrite(PIN_RESET, (reset == rst_active_high) ? HIGH : LOW);
}

void universal() {
	read_into_buffer(4);
	reply(spi_transaction(buff[0], buff[1], buff[2], buff[3]));
}

// -------------------------------------------------------------------------------------------------
// Writing
// -------------------------------------------------------------------------------------------------

void commit(unsigned int addr) {
	spi_transaction(0x4C, (addr >> 8) & 0xFF, addr & 0xFF, 0);
}

uint8_t write_flash_pages(int length) {
	unsigned int page = current_page();

	for(int i = 0; i < length; i += 2) {
		unsigned char here_hi = (here >> 8) & 0xFF;
		unsigned char here_lo = here & 0xFF;

		spi_transaction(0x40, here_hi, here_lo, buff[i]);
		spi_transaction(0x48, here_hi, here_lo, buff[i + 1]);

		here++;

		if(page != current_page()) {
			commit(page);
			page = current_page();
		}
	}

	commit(page);
	return STK_OK;
}

void write_flash(int length) {
	read_into_buffer(length);
	if(getch() == CRC_EOP) {
		Serial.print((char)STK_INSYNC);
		Serial.print((char)write_flash_pages(length));
	} else {
		Serial.print((char)STK_NOSYNC);
	}
}

uint8_t write_eeprom_chunk(unsigned int start, unsigned int length) {
	read_into_buffer(length);

	for(unsigned int i = 0; i < length; i++) {
		unsigned int addr = start + i;
		spi_transaction(0xC0, (addr >> 8) & 0xFF, addr & 0xFF, buff[i]);
		delay(45);
	}

	return STK_OK;
}

uint8_t write_eeprom(unsigned int length) {
	if(length > param.eepromsize) {
		return STK_FAILED;
	}

	unsigned int start = here * 2;
	unsigned int remaining = length;

	while(remaining > EECHUNK) {
		write_eeprom_chunk(start, EECHUNK);
		start += EECHUNK;
		remaining -= EECHUNK;
	}

	write_eeprom_chunk(start, remaining);
	return STK_OK;
}

void program_page() {
	unsigned int length = 256 * getch();
	length += getch();

	char memtype = getch();

	if(memtype == 'F') {
		write_flash(length);
	}
	else if(memtype == 'E') {
		char result = (char)write_eeprom(length);
		if(getch() == CRC_EOP) {
			Serial.print((char)STK_INSYNC);
			Serial.print(result);
		} else {
			Serial.print((char)STK_NOSYNC);
		}
	}
	else {
		Serial.print((char)STK_FAILED);
	}
}

// -------------------------------------------------------------------------------------------------
// Reading
// -------------------------------------------------------------------------------------------------

uint8_t flash_read(uint8_t hilo, unsigned int addr) {
	return spi_transaction(0x20 + hilo * 8, (addr >> 8) & 0xFF, addr & 0xFF, 0);
}

char flash_read_page(int length) {
	for(int x = 0; x < length; x += 2) {
		uint8_t low = flash_read(LOW, here);
		Serial.print((char)low);
		uint8_t high = flash_read(HIGH, here);
		Serial.print((char)high);
		here++;
	}
	return STK_OK;
}

char eeprom_read_page(int length) {
	int start = here * 2;
	for(int i = 0; i < length; i++) {
		int addr = start + i;
		uint8_t ee = spi_transaction(0xA0, (addr >> 8) & 0xFF, addr & 0xFF, 0xFF);
		Serial.print((char)ee);
	}
	return STK_OK;
}

void read_page() {
	int length = 256 * getch();
	length += getch();

	char memtype = getch();

	if(getch() == CRC_EOP) {
		Serial.print((char)STK_INSYNC);
		if     (memtype == 'F') Serial.print(flash_read_page(length));
		else if(memtype == 'E') Serial.print(eeprom_read_page(length));
	} else {
		Serial.print((char)STK_NOSYNC);
	}
}

void read_signature() {
	if(getch() == CRC_EOP) {
		Serial.print((char)STK_INSYNC);
		Serial.print((char)spi_transaction(0x30, 0x00, 0x00, 0x00));
		Serial.print((char)spi_transaction(0x30, 0x00, 0x01, 0x00));
		Serial.print((char)spi_transaction(0x30, 0x00, 0x02, 0x00));
		Serial.print((char)STK_OK);
	} else {
		Serial.print((char)STK_NOSYNC);
	}
}

// -------------------------------------------------------------------------------------------------
// Main loop
// -------------------------------------------------------------------------------------------------

void startup() {
	// setup IO
	Serial.begin(BAUDRATE);
	pinMode(PIN_READY, INPUT);
	pinMode(PIN_SYNC, INPUT);

	// reset the TS
	reset_target(true);
	pinMode(PIN_RESET, OUTPUT);
	delay(1);
	reset_target(false);
	pinMode(PIN_RESET, INPUT);
}

void enter_wait_state() {
	state = STATE_WAIT;
	avrisp_timeout = AVRISP_TIMEOUT;
}

void enter_prog_state() {
	state = STATE_PROG;

	// hold reset low and then SCK
	reset_target(true);
	pinMode(PIN_RESET, OUTPUT);
	SPI.begin();
	SPI.beginTransaction(SPISettings(SPI_CLOCK, MSBFIRST, SPI_MODE0));
	digitalWrite(PIN_SCK, LOW);
	delay(20);

	// then un-reset...
	reset_target(false);
	delayMicroseconds(100);

	// reset again...
	reset_target(true);
	delay(50);

	// and send the programming command.
	spi_transaction(0xAC, 0x53, 0x00, 0x00);
	empty_reply();
}

void exit_prog_state() {
	SPI.endTransaction();
	SPI.end();
	reset_target(false);
	pinMode(PIN_RESET, INPUT);
	empty_reply();

	enter_wait_state();
}

void enter_ts_state() {
	state = STATE_TS;
	start_ts_comms();
	Serial.println("hi!");
}

void exit_ts_state() {
	Serial.println("bye!");
	enter_wait_state();
}

int main() {
	init(); // arduino
	startup();
	enter_wait_state();

	while(true) {

		switch(state) {
			case STATE_WAIT: wait();      break;
			case STATE_PROG: avrisp();    break;
			case STATE_TS:   tinysynth(); break;
			case STATE_MIDI: midi_state();      break;
		}
	}

	return 0;
}

void wait() {
	avrisp();

	if(--avrisp_timeout == 0) {
		enter_midi_state();
	} else if((avrisp_timeout & 0xFFFF) == 0x8000) {
		Serial.println(avrisp_timeout);
	}
}

void avrisp() {
	if(!Serial.available()) {
		return;
	}

	switch(getch()) {
		case STK_GET_SYNC:       get_sync();         break;
		case STK_GET_SIGN_ON:    reply("AVR ISP");   break;
		case STK_GET_PARAMETER:  get_parameter();    break;
		case STK_SET_DEVICE:     set_device();       break;
		case STK_SET_DEVICE_EXT: dummy(5);           break;
		case STK_ENTER_PROGMODE: enter_prog_state(); break;
		case STK_LOAD_ADDRESS:   load_address();     break;
		case STK_PROG_FLASH:     dummy(2);           break;
		case STK_PROG_DATA:      dummy(1);           break;
		case STK_PROG_PAGE:      program_page();     break;
		case STK_READ_PAGE:      read_page();        break;
		case STK_UNIVERSAL:      universal();        break;
		case STK_LEAVE_PROGMODE: exit_prog_state();  break;
		case STK_READ_SIGN:      read_signature();   break;

		case 'T':                enter_ts_state();   break;

		case CRC_EOP:
			Serial.print((char)STK_NOSYNC);
			break;

		default:
			if(getch() == CRC_EOP)
				Serial.print((char)STK_UNKNOWN);
			else
				Serial.print((char)STK_NOSYNC);
	}
}

// -------------------------------------------------------------------------------------------------
// TinySynth mode
// -------------------------------------------------------------------------------------------------

#define TS_SILENCE  0x00
#define TS_COMMIT   0x01
#define TS_MIXSHIFT 0x02
#define TS_NOISEVOL 0x03
#define TS_NOISEREL 0x04
#define TS_SAMPLE1  0x05
#define TS_SAMPLE2  0x06
#define TS_CHENABLE 0x07

#define TS_CH1RATE  0x80
#define TS_CH1PHASE 0x81
#define TS_CH1NOTE  0x82
#define TS_CH1SAMP  0x83
#define TS_CH1VOL   0x84

#define TS_CHRATE(n)  ((n)*0x10 + TS_CH1RATE )
#define TS_CHPHASE(n) ((n)*0x10 + TS_CH1PHASE)
#define TS_CHNOTE(n)  ((n)*0x10 + TS_CH1NOTE )
#define TS_CHSAMP(n)  ((n)*0x10 + TS_CH1SAMP )
#define TS_CHVOL(n)   ((n)*0x10 + TS_CH1VOL  )

void start_ts_comms() {
	SPI.begin();
	SPI.beginTransaction(SPISettings(2000000, MSBFIRST, SPI_MODE3));
	digitalWrite(PIN_SYNC, LOW);
	pinMode(PIN_SYNC, OUTPUT);
	PINB = 1;
	delay_cycles(3000);
}

void end_ts_comms() {
	pinMode(PIN_SYNC, INPUT);
	SPI.endTransaction();
}

bool get_hex_nybble(uint8_t* a) {
	int8_t ch = parse_hex_digit(getch());

	if(ch >= 0) {
		*a = ch;
		return true;
	}

	return false;
}

bool get_hex_byte(uint8_t* a) {
	int8_t ch1 = parse_hex_digit(getch());

	if(ch1 >= 0) {
		int8_t ch2 = parse_hex_digit(getch());

		if(ch2 >= 0) {
			*a = (ch1 << 4) | ch2;
			return true;
		}
	}

	return false;
}

bool get_hex_bytes_2(uint8_t* a, uint8_t* b) {
	return get_hex_byte(a) && get_hex_byte(b);
}

bool get_hex_bytes_3(uint8_t* a, uint8_t* b, uint8_t* c) {
	return get_hex_byte(a) && get_hex_byte(b) && get_hex_byte(c);
}

void raw_ts_command(uint8_t a, uint8_t b = 0, uint8_t c = 0, uint8_t d = 0) {
	SPDR = a; loop_until_bit_is_set(SPSR, SPIF); delay_cycles(20);
	SPDR = b; loop_until_bit_is_set(SPSR, SPIF); delay_cycles(20);
	SPDR = c; loop_until_bit_is_set(SPSR, SPIF); delay_cycles(20);
	SPDR = d; loop_until_bit_is_set(SPSR, SPIF); delay_cycles(5000);
}

void ts_command(uint8_t a, uint8_t b = 0, uint8_t c = 0, uint8_t d = 0) {
	Serial.print(a, HEX); Serial.print('.');
	Serial.print(b, HEX); Serial.print('.');
	Serial.print(c, HEX); Serial.print('.');
	Serial.println(d, HEX);
	raw_ts_command(a, b, c, d);
}

void ts_command_auto(uint8_t a, uint8_t b = 0, uint8_t c = 0, uint8_t d = 0) {
	ts_command(a, b, c, d);
	if(autocommit) ts_command(TS_COMMIT);
}

bool ts_command_1n(int cmd, const char* name) {
	uint8_t n;

	if(get_hex_nybble(&n)) {
		Serial.println(name);
		ts_command_auto(cmd, n);
		return true;
	}

	return false;
}

bool ts_command_1B(int cmd, const char* name) {
	uint8_t a;

	if(get_hex_byte(&a)) {
		Serial.println(name);
		ts_command_auto(cmd, a);
		return true;
	}

	return false;
}

bool ts_command_2B(int cmd, const char* name) {
	uint8_t a, b;

	if(get_hex_bytes_2(&a, &b)) {
		Serial.println(name);
		ts_command_auto(cmd, a, b);
		return true;
	}

	return false;
}

bool ts_command_3B(int cmd, const char* name) {
	uint8_t a, b, c;

	if(get_hex_bytes_3(&a, &b, &c)) {
		Serial.println(name);
		ts_command_auto(cmd, a, b, c);
		return true;
	}

	return false;
}

bool ts_command_24b(int cmd, const char* name) {
	uint8_t hi, mid, lo;

	if(get_hex_bytes_3(&hi, &mid, &lo)) {
		Serial.println(name);
		ts_command_auto(cmd, lo, mid, hi);
		return true;
	}

	return false;
}

void ts_enable_autocommit(bool enable) {
	Serial.println(enable ? "autocommit on" : "autocommit off");
	autocommit = enable;
}

void ts_sync() {
	Serial.println("syncing");
	PINB = 1;
}

void ts_silence() {
	Serial.println("silence");
	ts_command(TS_SILENCE);
}

void ts_commit() {
	Serial.println("committing");
	ts_command(TS_COMMIT);
}

void tinysynth() {
	if(!Serial.available()) {
		return;
	}

	char ch = getch();

	switch(ch) {
		// -----------------------------------------------------------------
		// meta commands

		case 'A': return ts_enable_autocommit(true);
		case 'a': return ts_enable_autocommit(false);
		case 'x': return exit_ts_state();
		case '@': return ts_sync();

		// -----------------------------------------------------------------
		// global commands

		case '!': return ts_silence();
		case 'c': return ts_commit();
		case 'm': if(ts_command_1n(TS_MIXSHIFT, "mix shift")) return; break;
		case 's': if(ts_command_2B(TS_SAMPLE1,  "set 1 sample")) return; break;
		case 'S': if(ts_command_3B(TS_SAMPLE2,  "set 2 samples")) return; break;
		case 'e': if(ts_command_1B(TS_CHENABLE, "channel enable")) return; break;

		// -----------------------------------------------------------------
		// channel commands

		case 'n':
			switch(getch()) {
				case 'v': if(ts_command_1n(TS_NOISEVOL, "noise volume")) return; break;
				case 'r': if(ts_command_1B(TS_NOISEREL, "noise reload")) return; break;
				default: break;
			}
			break;

		case '1': case '2': case '3': case '4': case '5': case '6': case '7': case '8': {
			uint8_t cmd = TS_CH1RATE + ((ch - '1') << 4); // 0x80 .. 0xF0

			switch(getch()) {
				case 'r': if(ts_command_24b(cmd|0, "channel rate"  )) return; break;
				case 'p': if(ts_command_24b(cmd|1, "channel phase" )) return; break;
				case 'n': if(ts_command_24b(cmd|2, "channel note"  )) return; break;
				case 's': if(ts_command_2B (cmd|3, "channel sample")) return; break;
				case 'v': if(ts_command_1n (cmd|4, "channel vol"   )) return; break;
				default: break;
			}
			break;
		}

		// ignore whitespace
		case '\r': case '\n': case '\t': case ' ': return;
		default: break;
	}

	Serial.println("uhh... what?");
}

// -------------------------------------------------------------------------------------------------
// MIDI mode
// -------------------------------------------------------------------------------------------------

void enter_midi_state() {
	state = STATE_MIDI;

	Serial.println("MIDI TIME BITCHES");
	Serial.flush();
	// Serial.end();

	MIDI.begin(MIDI_CHANNEL_OMNI);
	MIDI.setHandleNoteOn(handleNoteOn);
	MIDI.setHandleNoteOff(handleNoteOff);
	MIDI.setHandleControlChange(handleControlChange);

	pinMode(PIN_READY, INPUT);
	start_ts_comms();
	raw_ts_command(TS_SILENCE);
}

uint32_t note_to_freq[] = {
	/*C-*/   0x227,  0x248,  0x26B,  0x290,  0x2B7,  0x2E0,  0x30C,  0x33A,  0x36B,  0x39F,  0x3D7,  0x411,
	/*C0*/   0x44F,  0x491,  0x4D6,  0x520,  0x56E,  0x5C1,  0x618,  0x675,  0x6D7,  0x73F,  0x7AE,  0x823,
	/*C1*/   0x89F,  0x922,  0x9AD,  0xA40,  0xADC,  0xB82,  0xC31,  0xCEA,  0xDAF,  0xE7F,  0xF5C, 0x1046,
	/*C2*/  0x113E, 0x1244, 0x135A, 0x1481, 0x15B9, 0x1704, 0x1862, 0x19D5, 0x1B5F, 0x1CFF, 0x1EB9, 0x208C,
	/*C3*/  0x227C, 0x2488, 0x26B5, 0x2902, 0x2B72, 0x2E08, 0x30C5, 0x33AA, 0x36BE, 0x39FF, 0x3D72, 0x4119,
	/*C4*/  0x44F8, 0x4910, 0x4D6A, 0x5204, 0x56E4, 0x5C10, 0x618A, 0x6754, 0x6D7C, 0x73FE, 0x7AE4, 0x8232,
	/*C5*/  0x89F0, 0x9220, 0x9AD4, 0xA408, 0xADC8, 0xB820, 0xC314, 0xCEA8, 0xDAF8, 0xE7FC, 0xF5C8,0x10464,
	/*C6*/ 0x113E0,0x12440,0x135A8,0x14810,0x15B90,0x17040,0x18628,0x19D50,0x1B5F0,0x1CFF8,0x1EB90,0x208C8,
	/*C7*/ 0x227C0,0x24880,0x26B50,0x29020,0x2B720,0x2E080,0x30C50,0x33AA0,0x36BE0,0x39FF0,0x3D720,0x41190,
	/*C8*/ 0x44F80,0x49100,0x4D6A0,0x52040,0x56E40,0x5C100,0x618A0,0x67540,0x6D7C0,0x73FE0,0x7AE40,0x82320,
	/*C9*/ 0x89F00,0x92200,0x9AD40,0xA4080,0xADC80,0xB8200,0xC3140,0xCEA80
};

uint8_t note_vol = 0;
bool note_release = false;
uint16_t note_fade = 0;
#define NOTE_FADE_TIME 10000

void midi_state() {
	MIDI.read();

	if(note_vol) {
		if(note_fade) {
			note_fade--;
		}

		if(note_fade == 0) {
			note_fade = NOTE_FADE_TIME;

			if(note_release) {
				note_vol--;
				raw_ts_command(TS_CHVOL(0), note_vol);

				if(note_vol == 0) {
					note_release = false;
					raw_ts_command(TS_CHENABLE, 0);
				}
			} else if(note_vol < 15) {
				note_vol++;
				raw_ts_command(TS_CHVOL(0), note_vol);
			}

			raw_ts_command(TS_COMMIT);
		}
	}
}

void sync() {
	PINB = 1;
	delay_cycles(10000);
}

void silence_all() {
	notes_on = 0;
	raw_ts_command(TS_SILENCE);
}

void handleNoteOn(byte channel, byte note, byte velocity) {
	(void)channel;
	(void)velocity;

	if(note <= 127) {
		uint32_t freq = note_to_freq[note] + note_tuning;
		notes_on++;
		note_release = false;

		if(notes_on == 1 && note_vol == 0) {
			note_vol = 1;
		}

		raw_ts_command(/*notes_on == 1 ? TS_CHNOTE(0) :*/ TS_CHRATE(0),
			freq & 0xFF, (freq >> 8) & 0xFF, (freq >> 16) & 0xFF);
		raw_ts_command(TS_CHENABLE, 1);
		raw_ts_command(TS_CHVOL(0), note_vol);
		raw_ts_command(TS_COMMIT);
	}
}

void handleNoteOff(byte channel, byte note, byte velocity) {
	(void)channel;
	(void)note;
	(void)velocity;

	notes_on--;

	if(notes_on	== 0) {
		// raw_ts_command(TS_CHENABLE, 0);
		// raw_ts_command(TS_COMMIT);

		note_release = true;
		note_fade = NOTE_FADE_TIME;
	}
}

void handleControlChange(byte channel, byte number, byte value) {
	(void)channel;

	switch(number) {
		case 20: // mix shift
			raw_ts_command(TS_MIXSHIFT, value & 3);
			raw_ts_command(TS_COMMIT);
			break;

		case 21: // tuning
			note_tuning = ((int)value) - 63;
			break;

		case 120:
		case 123: // panic!
			sync();
			silence_all();
			break;

		default: break;
	}
}