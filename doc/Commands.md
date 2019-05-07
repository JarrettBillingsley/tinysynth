# Command interface

The synth is controlled over SPI. Kinda. Marginally-compliant SPI.

There aren't many pins, and the tiny's weird USI peripheral is about the best chance we have at transferring bits asynchronously at a reasonable speed.

## Inputs and outputs

Hook things up like so:

```
+----------+   MOSI   +-----------+
|         >|----------|PB0        |
|          |   SYNC   |           |
|         >|----------|PB1        |
|   Host   |   SCK    |   Synth   |
|         >|----------|PB2        |
|          |   READY  |           |
|         <|----------|PB3        |
+----------+          +-----------+
```

`MOSI` and `SCK` might come from the host's hardware peripheral, or maybe it's just bit-banged. `SYNC` and `READY` are definitely not SPI signals.

> See, `PB1` *would* be used as `MISO`, but because of a hardware bug in many ATTiny85s, we can't use it as an output, only an input.

## Hardware protocol

`READY` is the only communication the synth has to the host. When it goes high, that means it's accepting commands.

All commands are 32 bits (4 bytes) long. Bits are clocked in on the rising edge of SCK. SCK could idle high (like SPI mode 3) or low (like SPI mode 0), it doesn't really matter.

> On the ATMega328 (Arduino), SPI mode 0 causes MOSI to idle high, which the tiny's USI doesn't... really seem to like. Mode 3 is more reliable, but you must send a `SYNC` after enabling the ATMega's SPI peripheral, since the SCK will transition from low to high, tricking the USI into thinking it's getting a bit.

Each byte of a command must be followed by a short delay of 1-2µs for the synth to process it. Software interrupt, okay?

Only one command can be sent per sample period (~61µs). Each command takes at most about 1 sample period to process.

**Do not send any bits while the `READY` signal is low.** Bad things will happen. There is no correctness checking on this protocol. No time. Gotta go fast.

So, **tl;dr**

1. Synth raises `READY` high
2. Host sees `READY` go high, and sends a 4-byte command, with a 1-2µs pause between bytes
3. `READY` goes low, and the host has to wait
4. After at most one sample period (~61µs), back to step 1

I'm thinking you could set up the host to have a command queue and a pin change interrupt on `READY`, where it would push out a command from the queue whenever `READY` goes high.

## The `SYNC` input

`SYNC` can be used by the host to put the synth's command processor into a known state. It's an edge-sensitive input; toggling it either direction will do the job.

If it is currently processing a command (`READY` is low), the current command will still be processed, but any bits in the USI buffer will be tossed out.

If it is not processing a command (`READY` is still high), any command bytes already received will be discarded, and any bits in the USI buffer will be tossed out.

In either case, after a `SYNC`, the command processor will be waiting for 32 bits again.

Why does this exist? It's kind of a bodge. I ran into issues with the ATMega328's SPI peripheral outputting spurious clock pulses when enabled, which would knock the synth out of sync. Maybe spurious clocks can happen in other circumstances, idk.

---

## Shadow state and committing

Since the command interface is so slow (relative to the sample rate), it would normally be impossible to e.g. start notes on more than one channel at exactly the same time.

Because of this, **most commands do not have an immediate effect.** Instead, there is a *shadow state,* a copy of all the synth state which the commands operate on.

The host can issue many commands over a period of time. None will affect the sound output. Then, the host issues a **commit** command to copy the shadow state to the synth state in *the time of a single sample,* so all the changes will happen at once.

```
 (most)      +--------------+    commit     +--------------+    sound!
commands --->| Shadow state | ------------> | Synth state  | ------------>
             +--------------+               +--------------+
```

There are two exceptions, commands which immediately affect the synth output: the **silence all** command and the **sample RAM** commands. Sadly, there just isn't enough RAM to keep a shadow copy of sample RAM. But with clever sample use, the composer can avoid playing parts of sample RAM which are being overwritten. Or, just overwrite em while they're playing, whatever, it's fiiiiiine

---

## The commands!

Commands are 4 bytes. The first byte is the operation, and the other three bytes are the arguments.

Commands are listed in the format `0x00(a,b,_)`: this means an operation byte of `0x00`, two argument bytes `a` and `b`, and an unused byte indicated by `_`. Not all commands use all bytes, so for dummy bytes you can send whatever (0s usually).

### Global commands

- **`0x00(_,_,_)`: Silence all, instantaneously**
	- AKA "panic" or "omg shut up"
	- All channels are disabled, and the noise volume is set to 0.
	- **This command does not need to be committed. The synth state is immediately modified.**
- **`0x01(_,_,_)`: Commit**
	- Copies the shadow state to the synth state.
- **`0x02(shift,_,_)`: Set mix shift**
	- Kind of a "global volume." After mixing all channels together, this shifts the output sample down into the range of a byte (since the output is effectively 8 bits).
	- `shift` is in the range [0, 3]. Defaults to 3.
- **`0x03(vol,_,_)`: Set noise volume**
	- Sets the noise channel's volume to `vol`, in the range [0, 15].
- **`0x04(reload,_,_)`: Set noise reload**
	- Kind of the noise channel's "pitch." Higher values are lower pitches. 0 is the highest pitch.
- **`0x05(addr, val, _)`: Load 1 sample byte**
	- `samples[addr] = val`
	- `val` is 8 bits, so 2 samples.
	- **This command does not need to be committed. The synth state is immediately modified.**
- **`0x06(addr, val1, val2)`: Load 2 sample bytes**
	- `samples[addr] = val1; samples[addr+1] = val2`
	- It's faster, so typically you'll use this.
	- **This command does not need to be committed. The synth state is immediately modified.**
- **`0x07(mask, _, _)`: Set channel enable mask**
	- `mask` is a bit mask of channels to enable.
		- The LSB (bit 0) is channel 1.
		- The MSB (bit 7) is channel 8.
	- So for instance, a mask of `0x1F` would enable channels 1-5 and disable 6-8.
	- Disabled channels do not contribute to sound output, and their phase will not update.
		- If you want the channel to be silent but still update the phase, enable it and set its volume to 0.

### Channel commands

For these, the channel is selected by the high nybble of the operation byte:

- `0x80` for channel 1
- `0x90` for channel 2
- `0xA0` for channel 3 etc. until
- `0xF0` for channel 8.

The low nybble selects the actual operation:

* **`0xN0(lo, mid, hi):` Set rate**
	- This is the "pitch" of the channel.
	- It's 24 bits, and given in little-endian order.
	- Higher values = higher pitch.
* **`0xN1(lo, mid, hi):` Set phase**
	- This is *where* in the sample the channel currently is.
	- It's also 24 bits, little-endian.
	- 0 is the beginning of the sample.
* **`0xN2(lo, mid, hi):` Set rate and reset phase**
	- Like `0xN0`, but also resets the phase to 0 (the beginning of the sample).
	- This is probably what you want when you play a "new note."
		- `0xN0` is more like "changing the pitch of a running note."
* **`0xN3(start, mask,_):` Set samples**
	- Sets this channel to use samples starting at BYTE address `start`.
	- `mask` controls the "length" of the sample. Kind of.
		- Say you have a sample starting at byte `0x20` and it's 32 samples long.
		- 32 samples is 16 bytes, so it lasts from `0x20` to `0x2F`.
		- For this, you'd use a `mask` of `0x0F` (15).
		- So generally speaking, for an N-sample sound, you'd use a mask of `(N ÷ 2) - 1`.
		- But since this is a bitwise mask, you're technically not limited to *consecutive* samples...
* **`0xN4(vol,_,_):` Set volume**
	- Sets the volume to `vol`, in the range [0, 15].
	- A channel with a volume of 0 is **not** the same as a disabled channel!
		- When the volume is 0 and the channel is enabled, the channel's phase is still updated.
		- This way, you can do e.g. tremolo/ducking effects, and the sample phase will be correct.