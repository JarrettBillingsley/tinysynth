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
CMD_COMMIT       = 0x01
CMD_MIX_SHIFT    = 0x02
CMD_NOISE_VOL    = 0x03
CMD_NOISE_RELOAD = 0x04
CMD_SAMPLE_SET1  = 0x05
CMD_SAMPLE_SET2  = 0x06
CMD_ENABLE_CHAN  = 0x07
CMD_CHAN_RATE    = 0x80 # channel 1
CMD_CHAN_PHASE   = 0x81
CMD_CHAN_NEWRATE = 0x82
CMD_CHAN_SAMPLE  = 0x83
CMD_CHAN_VOL     = 0x84

# all times measured in microseconds
time       = 1000 # where we start
byte_delay =    3 # how long to wait after sending a byte
bit_delay  =    1 # how long to wait after sending a bit
samp_delay =   62 # how long between samples

def out(signal, value):
	print("#{} {}{}".format(time, value, signal))

def delay(n):
	global time
	time += n

def delay_samples(n):
	delay(n * samp_delay)

def send_bit(b):
	out('D', b)
	delay(bit_delay)
	out('C', 1)
	delay(bit_delay)
	out('C', 0)
	delay(bit_delay)

def send_byte(b):
	for i in reversed(range(8)):
		send_bit((b >> i) & 1)
	delay(byte_delay)

def send_cmd(op, a = 0, b = 0, c = 0):
	send_byte(op)
	send_byte(a)
	send_byte(b)
	send_byte(c)
	delay(samp_delay)

def send_chan_cmd(ch, cmd, a = 0, b = 0, c = 0):
	send_cmd(cmd + 0x10 * ch, a, b, c)

def split24(n):
	return (n & 0xFF, (n >> 8) & 0xFF, (n >> 16) & 0xFF)

def silence():                send_cmd(CMD_SILENCE)
def commit():                 send_cmd(CMD_COMMIT)
def mix_shift(n):             send_cmd(CMD_MIX_SHIFT, n)
def noise_vol(n):             send_cmd(CMD_NOISE_VOL, n)
def noise_reload(n):          send_cmd(CMD_NOISE_RELOAD, n)
def sample(a, n):             send_cmd(CMD_SAMPLE_SET1, a, n)
def samples(a, n, m):         send_cmd(CMD_SAMPLE_SET2, a, n, m)
def enable_channels(n):       send_cmd(CMD_ENABLE_CHAN, n)
def channel_rate(ch, n):      send_chan_cmd(ch, CMD_CHAN_RATE, *split24(n))
def channel_phase(ch, n):     send_chan_cmd(ch, CMD_CHAN_PHASE, *split24(n))
def channel_newrate(ch, n):   send_chan_cmd(ch, CMD_CHAN_NEWRATE, *split24(n))
def channel_sample(ch, s, l): send_chan_cmd(ch, CMD_CHAN_SAMPLE, s, l)
def channel_vol(ch, n):       send_chan_cmd(ch, CMD_CHAN_VOL, n)

def vol_fade(ch, src, dst, d):
	if src < dst:
		r = range(src, dst + 1)
	else:
		r = reversed(range(dst, src + 1))

	for i in r:
		channel_vol(ch, i)
		commit()
		delay(d)

def commit_test():
	for i in range(8):
		enable_channels(1 << i)
		delay_samples(10)
		commit()
		delay_samples(50)

def phase_test():
	silence()
	delay_samples(10)
	enable_channels(1)
	commit()
	delay_samples(10)

	# should not change phase
	channel_rate(0, 0x10000)
	commit()
	delay_samples(500)
	channel_rate(0, 0x4000)
	commit()
	delay_samples(500)

	# SHOULD change phase
	channel_phase(0, 0)
	commit()
	delay_samples(500)

	# should ALSO change phase
	channel_newrate(0, 0x10000)
	commit()

# --------------------------------------------------------------

print(header)
# commit_test()
phase_test()
print(ending)