#! /usr/local/bin/python3

import sys
from serial import Serial, SerialException
from serial.tools import list_ports
from enum import IntEnum

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from TSHost import Ui_MainWindow

class MidiStatus(IntEnum):
	NoteOff        = 0x80
	NoteOn         = 0x90
	PolyAftertouch = 0xA0
	CC             = 0xB0
	ProgramChange  = 0xC0
	ChanAftertouch = 0xD0
	PitchBend      = 0xE0
	SysEx          = 0xF0

class CC(IntEnum):
	AllSoundOff = 120

class MidiConnection:
	def __init__(self, portName, speed = 115200, timeout = None):
		"""
		Throws SerialException if the connection could not be opened.
		"""
		self.portName = portName
		self.speed = speed
		self.timeout = timeout
		self.port = Serial(port=self.portName, baudrate=self.speed, timeout = timeout, write_timeout=self.timeout)

	def noteOff(self, ch, n, v): self._send(MidiStatus.NoteOff | (ch - 1), n, v)
	def noteOn(self, ch, n, v):  self._send(MidiStatus.NoteOn | (ch - 1), n, v)
	def panic(self):             self._send(MidiStatus.CC, CC.AllSoundOff)

	def _send(self, *args):
		self.port.write(bytes(args))

	def close(self):
		self.port.close()

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.connection = None

		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)

		self.ui.displayADSR.setSliders([
			self.ui.sliderAttack,
			self.ui.sliderDecay,
			self.ui.sliderSustain,
			self.ui.sliderRelease,
		])

		self.ui.widgetKeyboard.scene().setPianoHandler(self)

		self.ui.buttonRefresh.clicked.connect(self.refresh)
		self.ui.buttonConnect.clicked.connect(self.connect)

		self.show()

	def refresh(self, _):
		combo = self.ui.comboSerial
		combo.clear()
		for port in sorted(list_ports.comports()):
			combo.addItem(port.device)

	def connect(self, _):
		if self.connection:
			self.connection.close()

		port = self.ui.comboSerial.currentText()

		try:
			self.connection = MidiConnection(port)
		except SerialException as e:
			mb = QMessageBox(text = "Could not open port.")
			mb.exec()

	def noteOn(self, n, v):
		if self.connection:
			self.connection.noteOn(1, n, v)

	def noteOff(self, n, v):
		if self.connection:
			self.connection.noteOff(1, n, v)

if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = MainWindow()
	sys.exit(app.exec_())
