
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

	def __init__(self, parent = None, baseOctave = None, numKeys = None, startKey = None):
		super().__init__(parent)
		self.m_rotation = 0
		self.m_scene = None
		self.m_rawMap = None
		self.initialize()

		# TODO
		self.m_defaultMap = None
		self.m_defaultRawMap = None

		if baseOctave is None: baseOctave = CONST.DEFAULTBASEOCTAVE
		if numKeys is None:    numKeys = CONST.DEFAULTNUMBEROFKEYS
		if startKey is None:   startKey = CONST.DEFAULTSTARTINGKEY

		self.initScene(baseOctave, numKeys, startKey)

	def __DTOR__(self):
		self.m_scene.setRawKeyboardMode(False)
		setRawKeyboardMap(None)

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
		return
		# Default translated Keyboard Map
		self.m_defaultMap.insert(Qt.Key_Z, 12)
		self.m_defaultMap.insert(Qt.Key_S, 13)
		self.m_defaultMap.insert(Qt.Key_X, 14)
		self.m_defaultMap.insert(Qt.Key_D, 15)
		self.m_defaultMap.insert(Qt.Key_C, 16)
		self.m_defaultMap.insert(Qt.Key_V, 17)
		self.m_defaultMap.insert(Qt.Key_G, 18)
		self.m_defaultMap.insert(Qt.Key_B, 19)
		self.m_defaultMap.insert(Qt.Key_H, 20)
		self.m_defaultMap.insert(Qt.Key_N, 21)
		self.m_defaultMap.insert(Qt.Key_J, 22)
		self.m_defaultMap.insert(Qt.Key_M, 23)
		self.m_defaultMap.insert(Qt.Key_Q, 24)
		self.m_defaultMap.insert(Qt.Key_2, 25)
		self.m_defaultMap.insert(Qt.Key_W, 26)
		self.m_defaultMap.insert(Qt.Key_3, 27)
		self.m_defaultMap.insert(Qt.Key_E, 28)
		self.m_defaultMap.insert(Qt.Key_R, 29)
		self.m_defaultMap.insert(Qt.Key_5, 30)
		self.m_defaultMap.insert(Qt.Key_T, 31)
		self.m_defaultMap.insert(Qt.Key_6, 32)
		self.m_defaultMap.insert(Qt.Key_Y, 33)
		self.m_defaultMap.insert(Qt.Key_7, 34)
		self.m_defaultMap.insert(Qt.Key_U, 35)
		self.m_defaultMap.insert(Qt.Key_I, 36)
		self.m_defaultMap.insert(Qt.Key_9, 37)
		self.m_defaultMap.insert(Qt.Key_O, 38)
		self.m_defaultMap.insert(Qt.Key_0, 39)
		self.m_defaultMap.insert(Qt.Key_P, 40)

		# Default Raw Keyboard Map
	#if defined(Q_OS_LINUX)
		self.m_defaultRawMap.insert(94, 11)
		self.m_defaultRawMap.insert(52, 12)
		self.m_defaultRawMap.insert(39, 13)
		self.m_defaultRawMap.insert(53, 14)
		self.m_defaultRawMap.insert(40, 15)
		self.m_defaultRawMap.insert(54, 16)
		self.m_defaultRawMap.insert(55, 17)
		self.m_defaultRawMap.insert(42, 18)
		self.m_defaultRawMap.insert(56, 19)
		self.m_defaultRawMap.insert(43, 20)
		self.m_defaultRawMap.insert(57, 21)
		self.m_defaultRawMap.insert(44, 22)
		self.m_defaultRawMap.insert(58, 23)
		self.m_defaultRawMap.insert(59, 24)
		self.m_defaultRawMap.insert(46, 25)
		self.m_defaultRawMap.insert(60, 26)
		self.m_defaultRawMap.insert(47, 27)
		self.m_defaultRawMap.insert(61, 28)

		self.m_defaultRawMap.insert(24, 29)
		self.m_defaultRawMap.insert(11, 30)
		self.m_defaultRawMap.insert(25, 31)
		self.m_defaultRawMap.insert(12, 32)
		self.m_defaultRawMap.insert(26, 33)
		self.m_defaultRawMap.insert(13, 34)
		self.m_defaultRawMap.insert(27, 35)
		self.m_defaultRawMap.insert(28, 36)
		self.m_defaultRawMap.insert(15, 37)
		self.m_defaultRawMap.insert(29, 38)
		self.m_defaultRawMap.insert(16, 39)
		self.m_defaultRawMap.insert(30, 40)
		self.m_defaultRawMap.insert(31, 41)
		self.m_defaultRawMap.insert(18, 42)
		self.m_defaultRawMap.insert(32, 43)
		self.m_defaultRawMap.insert(19, 44)
		self.m_defaultRawMap.insert(33, 45)
		self.m_defaultRawMap.insert(20, 46)
		self.m_defaultRawMap.insert(34, 47)
		self.m_defaultRawMap.insert(35, 48)
	#endif

	#if defined(Q_OS_WIN)
		self.m_defaultRawMap.insert(86, 11)
		self.m_defaultRawMap.insert(44, 12)
		self.m_defaultRawMap.insert(31, 13)
		self.m_defaultRawMap.insert(45, 14)
		self.m_defaultRawMap.insert(32, 15)
		self.m_defaultRawMap.insert(46, 16)
		self.m_defaultRawMap.insert(47, 17)
		self.m_defaultRawMap.insert(34, 18)
		self.m_defaultRawMap.insert(48, 19)
		self.m_defaultRawMap.insert(35, 20)
		self.m_defaultRawMap.insert(49, 21)
		self.m_defaultRawMap.insert(36, 22)
		self.m_defaultRawMap.insert(50, 23)
		self.m_defaultRawMap.insert(51, 24)
		self.m_defaultRawMap.insert(38, 25)
		self.m_defaultRawMap.insert(52, 26)
		self.m_defaultRawMap.insert(39, 27)
		self.m_defaultRawMap.insert(53, 28)

		self.m_defaultRawMap.insert(16, 29)
		self.m_defaultRawMap.insert(3, 30)
		self.m_defaultRawMap.insert(17, 31)
		self.m_defaultRawMap.insert(4, 32)
		self.m_defaultRawMap.insert(18, 33)
		self.m_defaultRawMap.insert(5, 34)
		self.m_defaultRawMap.insert(19, 35)
		self.m_defaultRawMap.insert(20, 36)
		self.m_defaultRawMap.insert(7, 37)
		self.m_defaultRawMap.insert(21, 38)
		self.m_defaultRawMap.insert(8, 39)
		self.m_defaultRawMap.insert(22, 40)
		self.m_defaultRawMap.insert(23, 41)
		self.m_defaultRawMap.insert(10, 42)
		self.m_defaultRawMap.insert(24, 43)
		self.m_defaultRawMap.insert(11, 44)
		self.m_defaultRawMap.insert(25, 45)
		self.m_defaultRawMap.insert(12, 46)
		self.m_defaultRawMap.insert(26, 47)
		self.m_defaultRawMap.insert(27, 48)
	#endif

	#if defined(Q_OS_MAC)
		self.m_defaultRawMap.insert(50, 11)
		self.m_defaultRawMap.insert(6, 12)
		self.m_defaultRawMap.insert(1, 13)
		self.m_defaultRawMap.insert(7, 14)
		self.m_defaultRawMap.insert(2, 15)
		self.m_defaultRawMap.insert(8, 16)
		self.m_defaultRawMap.insert(9, 17)
		self.m_defaultRawMap.insert(5, 18)
		self.m_defaultRawMap.insert(11, 19)
		self.m_defaultRawMap.insert(4, 20)
		self.m_defaultRawMap.insert(45, 21)
		self.m_defaultRawMap.insert(38, 22)
		self.m_defaultRawMap.insert(46, 23)
		self.m_defaultRawMap.insert(43, 24)
		self.m_defaultRawMap.insert(37, 25)
		self.m_defaultRawMap.insert(47, 26)
		self.m_defaultRawMap.insert(41, 27)
		self.m_defaultRawMap.insert(44, 28)

		self.m_defaultRawMap.insert(12, 29)
		self.m_defaultRawMap.insert(19, 30)
		self.m_defaultRawMap.insert(13, 31)
		self.m_defaultRawMap.insert(20, 32)
		self.m_defaultRawMap.insert(14, 33)
		self.m_defaultRawMap.insert(21, 34)
		self.m_defaultRawMap.insert(15, 35)
		self.m_defaultRawMap.insert(17, 36)
		self.m_defaultRawMap.insert(22, 37)
		self.m_defaultRawMap.insert(16, 38)
		self.m_defaultRawMap.insert(26, 39)
		self.m_defaultRawMap.insert(32, 40)
		self.m_defaultRawMap.insert(34, 41)
		self.m_defaultRawMap.insert(25, 42)
		self.m_defaultRawMap.insert(31, 43)
		self.m_defaultRawMap.insert(29, 44)
		self.m_defaultRawMap.insert(35, 45)
		self.m_defaultRawMap.insert(27, 46)
		self.m_defaultRawMap.insert(33, 47)
		self.m_defaultRawMap.insert(30, 48)
	#endif
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
