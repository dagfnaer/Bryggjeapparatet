import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import pyqtgraph as qtplt
import random
import time
import collections
import numpy as np 
from time import strftime, gmtime

import PID


class Brew(QMainWindow):

	def __init__(self, parent=None):
		self.setval = 65			# initial setpoint value
		self.procval = 50			# initial process value

		#super().__init__()
		super(Brew, self).__init__(parent)
		
		self.other_window = None
		self.initMain()

	def initMain(self):
		# initiates application UI
		QToolTip.setFont(QFont('HelveticaNeue', 10))
		self.statusbar = self.statusBar()
		self.statusbar.showMessage('Klar')
		self.setToolTip('Dette er en hjemmelaget meske-regulator')

		self.menu()
		self.pidController()
		#self.processPlot()

		wid = QWidget(self)
		self.setCentralWidget(wid)
		self.windowLayout = QHBoxLayout()
		wid.setLayout(self.windowLayout)

		self.display(self.setval)
		self.buttons(self.setval)

		self.resize(800, 480)
		self.center
		self.setWindowTitle('Bryggjeapparatet')
		self.show()


		#### Process plot
		# initialisation data
		self._interval = int(60*1000)
		self._bufsize = int(60)
		self.databuffer = collections.deque([0.0]*self._bufsize, self._bufsize)
		self.temp_list = np.zeros(self._bufsize, dtype=np.float)
		self.setpoint_list = [] # Not being used
		self.time_list = np.linspace(-60, 0.0, self._bufsize)
		self.startime = time.time()
		
		# pyqtgraph
		self.procPlt = qtplt.PlotWidget()
		self.procPlt.setEnabled(True)
		self.procPlt.setGeometry(QRect(20,20,100,100))

		#self.windowLayout.addWidget(self.procPlt)
		#self.procPlt.resize(230,150)
		self.trend = self.procPlt.plot(self.time_list, self.temp_list,pen=(255,0,0))
		
		# plot timer
		self.pltTimer = QTimer()
		self.pltTimer.timeout.connect(self.updateplot)
		self.pltTimer.start(1000)

	def pidController(self):
		# PID controller

		self.P = 2
		self.I = 1
		self.D = 0
		self.i = 0

		# use PID library to calculate output
		self.pid = PID.PID(self.P, self.I, self.D) # Start PID funksjonen
		self.pid.clear()

		# config PID
		self.pid.setPoint = self.setval
		self.pid.setSampleTime(0.01)
		self.pid.setOutputLim(0.01,100)
		self.pid.setWindup(100)
		self.WindowSize = 5000

		# PID timer
		self.timer = QTimer()
		self.timer.setTimerType(Qt.PreciseTimer)
		self.timer.timeout.connect(self.on_timer)
		self.timer.start(100) 

	def on_timer(self):

		### random process value for testing ###
		if self.i>5:
			self.procval = random.randint(1, 10)
			self.i = 0
		self.i += 1
		########################################

		# update PID
		self.winStartTime = time.time()
		self.temp = self.procval

		self.pid.pid_update(self.temp)

		# turn relay on/off
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
		self.procValue = self.procval	

	def updateplot(self):
		self.databuffer.append(self.procval)
		self.temp_list[:] = self.databuffer
		self.trend.setData(self.time_list,self.temp_list)

	def menu(self):
		# set up menu

		menubar = self.menuBar()
		menubar.setNativeMenuBar(False) 		# for macOS
		fileMenu = menubar.addMenu('Fil')
		viewMenu = menubar.addMenu('Vis')

		brewAct = QAction(QIcon('beer.png'),'&Start brygging', self)
		brewAct.setStatusTip('Brygg øl')

		exitAct = QAction(QIcon('exit.png'), '&Avslutt', self)
		exitAct.setShortcut('Ctrl+Q')
		exitAct.setStatusTip('Avslutt programvare')
		exitAct.triggered.connect(qApp.quit)

		viewStatAct = QAction('Vis statusbar', self, checkable=True)
		viewStatAct.setStatusTip('Vis statusbar')
		viewStatAct.setChecked(True)
		viewStatAct.triggered.connect(self.statusbarToggleMenu)

		viewGraphAct = QAction('Vis temperatur', self, checkable=True)
		viewGraphAct.setStatusTip('Vis temperaturgraf')
		viewGraphAct.setChecked(True)

		fileMenu.addAction(brewAct)
		fileMenu.addAction(exitAct)

		viewMenu.addAction(viewStatAct)
		viewMenu.addAction(viewGraphAct)

	def closeEvent(self,event):
		reply = QMessageBox.question(self, 'Message',
			"Are you sure to quit?", QMessageBox.Yes |
			QMessageBox.No, QMessageBox.No)

		if reply == QMessageBox.Yes:
			event.accept()
		else:
			event.ignore()

	def display(self,setval):
		font = QFont()
		font.setFamily("HelveticaNeue")
		font.setPointSize(30)

		# Process value
		self.procValue = QLabel(self)
		self.procValue.resize(100,50)
		self.procValue.move(10,30)
		self.procValue.setObjectName("procValue")
		self.procValue.setFont(font)
		#self.windowLayout.addWidget(self.procValue)

		# Setpoint
		self.setValue = QLabel("Setpoint", self)
		self.setValue.resize(100,50)
		self.setValue.move(10,100)
		self.setValue.setObjectName("setValue")
		self.setValue.setText(str(self.setval))
		self.setValue.setFont(font)
		#self.windowLayout.addWidget(self.setValue)

		self.pidValue = QLabel(self)
		self.pidValue.resize(100,50)
		self.pidValue.move(10,170)
		self.pidValue.setObjectName("Value")
		self.pidValue.setFont(font)

		return self.setval

	def buttons(self,setval):
		#btn = QPushButton('Num Pad',self)
		#btn.setToolTip('This is a <b>Push Button</b> widget')
		#btn.resize(btn.sizeHint())
		#self.windowLayout.addWidget(btn)
		#btn.move(270,20)
		#btn.clicked.connect(self.newWinOpen)

		#qbtn = QPushButton('Quit',self)
		#qbtn.resize(qbtn.sizeHint())
		#qbtn.move(360,20)
		#qbtn.clicked.connect(QCoreApplication.instance().quit)

		btnOn = QPushButton('+',self)
		btnOn.setGeometry(QRect(280, 70, 65, 65))
		btnOn.setObjectName("btnOn")
		#self.windowLayout.addWidget(btnOn)
		btnOn.clicked.connect(lambda: self.addValue(self.setval))

		btnOff = QPushButton('-',self)
		btnOff.setGeometry(QRect(280, 170, 65, 65))
		btnOff.setObjectName("btnOff")
		#self.windowLayout.addWidget(btnOff)
		btnOff.clicked.connect(lambda: self.subValue(self.setval))

	def statusbarToggleMenu(self, state):
		if state:
			self.statusbar.show()
		else:
			self.statusbar.hide()

	def center(self):
		qr = self.frameGeometry()
		cp = QDesktopWidget().avaiableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

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
		
		self.resize(350, 350)
		self.center
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
    ex = Brew()
    sys.exit(app.exec_())


