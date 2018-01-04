## GUI for brewing 
#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
#from PyQt5.QtOpenGL import *
#from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
#import matplotlib.pyplot as plt
import pyqtgraph as qtplt
import random
import PID
import time
import collections
import numpy as np
from time import strftime, gmtime

class Main(QMainWindow):

	def __init__(self, parent=None):
		self.setval = 65
		self.procval = 60
		super(Main,self).__init__(parent)
		self.other_window = None
		self.initMain()

	def initMain(self):
		# Layout settings
		QToolTip.setFont(QFont('SansSerif',10))
		self.statusBar().showMessage('Ready')
		self.setToolTip('This is a <b>Mesh regulator</b> widget')
		self.menu()
		self.setGeometry(300, 300, 460, 320)
		wid = QWidget(self)
		self.setCentralWidget(wid)
		self.windowLayout = QHBoxLayout()
		wid.setLayout(self.windowLayout)

		self.display(self.setval)
		self.buttons(self.setval)
		self.center()
		self.setWindowTitle('GUI')
		self.setWindowIcon(QIcon('web.png'))

		# PID skjeten
		self.P = 2
		self.I = 0.01
		self.D = 0
		self.i = 0
		# Use pid library to calculate output
		self.pid = PID.PID(self.P, self.I, self.D) # Start PID funksjonen
		self.pid.clear()
		# Config PID
		self.pid.setPoint = self.setval
		self.pid.setSampleTime(0.01)
		self.pid.setOutputLim(0.01,100)
		self.pid.setWindup(100)
		self.WindowSize = 5000
		# PID Timer
		self.timer = QTimer()
		self.timer.setTimerType(Qt.PreciseTimer)
		self.timer.timeout.connect(self.on_timer)
		self.timer.start(100)

		# Process plot
		# Init data
		self._interval = int(60*1000)
		self._bufsize = int(60)
		self.databuffer = collections.deque([0.0]*self._bufsize, self._bufsize)
		self.temp_list = np.zeros(self._bufsize, dtype=np.float)
		self.setpoint_list = [] # Not being used
		self.time_list = np.linspace(-60, 0.0, self._bufsize)
		self.startime = time.time()
		
		# Pyqtgraph
		self.procPlt = qtplt.PlotWidget()
		self.procPlt.setEnabled(True)
		self.procPlt.setGeometry(QRect(20,40,100,100))

		self.windowLayout.addWidget(self.procPlt)
		self.procPlt.resize(230,150)
		self.trend = self.procPlt.plot(self.time_list, self.temp_list,pen=(255,0,0))
		# Plot Timer
		self.pltTimer = QTimer()
		self.pltTimer.timeout.connect(self.updateplot)
		self.pltTimer.start(1000)

		self.show()

	def on_timer(self):
		# ###### RAndom process value for testing ############
		# if self.i>5:
		# 	self.procval = rand.randProcVal()
		# 	self.i = 0
		# self.i += 1
		# ####################################################

		# Update PID
		self.winStartTime = time.time()
		self.temp = self.procval

		self.pid.pid_update(self.temp)

		# Turn Relay on/off
		if(time.time() - self.winStartTime > self.WindowSize):
		        self.winStartTime += self.WindowSize

		if(self.pid.output > time.time() - self.winStartTime):
		        self.logic = 1
		        self.pidValue.setText(str(self.pid.output))
		else:
		        self.logic = 0
		        self.pidValue.setText(str(0))

		with open("mesh_temp.csv","a") as log:
		        log.write("{0},{1}\n".format(strftime("%Y-%m-%d %H:%M:%S"),str(self.temp)))
		self.procValue.setText(str(self.procval))

	def updateplot(self):
		self.databuffer.append(self.procval)
		self.temp_list[:] = self.databuffer
		self.trend.setData(self.time_list,self.temp_list)

	def closeEvent(self,event):
		reply = QMessageBox.question(self, 'Message',
			"Are you sure to quit?", QMessageBox.Yes |
			QMessageBox.No, QMessageBox.No)

		if reply == QMessageBox.Yes:
			event.accept()
		else:
			event.ignore()

	def menu(self):

		exitAction = QAction(QIcon('exit.png'),'&Exit',self)
		exitAction.setShortcut('Ctrl+Q')
		exitAction.setStatusTip('Exit App')
		exitAction.triggered.connect(qApp.quit)


		menubar = self.menuBar()
		fileMenu = menubar.addMenu('&File')
		fileMenu.addAction(exitAction)
	def display(self,setval):
		font = QFont()
		font.setFamily("Arial")
		font.setPointSize(30)
		
		# Process value
		self.procValue = QTextEdit(self)
		self.procValue.setGeometry(QRect(370, 70, 60, 60))
		self.procValue.setObjectName("procValue")
		self.procValue.setFont(font)
		#self.windowLayout.addWidget(self.procValue)
		# Setpoint
		self.setValue = QTextEdit(self)
		self.setValue.setGeometry(QRect(370, 170, 60, 60))
		self.setValue.setObjectName("setValue")
		self.setValue.setText(str(self.setval))
		self.setValue.setFont(font)
		#self.windowLayout.addWidget(self.setValue)

		self.pidValue = QTextEdit(self)
		self.pidValue.setGeometry(QRect(170, 170, 60, 60))
		self.pidValue.setObjectName("Value")
		return self.setval



	def buttons(self,setval):
		#btn = QPushButton('Num Pad',self)
		#btn.setToolTip('This is a <b>Push Button</b> widget')
		#btn.resize(btn.sizeHint())
		#self.windowLayout.addWidget(btn)
		#btn.move(270,20)
		#btn.clicked.connect(self.newWinOpen)

		qbtn = QPushButton('Quit',self)
		qbtn.resize(qbtn.sizeHint())
		qbtn.move(360,20)
		qbtn.clicked.connect(QCoreApplication.instance().quit)

		btnOn = QPushButton('+',self)
		btnOn.setGeometry(QRect(280, 70, 71, 61))
		btnOn.setObjectName("btnOn")
		#self.windowLayout.addWidget(btnOn)
		
		btnOn.clicked.connect(lambda: self.addValue(self.setval))

		btnOff = QPushButton('-',self)
		btnOff.setGeometry(QRect(280, 170, 71, 61))
		btnOff.setObjectName("btnOff")
		#self.windowLayout.addWidget(btnOff)
		btnOff.clicked.connect(lambda: self.subValue(self.setval))
	def addValue(self,setval):
		self.setval += 1
		self.pid.setPoint = (self.setval)
		self.setValue.setText(str(self.setval))
		return self.setval
	def subValue(self,setval):
		self.setval -= 1
		self.pid.setPoint = (self.setval)
		self.setValue.setText(str(setval))
		return self.setval
	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def newWinOpen(self):
		self.other_window = numpad()
		self.other_window.show()

	def newWinClear(self):
		del self.other_window
		self.other_window = None

class numpad(QWidget):

	def __init__(self, parent=None):
		super().__init__(parent)

		self.initNewWin()

	def initNewWin(self):
		
		self.setGeometry(300, 300, 460, 320)
		self.setWindowTitle('Num Pad')
		self.grid()
		self.center()

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def buttons(self):
		okButton = QPushButton("OK")
		okButton.clicked.connect(self.close)
		cancelButton = QPushButton("Cancel")

		cancelButton.clicked.connect(self.close)

		hbox = QHBoxLayout()
		hbox.addStretch(1)
		hbox.addWidget(okButton)
		hbox.addWidget(cancelButton)

		vbox = QVBoxLayout()
		vbox.addStretch(1)
		vbox.addLayout(hbox)

		self.setLayout(vbox)	

	def grid(self):
		grid = QGridLayout()
		self.setLayout(grid)

		numpad = ['7', '8', '9',
				'4', '5', '6',
				'1', '2', '3',
				'OK','0','Cancel']
		positions = [(i,j) for i in range(4) for j in range(3)]

		for position, numb in zip(positions, numpad):

			if numb == '':
				continue	
			button = QPushButton(numb)
			grid.addWidget(button, *position)



if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = Main()
	sys.exit(app.exec_())
