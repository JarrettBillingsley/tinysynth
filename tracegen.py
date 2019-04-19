# generates input traces for simulation.

header = """$timescale 1us $end
$scope module logic $end
	$var wire 1 D iogB_0 $end
	$var wire 1 C iogB_2 $end
$upscope $end
$enddefinitions $end
$dumpvars
	0D
	0C
$end"""

ending = "#1000000 0D 0C"

CMD_SILENCE      = 0x00
CMD_MIX_SHIFT    = 0x01
CMD_NOISE_VOL    = 0x02
CMD_NOISE_RELOAD = 0x03
CMD_CHAN_FLAGS   = 0x40 # channel 1
CMD_CHAN_RATE    = 0x41
CMD_CHAN_PHASE   = 0x42
CMD_CHAN_NEWRATE = 0x43
CMD_CHAN_SAMPLE  = 0x44
CMD_CHAN_VOL     = 0x45
CMD_SAMPLE_SET1  = 0x80
CMD_SAMPLE_SET2  = 0x81

# all times measured in microseconds
time       = 1000 # where we start
byte_delay =    3 # how long to wait after sending a byte
bit_delay  =    1 # how long to wait after sending a bit
samp_delay =   31 # how long between samples

def out(signal, value):
	global time
	print("#{} {}{}".format(time, value, signal))

def send_bit(b):
	global time
	out('D', b)
	time += bit_delay
	out('C', 1)
	time += bit_delay
	out('C', 0)
	time += bit_delay

def send_byte(b):
	global time
	for i in reversed(range(8)):
		send_bit((b >> i) & 1)
	time += byte_delay

def send_cmd(op, a = 0, b = 0, c = 0):
	send_byte(op)
	send_byte(a)
	send_byte(b)
	send_byte(c)

def send_chan_cmd(ch, cmd, a = 0, b = 0, c = 0):
	send_cmd(cmd + 0x10 * ch, a, b, c)

def vol_fade(ch, src, dst, delay):
	global time
	if src < dst:
		for i in range(src, dst + 1):
			send_chan_cmd(ch, CMD_CHAN_VOL, i)
			time += delay
	else:
		for i in range(src, dst - 1, -1):
			send_chan_cmd(ch, CMD_CHAN_VOL, i)
			time += delay

print(header)
send_cmd(CMD_NOISE_VOL, 0)
time += samp_delay
vol_fade(0, 15, 0, 500)
vol_fade(0, 0, 15, 500)
print(ending)