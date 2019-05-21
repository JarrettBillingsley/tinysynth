from math import ceil, floor

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import *

from pianokey import PianoKey

class CONST:
	KEYWIDTH         = 18
	KEYHEIGHT        = 72
	KEYLABELFONTSIZE = 7

def sceneWidth(keys):
	return CONST.KEYWIDTH * ceil(keys * 7.0 / 12.0)

class KeyLabel(QGraphicsTextItem):
	def __init__(self, parent = None):
		super().__init__(parent)
		self.setAcceptedMouseButtons(Qt.NoButton)
		self.setRotation(self.rotation() + 270)

	def boundingRect(self):
		return self.mapRectFromScene(self.parentItem().rect());

class PianoScene(QGraphicsScene):
	noteOn  = pyqtSignal(int, int, arguments=['note', 'vel'])
	noteOff = pyqtSignal(int, int, arguments=['note', 'vel'])

	def __init__(self, baseOctave, numKeys, startKey, keyPressedColor = QColor(), parent = None):
		super().__init__(QRectF(0, 0, sceneWidth(numKeys), CONST.KEYHEIGHT), parent)

		self.m_baseOctave      = baseOctave
		self.m_numKeys         = numKeys
		self.m_startKey        = startKey
		self.m_keyPressedColor = keyPressedColor
		self.m_minNote         = 0
		self.m_maxNote         = 127
		self.m_transpose       = 0
		self.m_showLabels      = False
		self.m_useFlats        = False
		self.m_rawkbd          = False
		self.m_keyboardEnabled = True
		self.m_mouseEnabled    = True
		self.m_touchEnabled    = False
		self.m_mousePressed    = False
		self.m_velocity        = 100
		self.m_channel         = 0
		self.m_velocityTint    = True
		self.m_handler         = None
		self.m_keybdMap        = None
		self.m_keys            = {}
		self.m_labels          = {}
		self.m_noteNames       = []
		self.m_names_s         = []
		self.m_names_f         = []

		if self.m_keyPressedColor.isValid():
			hilightBrush = self.m_keyPressedColor
		else:
			hilightBrush = QApplication.palette().highlight()

		lblFont = QApplication.font()
		lblFont.setPointSize(CONST.KEYLABELFONTSIZE)
		upperLimit = self.m_numKeys + self.m_startKey

		adj = self.m_startKey % 12
		if adj >= 5: adj += 1

		for i in range(self.m_startKey, upperLimit):
			ocs = i // 12 * 7

			j = i % 12
			if j >= 5: j += 1

			if (j % 2) == 0:
				x = (ocs + floor((j - adj) / 2.0)) * CONST.KEYWIDTH
				key = PianoKey(QRectF(x, 0, CONST.KEYWIDTH, CONST.KEYHEIGHT), False, i)
				lbl = KeyLabel(key)
				lbl.setDefaultTextColor(Qt.black)
				lbl.setPos(x, CONST.KEYHEIGHT)
			else:
				x = (ocs + floor((j - adj) / 2.0)) * CONST.KEYWIDTH + CONST.KEYWIDTH * 6//10 + 1
				key = PianoKey(QRectF(x, 0, CONST.KEYWIDTH * 8//10 - 1, CONST.KEYHEIGHT * 6//10), True, i)
				key.setZValue(1)
				lbl = KeyLabel(key)
				lbl.setDefaultTextColor(Qt.white)
				lbl.setPos(x - 3, CONST.KEYHEIGHT * 6//10 - 3)

			key.setAcceptTouchEvents(True)

			if self.m_keyPressedColor.isValid():
				key.setPressedBrush(hilightBrush)

			self.m_keys[i] = key
			self.addItem(key)

			lbl.setFont(lblFont)
			self.m_labels[i] = lbl
		self.hideOrShowKeys()
		self.retranslate()

	def getKeyboardMap    (self): return self.m_keybdMap
	def getPianoHandler   (self): return self.m_handler
	def getKeyPressedColor(self): return self.m_keyPressedColor
	def getMinNote        (self): return self.m_minNote
	def getMaxNote        (self): return self.m_maxNote
	def getTranspose      (self): return self.m_transpose
	def showLabels        (self): return self.m_showLabels
	def useFlats          (self): return self.m_useFlats
	def isKeyboardEnabled (self): return self.m_keyboardEnabled
	def isMouseEnabled    (self): return self.m_mouseEnabled
	def isTouchEnabled    (self): return self.m_touchEnabled
	def velocityTint      (self): return self.m_velocityTint
	def baseOctave        (self): return self.m_baseOctave
	def numKeys           (self): return self.m_numKeys
	def startKey          (self): return self.m_startKey
	def getRawKeyboardMode(self): return self.m_rawkbd
	def getChannel        (self): return self.m_channel
	def noteNames         (self): return self.m_names_s
	def getVelocity       (self): return self.m_velocity
	def setKeyboardMap    (self, map     ): self.m_keybdMap     = map
	def setPianoHandler   (self, handler ): self.m_handler      = handler
	def setVelocityTint   (self, enable  ): self.m_velocityTint = enable
	def setVelocity       (self, velocity): self.m_velocity     = velocity
	def setChannel        (self, channel ): self.m_channel      = channel

	def sizeHint(self):
		return QSize(sceneWidth(self.m_numKeys), CONST.KEYHEIGHT)

	def showKeyOn(self, key, vel):
		if vel >= 0:
			if self.m_keyPressedColor.isValid():
				if self.m_velocityTint and vel >= 0:
					key.setPressedBrush(QBrush(self.m_keyPressedColor.lighter(200 - vel)))
				else:
					key.setPressedBrush(QBrush(self.m_keyPressedColor))
			else:
				self.setColorFromPolicy(key, vel)
		key.setPressed(True)

	def showKeyOff(self, key, int):
		key.setPressed(False)

	def showNoteOn(self, note, vel = -1):
		n = note - self.m_baseOctave * 12 - self.m_transpose
		if (note >= self.m_minNote) and (note <= self.m_maxNote) and n in self.m_keys:
			self.showKeyOn(self.m_keys[n], vel)

	def showNoteOff(self, note, vel = -1):
		n = note - self.m_baseOctave * 12 - self.m_transpose
		if (note >= self.m_minNote) and (note <= self.m_maxNote) and n in self.m_keys:
			self.showKeyOff(self.m_keys[n], vel)

	def triggerNoteOn(self, note, vel):
		n = self.m_baseOctave * 12 + note + self.m_transpose
		if (n >= self.m_minNote) and (n <= self.m_maxNote):
			if self.m_handler is not None:
				self.m_handler.noteOn(n, vel)
			else:
				self.noteOn.emit(n, vel)

	def triggerNoteOff(self, note, vel):
		n = self.m_baseOctave * 12 + note + self.m_transpose
		if (n >= self.m_minNote) and (n <= self.m_maxNote):
			if self.m_handler is not None:
				self.m_handler.noteOff(n, vel)
			else:
				self.noteOff.emit(n, vel)

	def setColorFromPolicy(self, key, vel):
		c = QApplication.palette().highlight().color()
		if self.m_velocityTint and vel >= 0:
			key.setPressedBrush(QBrush(c.lighter(200 - vel)))
		else:
			key.setPressedBrush(QBrush(c))

	def _keyOn(self, key, pressure = None):
		vel = self.m_velocity
		if pressure is not None:
			vel *= pressure

		self.triggerNoteOn(key.getNote(), vel)
		self.showKeyOn(key, vel)

	def keyOn(self, note):
		if note in self.m_keys:
			self._keyOn(self.m_keys[note])
		else:
			self.triggerNoteOn(note, self.m_velocity)

	def _keyOff(self, key, pressure = None):
		vel = self.m_velocity
		if pressure is not None:
			vel *= pressure
		self.triggerNoteOff(key.getNote(), vel)
		self.showKeyOff(key, vel)

	def keyOff(self, note):
		if note in self.m_keys:
			self._keyOff(self.m_keys[note])
		else:
			self.triggerNoteOff(note, self.m_velocity)

	def getKeyForPos(self, p):
		for itm in self.items(p, Qt.IntersectsItemShape, Qt.DescendingOrder):
			if isinstance(itm, PianoKey):
				return itm
		return None

	def mouseMoveEvent(self, mouseEvent):
		if self.m_mouseEnabled and mouseEvent.source() == Qt.MouseEventNotSynthesized:
			if self.m_mousePressed:
				key = self.getKeyForPos(mouseEvent.scenePos())
				lastkey = self.getKeyForPos(mouseEvent.lastScenePos())
				if (lastkey is not None) and (lastkey != key) and lastkey.isPressed():
					self._keyOff(lastkey)
				if (key is not None) and not key.isPressed():
					self._keyOn(key)
				mouseEvent.accept()

	def mousePressEvent(self, mouseEvent):
		if self.m_mouseEnabled and mouseEvent.source() == Qt.MouseEventNotSynthesized:
			key = self.getKeyForPos(mouseEvent.scenePos())
			if key is not None and not key.isPressed():
				self._keyOn(key)
				self.m_mousePressed = True
				mouseEvent.accept()

	def mouseReleaseEvent(self, mouseEvent):
		if self.m_mouseEnabled and mouseEvent.source() == Qt.MouseEventNotSynthesized:
			self.m_mousePressed = False
			key = self.getKeyForPos(mouseEvent.scenePos())
			if key is not None and key.isPressed():
				self._keyOff(key)
				mouseEvent.accept()

	def getNoteFromKey(self, key):
		if self.m_keybdMap is not None:
			return self.m_keybdMap.get(key, -1)
		return -1

	def getPianoKey(self, key):
		note = self.getNoteFromKey(key)
		if note in self.m_keys:
			return self.m_keys[note]
		return None

	def keyPressEvent(self, keyEvent):
		if self.m_keyboardEnabled:
			if not self.m_rawkbd and not keyEvent.isAutoRepeat(): # ignore auto-repeats
				note = self.getNoteFromKey(keyEvent.key())
				if note > -1:
					self.keyOn(note)
			keyEvent.accept()
			return
		keyEvent.ignore()

	def keyReleaseEvent(self, keyEvent):
		if self.m_keyboardEnabled:
			if not self.m_rawkbd and not keyEvent.isAutoRepeat(): # ignore auto-repeats
				note = self.getNoteFromKey(keyEvent.key())
				if note > -1:
					self.keyOff(note)
			keyEvent.accept()
			return
		keyEvent.ignore()

	def event(self, event):
		if self.m_touchEnabled:
			t = event.type()
			if (t == QEvent.TouchBegin or t == QEvent.TouchEnd or t == QEvent.TouchUpdate):
				for touchPoint in event.touchPoints():
					if touchPoint.state() == Qt.TouchPointReleased:
						key = self.getKeyForPos(touchPoint.scenePos())
						if key is not None and key.isPressed():
							self._keyOff(key, touchPoint.pressure())
					elif touchPoint.state() == Qt.TouchPointPressed:
						key = self.getKeyForPos(touchPoint.scenePos())
						if key is not None and not key.isPressed():
							self._keyOn(key, touchPoint.pressure())
							key.ensureVisible()
					elif touchPoint.state() == Qt.TouchPointMoved:
						key = self.getKeyForPos(touchPoint.scenePos())
						lastkey = self.getKeyForPos(touchPoint.lastScenePos())
						if (lastkey is not None) and (lastkey != key) and lastkey.isPressed():
							self._keyOff(lastkey, touchPoint.pressure())
						if (key is not None) and not key.isPressed():
							self._keyOn(key, touchPoint.pressure())
				#qDebug() << "accepted event: " << event
				event.accept()
				return True

		#qDebug() << "unprocessed event: " << event
		return super().event(event)

	def allKeysOff(self):
		for key in self.m_keys.values():
			key.setPressed(False)

	def setKeyPressedColor(self, color):
		if color.isValid() and (color != self.m_keyPressedColor):
			self.m_keyPressedColor = color
			hilightBrush = QBrush(self.m_keyPressedColor)
			for key in self.m_keys.values():
				key.setPressedBrush(hilightBrush)

	def resetKeyPressedColor(self):
		if self.m_keyPressedColor.isValid():
			color = self.m_keyPressedColor
		else:
			color = QApplication.palette().highlight()

		hilightBrush = QBrush(color)

		for key in self.m_keys.values():
			key.setPressedBrush(hilightBrush)

	def hideOrShowKeys(self):
		for key in self.m_keys.values():
			n = self.m_baseOctave * 12 + key.getNote() + self.m_transpose
			key.setVisible(self.m_minNote <= n <= self.m_maxNote)

	def setMinNote(self, note):
		if self.m_minNote != note:
			self.m_minNote = note
			self.hideOrShowKeys()

	def setMaxNote(self, note):
		if self.m_maxNote != note:
			self.m_maxNote = note
			self.hideOrShowKeys()

	def setBaseOctave(self, base):
		if self.m_baseOctave != base:
			self.m_baseOctave = base
			self.hideOrShowKeys()
			self.refreshLabels()

	def noteName(self, note):
		num = (note + self.m_transpose + 12) % 12
		adj =  2 if (note + self.m_transpose < 0) else 1
		oct = self.m_baseOctave + ((note + self.m_transpose) / 12) - adj

		if not self.m_noteNames:
			name = ""
			if self.m_names_f and self.m_names_s:
				if self.m_useFlats:
					name = self.m_names_f[num]
				else:
					name = self.m_names_s[num]
			return "{}<span style='vertical-align:sub;'>{}</span>".format(name, oct)
		else:
			noteIndex = note + self.m_transpose + 12 * self.m_baseOctave
			return "<span style='font-size:5pt;'>{}</span>".format(self.m_noteNames[noteIndex])

	def refreshLabels(self):
		for lbl in self.m_labels.values():
			key = lbl.parentItem()
			if isinstance(key, PianoKey):
				lbl.setHtml(self.noteName(key.getNote()))
				lbl.setVisible(self.m_showLabels)

	def refreshKeys(self):
		for key in self.m_keys.values():
			key.setPressed(False)

	def setShowLabels(self, show):
		if self.m_showLabels != show:
			self.m_showLabels = show
			self.refreshLabels()

	def setUseFlats(self, use):
		if self.m_useFlats != use:
			self.m_useFlats = use
			self.refreshLabels()

	def setTranspose(self, transpose):
		if self.m_transpose != transpose and transpose > -12 and transpose < 12:
			self.m_transpose = transpose
			self.hideOrShowKeys()
			self.refreshLabels()

	def setRawKeyboardMode(self, b):
		if self.m_rawkbd != b:
			self.m_rawkbd = b

	def useCustomNoteNames(self, names):
		self.m_noteNames = names
		self.refreshLabels()

	def useStandardNoteNames(self):
		self.m_noteNames.clear()
		self.refreshLabels()

	def setKeyboardEnabled(self, enable):
		if enable != self.m_keyboardEnabled:
			self.m_keyboardEnabled = enable

	def setMouseEnabled(self, enable):
		if enable != self.m_mouseEnabled:
			self.m_mouseEnabled = enable

	def setTouchEnabled(self, enable):
		if enable != self.m_touchEnabled:
			self.m_touchEnabled = enable

	def retranslate(self):
		self.m_names_s = ["C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯", "A", "A♯", "B"]
		self.m_names_f = ["C", "D♭", "D", "E♭", "E", "F", "G♭", "G", "A♭", "A", "B♭", "B"]
		self.refreshLabels()
