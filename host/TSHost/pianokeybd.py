# Virtual Piano Widget for Qt4
# Copyright (C) 2008-2018, Pedro Lopez-Cabanillas <plcl@users.sf.net>
# Translated to Python by Jarrett Billingsley

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program; If not, see <http://www.gnu.org/licenses/>.

import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import *

from pianoscene import PianoScene

class CONST:
	DEFAULTNUMBEROFKEYS = 61
	DEFAULTBASEOCTAVE   = 3
	DEFAULTSTARTINGKEY  = 0

class PianoKeybd(QGraphicsView):
#if defined(RAWKBD_SUPPORT)
		# , public RawKbdHandler
#endif

	noteOn  = pyqtSignal(int, int, arguments = ['midiNote', 'vel'])
	noteOff = pyqtSignal(int, int, arguments = ['midiNote', 'vel'])

	# Q_PROPERTY( int baseOctave READ baseOctave WRITE setBaseOctave )
	# Q_PROPERTY( int numKeys READ numKeys WRITE setNumKeys )
	# Q_PROPERTY( int rotation READ getRotation WRITE setRotation )
	# Q_PROPERTY( QColor keyPressedColor READ getKeyPressedColor WRITE setKeyPressedColor )
	# Q_PROPERTY( bool showLabels READ showLabels WRITE setShowLabels )
	# Q_PROPERTY( bool useFlats READ useFlats WRITE setUseFlats )
	# Q_PROPERTY( int transpose READ getTranspose WRITE setTranspose )

	def __init__(self, parent = None, baseOctave = CONST.DEFAULTBASEOCTAVE,
			numKeys = CONST.DEFAULTNUMBEROFKEYS, startKey = CONST.DEFAULTSTARTINGKEY):

		super().__init__(parent)
		self.m_rotation = 0
		self.m_scene = None
		self.m_rawMap = None
		self.m_defaultMap = {}
		self.m_defaultRawMap = {}
		self.initialize()
		self.initScene(baseOctave, numKeys, startKey)

	def setNumKeys(self, numKeys, startKey):
		if numKeys != self.m_scene.numKeys() or startKey != self.m_scene.startKey():
			baseOctave = self.m_scene.baseOctave()
			color = self.m_scene.getKeyPressedColor()
			handler = self.m_scene.getPianoHandler()
			keyMap = self.m_scene.getKeyboardMap()
			keyboardEnabled = self.m_scene.isKeyboardEnabled()
			mouseEnabled = self.m_scene.isMouseEnabled()
			touchEnabled = self.m_scene.isTouchEnabled()

			self.initScene(baseOctave, numKeys, startKey, color)
			self.m_scene.setPianoHandler(handler)
			self.m_scene.setKeyboardMap(keyMap)
			self.m_scene.setKeyboardEnabled(keyboardEnabled)
			self.m_scene.setMouseEnabled(mouseEnabled)
			self.m_scene.setTouchEnabled(touchEnabled)
			self.fitInView(self.m_scene.sceneRect(), Qt.KeepAspectRatio)

	def setRotation(self, r):
		if r != self.m_rotation:
			self.m_rotation = r
			self.resetTransform()
			self.rotate(self.m_rotation)
			self.fitInView(self.m_scene.sceneRect(), Qt.KeepAspectRatio)

	def sizeHint(self):
		return self.mapFromScene(self.sceneRect()).boundingRect().size()

	def baseOctave(self):                return self.m_scene.baseOctave()
	def setBaseOctave(self, baseOctave): self.m_scene.setBaseOctave(baseOctave)
	def numKeys(self):                   return self.m_scene.numKeys()
	def startKey(self):                  return self.m_scene.startKey()
	def getRotation(self):               return self.m_rotation
	def getKeyPressedColor(self):        return self.m_scene.getKeyPressedColor()
	def setKeyPressedColor(self, c):     self.m_scene.setKeyPressedColor(c)
	def showLabels(self):                return self.m_scene.showLabels()
	def setShowLabels(self, show):       self.m_scene.setShowLabels(show)
	def useFlats(self):                  return self.m_scene.useFlats()
	def setUseFlats(self, use):          self.m_scene.setUseFlats(use)
	def getTranspose(self):              return self.m_scene.getTranspose()
	def setTranspose(self, t):           self.m_scene.setTranspose(t)
	def getPianoScene(self):             return self.m_scene
	def setRawKeyboardMap(self, m):      self.m_rawMap = m
	def getRawKeyboardMap(self):         return self.m_rawMap
	def resetRawKeyboardMap(self):       self.m_rawMap = self.m_defaultRawMap
	def resetKeyboardMap(self):          self.m_scene.setKeyboardMap(self.m_defaultMap)

	def initScene(self, base, num, strt, c = QColor()):
		self.m_scene = PianoScene(base, num, strt, c, self)
		self.m_scene.setKeyboardMap(self.m_defaultMap)
		self.m_scene.noteOn.connect(self.noteOn)
		self.m_scene.noteOff.connect(self.noteOff)
		self.setScene(self.m_scene)

	def initialize(self):
		self.setAttribute(Qt.WA_AcceptTouchEvents)
		self.setAttribute(Qt.WA_InputMethodEnabled, False)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setCacheMode(QGraphicsView.CacheBackground)
		self.setViewportUpdateMode(QGraphicsView.MinimalViewportUpdate)
		self.setRenderHints(QPainter.Antialiasing|QPainter.TextAntialiasing|QPainter.SmoothPixmapTransform)
		self.setOptimizationFlag(QGraphicsView.DontClipPainter, True)
		self.setOptimizationFlag(QGraphicsView.DontSavePainterState, True)
		self.setOptimizationFlag(QGraphicsView.DontAdjustForAntialiasing, True)
		self.setBackgroundBrush(QApplication.palette().window())
		self.initDefaultMap()

	def resizeEvent(self, event):
		super().resizeEvent(event)
		self.fitInView(self.m_scene.sceneRect(), Qt.KeepAspectRatio)

	def initDefaultMap(self):
		# Default translated Keyboard Map
		self.m_defaultMap[Qt.Key_Z] = 12
		self.m_defaultMap[Qt.Key_S] = 13
		self.m_defaultMap[Qt.Key_X] = 14
		self.m_defaultMap[Qt.Key_D] = 15
		self.m_defaultMap[Qt.Key_C] = 16
		self.m_defaultMap[Qt.Key_V] = 17
		self.m_defaultMap[Qt.Key_G] = 18
		self.m_defaultMap[Qt.Key_B] = 19
		self.m_defaultMap[Qt.Key_H] = 20
		self.m_defaultMap[Qt.Key_N] = 21
		self.m_defaultMap[Qt.Key_J] = 22
		self.m_defaultMap[Qt.Key_M] = 23
		self.m_defaultMap[Qt.Key_Q] = 24
		self.m_defaultMap[Qt.Key_2] = 25
		self.m_defaultMap[Qt.Key_W] = 26
		self.m_defaultMap[Qt.Key_3] = 27
		self.m_defaultMap[Qt.Key_E] = 28
		self.m_defaultMap[Qt.Key_R] = 29
		self.m_defaultMap[Qt.Key_5] = 30
		self.m_defaultMap[Qt.Key_T] = 31
		self.m_defaultMap[Qt.Key_6] = 32
		self.m_defaultMap[Qt.Key_Y] = 33
		self.m_defaultMap[Qt.Key_7] = 34
		self.m_defaultMap[Qt.Key_U] = 35
		self.m_defaultMap[Qt.Key_I] = 36
		self.m_defaultMap[Qt.Key_9] = 37
		self.m_defaultMap[Qt.Key_O] = 38
		self.m_defaultMap[Qt.Key_0] = 39
		self.m_defaultMap[Qt.Key_P] = 40

		# Default Raw Keyboard Map
		if sys.platform == 'win32' or sys.platform == 'cygwin':
			self.m_defaultRawMap[86] = 11
			self.m_defaultRawMap[44] = 12
			self.m_defaultRawMap[31] = 13
			self.m_defaultRawMap[45] = 14
			self.m_defaultRawMap[32] = 15
			self.m_defaultRawMap[46] = 16
			self.m_defaultRawMap[47] = 17
			self.m_defaultRawMap[34] = 18
			self.m_defaultRawMap[48] = 19
			self.m_defaultRawMap[35] = 20
			self.m_defaultRawMap[49] = 21
			self.m_defaultRawMap[36] = 22
			self.m_defaultRawMap[50] = 23
			self.m_defaultRawMap[51] = 24
			self.m_defaultRawMap[38] = 25
			self.m_defaultRawMap[52] = 26
			self.m_defaultRawMap[39] = 27
			self.m_defaultRawMap[53] = 28

			self.m_defaultRawMap[16] = 29
			self.m_defaultRawMap[3] = 30
			self.m_defaultRawMap[17] = 31
			self.m_defaultRawMap[4] = 32
			self.m_defaultRawMap[18] = 33
			self.m_defaultRawMap[5] = 34
			self.m_defaultRawMap[19] = 35
			self.m_defaultRawMap[20] = 36
			self.m_defaultRawMap[7] = 37
			self.m_defaultRawMap[21] = 38
			self.m_defaultRawMap[8] = 39
			self.m_defaultRawMap[22] = 40
			self.m_defaultRawMap[23] = 41
			self.m_defaultRawMap[10] = 42
			self.m_defaultRawMap[24] = 43
			self.m_defaultRawMap[11] = 44
			self.m_defaultRawMap[25] = 45
			self.m_defaultRawMap[12] = 46
			self.m_defaultRawMap[26] = 47
			self.m_defaultRawMap[27] = 48
		elif sys.platform == 'darwin':
			self.m_defaultRawMap[50] = 11
			self.m_defaultRawMap[6] = 12
			self.m_defaultRawMap[1] = 13
			self.m_defaultRawMap[7] = 14
			self.m_defaultRawMap[2] = 15
			self.m_defaultRawMap[8] = 16
			self.m_defaultRawMap[9] = 17
			self.m_defaultRawMap[5] = 18
			self.m_defaultRawMap[11] = 19
			self.m_defaultRawMap[4] = 20
			self.m_defaultRawMap[45] = 21
			self.m_defaultRawMap[38] = 22
			self.m_defaultRawMap[46] = 23
			self.m_defaultRawMap[43] = 24
			self.m_defaultRawMap[37] = 25
			self.m_defaultRawMap[47] = 26
			self.m_defaultRawMap[41] = 27
			self.m_defaultRawMap[44] = 28

			self.m_defaultRawMap[12] = 29
			self.m_defaultRawMap[19] = 30
			self.m_defaultRawMap[13] = 31
			self.m_defaultRawMap[20] = 32
			self.m_defaultRawMap[14] = 33
			self.m_defaultRawMap[21] = 34
			self.m_defaultRawMap[15] = 35
			self.m_defaultRawMap[17] = 36
			self.m_defaultRawMap[22] = 37
			self.m_defaultRawMap[16] = 38
			self.m_defaultRawMap[26] = 39
			self.m_defaultRawMap[32] = 40
			self.m_defaultRawMap[34] = 41
			self.m_defaultRawMap[25] = 42
			self.m_defaultRawMap[31] = 43
			self.m_defaultRawMap[29] = 44
			self.m_defaultRawMap[35] = 45
			self.m_defaultRawMap[27] = 46
			self.m_defaultRawMap[33] = 47
			self.m_defaultRawMap[30] = 48
		else:
			# some linux/freebsd thing?
			self.m_defaultRawMap[94] = 11
			self.m_defaultRawMap[52] = 12
			self.m_defaultRawMap[39] = 13
			self.m_defaultRawMap[53] = 14
			self.m_defaultRawMap[40] = 15
			self.m_defaultRawMap[54] = 16
			self.m_defaultRawMap[55] = 17
			self.m_defaultRawMap[42] = 18
			self.m_defaultRawMap[56] = 19
			self.m_defaultRawMap[43] = 20
			self.m_defaultRawMap[57] = 21
			self.m_defaultRawMap[44] = 22
			self.m_defaultRawMap[58] = 23
			self.m_defaultRawMap[59] = 24
			self.m_defaultRawMap[46] = 25
			self.m_defaultRawMap[60] = 26
			self.m_defaultRawMap[47] = 27
			self.m_defaultRawMap[61] = 28

			self.m_defaultRawMap[24] = 29
			self.m_defaultRawMap[11] = 30
			self.m_defaultRawMap[25] = 31
			self.m_defaultRawMap[12] = 32
			self.m_defaultRawMap[26] = 33
			self.m_defaultRawMap[13] = 34
			self.m_defaultRawMap[27] = 35
			self.m_defaultRawMap[28] = 36
			self.m_defaultRawMap[15] = 37
			self.m_defaultRawMap[29] = 38
			self.m_defaultRawMap[16] = 39
			self.m_defaultRawMap[30] = 40
			self.m_defaultRawMap[31] = 41
			self.m_defaultRawMap[18] = 42
			self.m_defaultRawMap[32] = 43
			self.m_defaultRawMap[19] = 44
			self.m_defaultRawMap[33] = 45
			self.m_defaultRawMap[20] = 46
			self.m_defaultRawMap[34] = 47
			self.m_defaultRawMap[35] = 48

		self.m_rawMap = self.m_defaultRawMap

	#if defined(RAWKBD_SUPPORT)
	# def handleKeyPressed(self, int keycode):
	# {
	# 	if self.m_scene.isKeyboardEnabled() and self.m_rawMap != None and self.m_rawMap.contains(keycode):
	# 		self.m_scene.keyOn(self.m_rawMap.value(keycode))
	# 		return True
	# 	}
	# 	return False
	# }

	# def handleKeyReleased(self, int keycode):
	# {
	# 	if self.m_scene.isKeyboardEnabled() and self.m_rawMap != None and self.m_rawMap.contains(keycode):
	# 		self.m_scene.keyOff(self.m_rawMap.value(keycode))
	# 		return True
	# 	}
	# 	return False
	# }
	#endif
