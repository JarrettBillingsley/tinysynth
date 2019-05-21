
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import *

class ADSRDisplay(QWidget):

	def __init__(self, parent=None):
		super().__init__(parent)
		self.sliders = None

		pen = QPen(QColor(255, 255, 255))
		pen.setJoinStyle(Qt.RoundJoin)
		pen.setCapStyle(Qt.RoundCap)
		pen.setWidth(2)
		self.pen = pen

	def setSliders(self, sliders):
		self.sliders = sliders

	def paintEvent(self, event):
		Att, Dec, Sus, Rel = self._getSliderValues()

		p = QPainter(self)
		p.setRenderHints(QPainter.Antialiasing, True)
		p.setPen(self.pen)

		w, h = self.width() - 6, self.height() - 6

		x1 = 0
		x2 = 0.3 * Att * w
		x3 = x2 + (0.3 * Dec * w)
		x4 = x3 + (0.1 * w)
		x5 = x4 + (0.3 * Rel * w)

		y1 = h
		y2 = 0
		y3 = (1 - Sus) * h

		points = [
			QPoint(x1 + 3, y1 + 3),
			QPoint(x2 + 3, y2 + 3),
			QPoint(x3 + 3, y3 + 3),
			QPoint(x4 + 3, y3 + 3),
			QPoint(x5 + 3, y1 + 3),
		]

		p.drawPolyline(QPolygon(points))

	def _getSliderValues(self):
		return tuple((s.value() - s.minimum()) / (s.maximum() - s.minimum()) for s in self.sliders)