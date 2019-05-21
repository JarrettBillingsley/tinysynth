# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'TSHost.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(869, 529)
        MainWindow.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.buttonPanic = QtWidgets.QPushButton(self.centralwidget)
        self.buttonPanic.setGeometry(QtCore.QRect(360, 70, 50, 50))
        font = QtGui.QFont()
        font.setFamily(".SF NS Text")
        font.setBold(True)
        font.setItalic(False)
        font.setUnderline(False)
        font.setWeight(75)
        font.setKerning(True)
        self.buttonPanic.setFont(font)
        self.buttonPanic.setAutoFillBackground(False)
        self.buttonPanic.setStyleSheet("QPushButton {\n"
"    margin: 0;\n"
"    border: 3px solid red;\n"
"    border-radius: 25px;\n"
"    color: white;\n"
"    background-color: red;\n"
"}\n"
"QPushButton:hover {\n"
"    border-color: white;\n"
"}\n"
"QPushButton:pressed {\n"
"    color: red;\n"
"    background-color: white;\n"
"}")
        self.buttonPanic.setCheckable(True)
        self.buttonPanic.setDefault(False)
        self.buttonPanic.setFlat(False)
        self.buttonPanic.setObjectName("buttonPanic")
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 160, 80, 90))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.labelMixShiftValue = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelMixShiftValue.sizePolicy().hasHeightForWidth())
        self.labelMixShiftValue.setSizePolicy(sizePolicy)
        self.labelMixShiftValue.setAlignment(QtCore.Qt.AlignCenter)
        self.labelMixShiftValue.setObjectName("labelMixShiftValue")
        self.verticalLayout_3.addWidget(self.labelMixShiftValue)
        self.dialMixShift = QtWidgets.QDial(self.layoutWidget)
        self.dialMixShift.setMinimum(0)
        self.dialMixShift.setMaximum(3)
        self.dialMixShift.setPageStep(1)
        self.dialMixShift.setProperty("value", 3)
        self.dialMixShift.setTracking(True)
        self.dialMixShift.setOrientation(QtCore.Qt.Horizontal)
        self.dialMixShift.setInvertedAppearance(True)
        self.dialMixShift.setInvertedControls(False)
        self.dialMixShift.setWrapping(False)
        self.dialMixShift.setNotchTarget(16.0)
        self.dialMixShift.setNotchesVisible(False)
        self.dialMixShift.setObjectName("dialMixShift")
        self.verticalLayout_3.addWidget(self.dialMixShift)
        self.label_4 = QtWidgets.QLabel(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_3.addWidget(self.label_4)
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setEnabled(True)
        self.frame.setGeometry(QtCore.QRect(10, 10, 411, 50))
        self.frame.setFrameShape(QtWidgets.QFrame.Box)
        self.frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame.setObjectName("frame")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout_3.setContentsMargins(4, 0, 4, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label = QtWidgets.QLabel(self.frame)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.comboSerial = QtWidgets.QComboBox(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboSerial.sizePolicy().hasHeightForWidth())
        self.comboSerial.setSizePolicy(sizePolicy)
        self.comboSerial.setCurrentText("")
        self.comboSerial.setObjectName("comboSerial")
        self.horizontalLayout_3.addWidget(self.comboSerial)
        self.buttonRefresh = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonRefresh.sizePolicy().hasHeightForWidth())
        self.buttonRefresh.setSizePolicy(sizePolicy)
        self.buttonRefresh.setObjectName("buttonRefresh")
        self.horizontalLayout_3.addWidget(self.buttonRefresh)
        self.buttonConnect = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonConnect.sizePolicy().hasHeightForWidth())
        self.buttonConnect.setSizePolicy(sizePolicy)
        self.buttonConnect.setObjectName("buttonConnect")
        self.horizontalLayout_3.addWidget(self.buttonConnect)
        self.checkPolyphonic = QtWidgets.QCheckBox(self.centralwidget)
        self.checkPolyphonic.setGeometry(QtCore.QRect(20, 80, 91, 20))
        self.checkPolyphonic.setCheckable(True)
        self.checkPolyphonic.setObjectName("checkPolyphonic")
        self.widgetChannel = QtWidgets.QWidget(self.centralwidget)
        self.widgetChannel.setGeometry(QtCore.QRect(20, 100, 121, 41))
        self.widgetChannel.setObjectName("widgetChannel")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.widgetChannel)
        self.horizontalLayout_5.setContentsMargins(4, 0, 4, 0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_5 = QtWidgets.QLabel(self.widgetChannel)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_5.addWidget(self.label_5)
        self.spinBox = QtWidgets.QSpinBox(self.widgetChannel)
        self.spinBox.setMinimum(1)
        self.spinBox.setMaximum(8)
        self.spinBox.setObjectName("spinBox")
        self.horizontalLayout_5.addWidget(self.spinBox)
        self.layoutWidget1 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget1.setGeometry(QtCore.QRect(90, 160, 80, 90))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget1)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.labelFineTuneValue = QtWidgets.QLabel(self.layoutWidget1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelFineTuneValue.sizePolicy().hasHeightForWidth())
        self.labelFineTuneValue.setSizePolicy(sizePolicy)
        self.labelFineTuneValue.setAlignment(QtCore.Qt.AlignCenter)
        self.labelFineTuneValue.setObjectName("labelFineTuneValue")
        self.verticalLayout.addWidget(self.labelFineTuneValue)
        self.dialFineTune = QtWidgets.QDial(self.layoutWidget1)
        self.dialFineTune.setMinimum(-63)
        self.dialFineTune.setMaximum(63)
        self.dialFineTune.setTracking(True)
        self.dialFineTune.setInvertedAppearance(False)
        self.dialFineTune.setInvertedControls(False)
        self.dialFineTune.setWrapping(False)
        self.dialFineTune.setNotchTarget(16.0)
        self.dialFineTune.setNotchesVisible(False)
        self.dialFineTune.setObjectName("dialFineTune")
        self.verticalLayout.addWidget(self.dialFineTune)
        self.label_2 = QtWidgets.QLabel(self.layoutWidget1)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.layoutWidget2 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget2.setGeometry(QtCore.QRect(170, 70, 181, 181))
        self.layoutWidget2.setObjectName("layoutWidget2")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.layoutWidget2)
        self.verticalLayout_4.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.displayADSR = ADSRDisplay(self.layoutWidget2)
        self.displayADSR.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(3)
        sizePolicy.setHeightForWidth(self.displayADSR.sizePolicy().hasHeightForWidth())
        self.displayADSR.setSizePolicy(sizePolicy)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(49, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(49, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(49, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(49, 50, 50))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.displayADSR.setPalette(palette)
        self.displayADSR.setAutoFillBackground(True)
        self.displayADSR.setObjectName("displayADSR")
        self.verticalLayout_4.addWidget(self.displayADSR)
        spacerItem = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.sliderAttack = QtWidgets.QSlider(self.layoutWidget2)
        self.sliderAttack.setTracking(True)
        self.sliderAttack.setOrientation(QtCore.Qt.Vertical)
        self.sliderAttack.setObjectName("sliderAttack")
        self.horizontalLayout_4.addWidget(self.sliderAttack)
        self.sliderDecay = QtWidgets.QSlider(self.layoutWidget2)
        self.sliderDecay.setTracking(True)
        self.sliderDecay.setOrientation(QtCore.Qt.Vertical)
        self.sliderDecay.setObjectName("sliderDecay")
        self.horizontalLayout_4.addWidget(self.sliderDecay)
        self.sliderSustain = QtWidgets.QSlider(self.layoutWidget2)
        self.sliderSustain.setMaximum(15)
        self.sliderSustain.setPageStep(5)
        self.sliderSustain.setProperty("value", 15)
        self.sliderSustain.setTracking(True)
        self.sliderSustain.setOrientation(QtCore.Qt.Vertical)
        self.sliderSustain.setObjectName("sliderSustain")
        self.horizontalLayout_4.addWidget(self.sliderSustain)
        self.sliderRelease = QtWidgets.QSlider(self.layoutWidget2)
        self.sliderRelease.setTracking(True)
        self.sliderRelease.setOrientation(QtCore.Qt.Vertical)
        self.sliderRelease.setObjectName("sliderRelease")
        self.horizontalLayout_4.addWidget(self.sliderRelease)
        self.verticalLayout_4.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_3 = QtWidgets.QLabel(self.layoutWidget2)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout_2.addWidget(self.label_3)
        self.label_6 = QtWidgets.QLabel(self.layoutWidget2)
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_2.addWidget(self.label_6)
        self.label_7 = QtWidgets.QLabel(self.layoutWidget2)
        self.label_7.setAlignment(QtCore.Qt.AlignCenter)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_2.addWidget(self.label_7)
        self.label_8 = QtWidgets.QLabel(self.layoutWidget2)
        self.label_8.setAlignment(QtCore.Qt.AlignCenter)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_2.addWidget(self.label_8)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        self.widgetKeyboard = PianoKeybd(self.centralwidget)
        self.widgetKeyboard.setGeometry(QtCore.QRect(10, 260, 851, 221))
        self.widgetKeyboard.setObjectName("widgetKeyboard")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.dialMixShift.valueChanged['int'].connect(self.labelMixShiftValue.setNum)
        self.dialFineTune.valueChanged['int'].connect(self.labelFineTuneValue.setNum)
        self.sliderAttack.valueChanged['int'].connect(self.displayADSR.update)
        self.sliderDecay.valueChanged['int'].connect(self.displayADSR.update)
        self.sliderRelease.valueChanged['int'].connect(self.displayADSR.update)
        self.sliderSustain.valueChanged['int'].connect(self.displayADSR.update)
        self.checkPolyphonic.toggled['bool'].connect(self.widgetChannel.setDisabled)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        MainWindow.setTabOrder(self.buttonConnect, self.dialMixShift)
        MainWindow.setTabOrder(self.dialMixShift, self.dialFineTune)
        MainWindow.setTabOrder(self.dialFineTune, self.sliderAttack)
        MainWindow.setTabOrder(self.sliderAttack, self.sliderDecay)
        MainWindow.setTabOrder(self.sliderDecay, self.sliderSustain)
        MainWindow.setTabOrder(self.sliderSustain, self.sliderRelease)
        MainWindow.setTabOrder(self.sliderRelease, self.spinBox)
        MainWindow.setTabOrder(self.spinBox, self.checkPolyphonic)
        MainWindow.setTabOrder(self.checkPolyphonic, self.buttonPanic)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "TSHost"))
        self.buttonPanic.setText(_translate("MainWindow", "STOP"))
        self.labelMixShiftValue.setText(_translate("MainWindow", "3"))
        self.label_4.setText(_translate("MainWindow", "Mix shift"))
        self.label.setText(_translate("MainWindow", "Port"))
        self.buttonRefresh.setText(_translate("MainWindow", "Refresh"))
        self.buttonConnect.setText(_translate("MainWindow", "Connect"))
        self.checkPolyphonic.setText(_translate("MainWindow", "Polyphonic"))
        self.label_5.setText(_translate("MainWindow", "Channel"))
        self.labelFineTuneValue.setText(_translate("MainWindow", "0"))
        self.label_2.setText(_translate("MainWindow", "Fine tune"))
        self.label_3.setText(_translate("MainWindow", "Att"))
        self.label_6.setText(_translate("MainWindow", "Dec"))
        self.label_7.setText(_translate("MainWindow", "Sus"))
        self.label_8.setText(_translate("MainWindow", "Rel"))


from adsrdisplay import ADSRDisplay
from pianokeybd import PianoKeybd
