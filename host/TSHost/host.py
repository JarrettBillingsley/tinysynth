#! /usr/local/bin/python3

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from TSHost import Ui_MainWindow

class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)

		self.findChild(QWidget, 'widgetKeyboard').scene().setPianoHandler(self)

		self.show()

	def noteOn(self, n, v):
		print("on:", n, v)

	def noteOff(self, n, v):
		print("off:", n, v)


if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = MainWindow()
	sys.exit(app.exec_())
