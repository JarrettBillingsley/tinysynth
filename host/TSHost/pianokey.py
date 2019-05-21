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

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import *

blackBrush = QBrush(Qt.black)
whiteBrush = QBrush(Qt.white)

class PianoKey(QGraphicsRectItem):
	def __init__(self, parent = None):
		super().__init__(parent)
		self.m_pressed = False

	def __init__(self, rect, brushOrBlack, note, parent = None):
		super().__init__(rect, parent)
		self.m_pressed = False
		self.m_note = note

		global blackBrush, whiteBrush

		if isinstance(brushOrBlack, QBrush):
			self.m_brush = brushOrBlack
			self.m_black = (brushOrBlack is blackBrush)
		else:
			self.m_brush = blackBrush if brushOrBlack else whiteBrush
			self.m_black = brushOrBlack

		self.m_selectedBrush = QBrush()
		self.setAcceptedMouseButtons(Qt.NoButton)

	def setPressed(self, p):
		if p != self.m_pressed:
			self.m_pressed = p
			self.update()

	def isPressed(self):
		return self.m_pressed

	def setBrush(self, b):
		self.m_brush = b

	def setPressedBrush(self, b):
		self.m_selectedBrush = b

	def resetBrush(self):
		global blackBrush, whiteBrush
		if self.m_black:
			self.m_brush = blackBrush
		else:
			self.m_brush = whiteBrush

	def getNote(self):
		return self.m_note

	def getDegree(self):
		return self.m_note % 12

	def getType(self):
		return 1 if self.m_black else 0

	blackPen = QPen(Qt.black, 1)
	grayPen = QPen(QBrush(Qt.gray), 1, Qt.SolidLine,  Qt.RoundCap, Qt.RoundJoin)

	def paint(self, painter, opt, widget):
		if self.m_pressed:
			if self.m_selectedBrush.style() != Qt.NoBrush:
				painter.setBrush(self.m_selectedBrush)
			else:
				painter.setBrush(QApplication.palette().highlight())
		else:
			painter.setBrush(self.m_brush)

		r = self.rect()
		painter.setPen(PianoKey.blackPen)
		painter.drawRoundedRect(r, 1, 1)
		painter.setPen(PianoKey.grayPen)
		painter.drawPolyline(
			 QPointF(r.left()  + 1.5, r.bottom() - 1),
			 QPointF(r.right() - 1,   r.bottom() - 1),
			 QPointF(r.right() - 1,   r.top()    + 1),
		)