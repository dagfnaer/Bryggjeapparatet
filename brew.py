#!/usr/bin/python

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import sys
import random
import time
import collections
import numpy as np
import pyqtgraph as qtplt
from time import strftime, gmtime

from functools import partial
#from globals import *

import PID

#from max6675 import MAX6675

# Inspo:
# https://github.com/mba7/SerialPort-RealTime-Data-Plotter/blob/master/live_monitor.py
# https://github.com/eliben/code-for-blog/blob/master/2009/plotting_data_monitor/plotting_data_monitor.pyw

# cs_pin = 38
# clock_pin = 36
# data_pin = 37
# units = "c"
# thermocouple = MAX6675(cs_pin, clock_pin, data_pin, units)
# print(thermocouple.get())
# thermocouple.cleanup()


class BrewMonitor(QMainWindow):

	def __init__(self, parent=None):
		super(BrewMonitor, self).__init__(parent)

		self.setWindowTitle('Bryggjeapparatet')
		self.resize(800, 480)

		#self.procval = thermocouple.get()

		self.monitor_active = False
		self.gcurveOn = [1]*2
		self.setval = 65			# initial setpoint value
		self.procval = 50			# initial process value
		#self.pid.output = 0			# initial pid value
		self.start_time = 0			# initial time value used in on_timer
		self.time_seconds = 0		# initial timer value

		#self.create_menu()
		self.create_main_frame()
		self.create_menu()
		self.create_status_bar()

		self.btnStart.clicked.connect(self.OnStart)
		self.btnStop.clicked.connect(self.OnStop)
	#---------------------------------------------------


	def create_plot(self):
		"""
		Purpose:	create the temperature plot
		Return:		return the pyqtgraph plot
		"""
		
		## initialisation data
		self._bufsize = int(120)

		self.temp_buffer = collections.deque([0.0]*self._bufsize, self._bufsize)
		self.temp_list = np.zeros(self._bufsize, dtype=np.float)

		self.setpoint_buffer = collections.deque([0.0]*self._bufsize, self._bufsize)
		self.setpoint_list = np.zeros(self._bufsize, dtype=np.float)

		self.time_list = collections.deque(np.linspace(-120, 0, self._bufsize))

		qtplt.setConfigOption('leftButtonPan', False)

		self.procPlot = qtplt.PlotWidget(title='Mesketemperatur', 
			left='Temperatur [C]', bottom='Tid [s]')

		self.trend_temp = self.procPlot.plot(self.time_list, self.temp_list,
			pen=qtplt.mkPen(color='g'))
		self.trend_setpoint = self.procPlot.plot(self.time_list, self.setpoint_list, 
			pen=qtplt.mkPen(color='r', style=Qt.DashLine))

		return self.procPlot
	#---------------------------------------------------


	def create_status_bar(self):
		self.status_text = QLabel('Idle')
		self.statusBar().addWidget(self.status_text, 1)
	#---------------------------------------------------


	def create_pump_box(self):

		self.pump_box = QGroupBox('Pumpe')

		pump_layout = QGridLayout()

		self.btnPump_on = QPushButton("På")
		self.btnPump_off = QPushButton("Av")
		self.btnPump_off.setEnabled(False)
		self.btnPump_on.clicked.connect(self.pumpOn)
		self.btnPump_off.clicked.connect(self.pumpOff)


		pump_layout.addWidget(self.btnPump_on,0,0)
		pump_layout.addWidget(self.btnPump_off,0,1)

		return pump_layout
	#---------------------------------------------------


	def create_checkbox(self, label, color, connect_fn, connect_param):
		"""
		Purpose:	create a personalized checkbox
		Input:		the label, color, activated function and the transmitted parameter
		Return:		return a checkbox widget
		"""

		checkBox = QCheckBox(label)
		checkBox.setChecked(1)
		checkBox.setFont(QFont("Arial", pointSize=12, weight=QFont.Bold))
		green = QPalette()
		green.setColor(QPalette.Foreground, color)
		checkBox.setPalette(green)
		checkBox.clicked.connect(partial(connect_fn,connect_param))

		return checkBox
	#---------------------------------------------------


	def create_main_frame(self):
		"""
		Purpose:	create the main frame Qt widget
		"""

		# Pump box
		pump_layout = self.create_pump_box()
		self.pump_box.setLayout(pump_layout)

		# Start/stop buttons
		self.btnStart = QPushButton("Start")
		self.btnStop = QPushButton("Stopp")
		self.btnStop.setEnabled(False)

		# Update set point buttons
		self.btnPlus = QPushButton('+', self)
		#self.btnPlus.setObjectName("btnPlus")
		self.btnPlus.clicked.connect(lambda: self.addValue(self.setval))

		self.btnMin = QPushButton('-', self)
		#self.btnMin.setObjectName("btnMin")
		self.btnMin.clicked.connect(lambda: self.subValue(self.setval))

		# Create the plot and curves
		self.procPlot_wid = self.create_plot()

		# Create the configuration horizontal panel
		self.gCheckbox = 	[	self.create_checkbox("Temperatur", Qt.green, self.activate_curve, 0),
								self.create_checkbox("Settpunkt", Qt.red, self.activate_curve, 1)
							]

		# Clear screen button
		self.btnClear = QPushButton("Tøm skjerm")
		self.btnClear.clicked.connect(self.clear_screen)

		# Temperature display
		self.temp_text = QLabel(self)
		self.temp_text.setText("Temperatur:")
		self.temp_box = QLabel(self)

		# Setpoint display
		self.setpoint_text = QLabel(self)
		self.setpoint_text.setText("Settpunkt:")
		self.setpoint_box = QLabel(self)
		self.setpoint_box.setText(str(round(self.setval,1)))

		# PID output display
		self.pidout_text = QLabel(self)
		self.pidout_text.setText("Pådrag:")
		self.pidout_box = QLabel(self)

		# Time display
		self.time_text = QLabel(self)
		self.time_text.setText("Tid:")
		self.time_box = QLabel(self)
		

		# Place the horizontal panel widget
		plot_layout = QGridLayout()
		plot_layout.addWidget(self.procPlot_wid,0,0,10,1)
		plot_layout.addWidget(self.gCheckbox[0],0,2,1,4)
		plot_layout.addWidget(self.gCheckbox[1],1,2,1,4)
		plot_layout.addWidget(self.btnStart,7,2,1,4)
		plot_layout.addWidget(self.btnStop,8,2,1,4)
		plot_layout.addWidget(self.btnClear,9,2,1,4)
		plot_layout.addWidget(self.btnPlus,6,2,1,2)
		plot_layout.addWidget(self.btnMin,6,4,1,2)
		plot_layout.addWidget(self.temp_text,3,2,1,2)
		plot_layout.addWidget(self.temp_box,3,4,1,2)
		plot_layout.addWidget(self.setpoint_text,5,2,1,2)
		plot_layout.addWidget(self.setpoint_box,5,4,1,2)
		plot_layout.addWidget(self.pidout_text,4,2,1,2)
		plot_layout.addWidget(self.pidout_box,4,4,1,2)
		plot_layout.addWidget(self.time_text,2,2,1,2)
		plot_layout.addWidget(self.time_box,2,4,1,2)

		plot_groupbox = QGroupBox('Mesketemperatur')
		plot_groupbox.setLayout(plot_layout)

		# Place the main frame and layout
		self.main_frame = QWidget()
		main_layout = QVBoxLayout()
		main_layout.addWidget(self.pump_box)
		main_layout.addWidget(plot_groupbox)
		main_layout.addStretch(1)
		self.main_frame.setLayout(main_layout)

		self.setCentralWidget(self.main_frame)
	#---------------------------------------------------


	def clear_screen(self):
		self.temp_buffer = collections.deque([0.0]*self._bufsize, self._bufsize)
		self.setpoint_buffer = collections.deque([0.0]*self._bufsize, self._bufsize)

	#---------------------------------------------------


	def activate_curve(self, axe):
		if self.gCheckbox[axe].isChecked():
			self.gcurveOn[axe] = 1
		else:
			self.gcurveOn[axe] = 0
	#---------------------------------------------------


	def create_menu(self):

		# Fil
		self.file_menu = self.menuBar().addMenu('Fil')
		self.menuBar().setNativeMenuBar(False)

		self.start_action = QAction(QIcon('beer.png'), 'Start mesking', self)
		self.start_action.setShortcut('Ctrl+M')
		self.start_action.setStatusTip('Start mesking av øl')
		self.start_action.triggered.connect(self.OnStart)

		self.boil_action = QAction(QIcon('boil.png'), 'Start koking', self)
		self.boil_action.setShortcut('Ctrl+K')
		self.boil_action.setStatusTip('Start koking av øl')
		self.boil_action.triggered.connect(self.boilStart)

		self.stop_action = QAction(QIcon('stop.png'), 'Stopp', self)
		self.stop_action.setShortcut('Ctrl+S')
		self.stop_action.setStatusTip('Slå av varmeelement')
		self.stop_action.triggered.connect(self.OnStop)

		self.exit_action = QAction(QIcon('exit.png'), 'Avslutt', self)
		self.exit_action.setShortcut('Ctrl+Q')
		self.exit_action.setStatusTip('Avslutt bryggjeapparatet')
		self.exit_action.triggered.connect(self.close)

		self.stop_action.setEnabled(False)

		self.add_actions(self.file_menu,
			(self.start_action, self.boil_action,
				self.stop_action, None, self.exit_action))


		# Plot
		self.graph_menu = self.menuBar().addMenu('Plot')

		self.autoScale_action = QAction('Autoskalér begge akser', self)
		self.autoScale_action.triggered.connect(self.procPlot.enableAutoScale)
	
		self.xMenu = QMenu('X-akse', self)
		self.showX_action = QAction('Vis', self, checkable=True)
		self.showX_action.setChecked(True)
		self.showX_action.triggered.connect(self.show_x)
		self.autoScaleX_action = QAction('Autoskalér', self)
		self.autoScaleX_action.triggered.connect(self.autoscale_x)
		self.add_actions(self.xMenu, (self.autoScaleX_action, self.showX_action))

		self.yMenu = QMenu('Y-akse', self)
		self.showY_action = QAction('Vis', self, checkable=True)
		self.showY_action.setChecked(True)
		self.showY_action.triggered.connect(self.show_y)
		self.autoScaleY_action = QAction('Autoskalér', self)
		self.autoScaleY_action.triggered.connect(self.autoscale_y)
		self.add_actions(self.yMenu, (self.autoScaleY_action, self.showY_action))

		self.graph_menu.addAction(self.autoScale_action)
		self.graph_menu.addMenu(self.xMenu)
		self.graph_menu.addMenu(self.yMenu)


		# Hjelp
		self.help_menu = self.menuBar().addMenu('Hjelp')
		self.about_action = QAction('Om', self)
		self.about_action.setShortcut('F1')
		self.about_action.setStatusTip('Om applikasjonen')
		#self.about_action.triggered.connect(self.on_about)

		self.add_actions(self.help_menu, (None, self.about_action))
	#---------------------------------------------------


	def autoscale_x(self, state):
		self.procPlot.enableAutoRange(axis='x', enable=True)
	#---------------------------------------------------


	def autoscale_y(self, state):
		self.procPlot.enableAutoRange(axis='y', enable=True)
	#---------------------------------------------------


	def show_x(self, state):
		if state:
			self.procPlot.showAxis('bottom', show=True)
			
		else:
			self.procPlot.showAxis('bottom', show=False)	
	#---------------------------------------------------


	def show_y(self, state):
		if state:
			self.procPlot.showAxis('left', show=True)
		else:
			self.procPlot.showAxis('left', show=False)
	#---------------------------------------------------


	def set_actions_enable_state(self):

		if self.portname.text() == '':
			start_enable = stop_enable = False
		else:
			start_enable = not self.monitor_active
			stop_enable = self.monitor_active

		self.start_action.setEnabled(start_enable)
		self.stop_action.setEnabled(stop_enable)
	#---------------------------------------------------


	def on_about(self):

		msg = __doc__
		QMessageBox.about(self, "About the demo", msg.strip())
	#---------------------------------------------------


	def pumpOn(self):
		"""
		Start pump
		"""

		self.btnPump_on.setEnabled(False)
		self.btnPump_off.setEnabled(True)

		self.pump_active = True
	#---------------------------------------------------


	def pumpOff(self):
		"""
		Start pump
		"""

		self.btnPump_on.setEnabled(True)
		self.btnPump_off.setEnabled(False)

		self.pump_active = False
	#---------------------------------------------------


	def OnStart(self):
		"""
		Start the monitor and the update timer
		"""

		self.btnStart.setEnabled(False)
		self.btnStop.setEnabled(True)

		self.start_action.setEnabled(False)
		self.stop_action.setEnabled(True)

		self.monitor_active = True

		self.pltTimer = QTimer()
		self.pltTimer.timeout.connect(self.tick_timer)
		self.pltTimer.start(1000)

		### PID controller
		self.P = 2
		self.I = 0.01
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

		self.status_text.setText('Brygging pågår')
		#debug('--> Monitor running')
	#---------------------------------------------------


	def boilStart(self):
		"""
		Set setpoint to 110 and turn pump on
		"""

		self.setval = 110
		self.setpoint_box.setText(str(self.setval))
		self.OnStart()
		self.pumpOn()

		self.boil_action.setEnabled(False)

		return self.setval
	#---------------------------------------------------


	def OnStop(self):
		"""
		Stop the monitor
		"""

		self.setval = 0
		self.pidval = 0
		self.pumpOff()
		self.timer.stop()
		self.pltTimer.stop()

		self.monitor_active = False

		self.btnStart.setEnabled(True)
		self.btnStop.setEnabled(False)

		self.start_action.setEnabled(True)
		self.boil_action.setEnabled(True)
		self.stop_action.setEnabled(False)

		self.timer.stop()
		self.status_text.setText('Brygging stoppet')
		#debug('--> Monitor idle')
	#---------------------------------------------------

	def on_timer(self):

        ### random process value for testing ###
		if self.i>70:
			self.procval = random.randint(1, 100)
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
		        self.pidout_box.setText(str(round(self.pid.output,1)))
		else:
		        self.logic = 0
		        self.pidout_box.setText(str(0))

		with open("mesh_temp.csv","a") as log:
		        log.write("{0},{1}\n".format(strftime("%Y-%m-%d %H:%M:%S"),str(self.temp)))
		
		# Update temperature display
		self.temp_box.setText(str(round(self.procval,1)))


	#---------------------------------------------------


	def tick_timer(self):
		self.time_seconds += 1
		self.runtime = "%d:%02d" % (self.time_seconds/60,self.time_seconds % 60)
		self.time_box.setText(str(self.runtime))
		self.updateplot()
	#---------------------------------------------------


	def updateplot(self):
		self.temp_buffer.append(self.procval)
		self.temp_list[:] = self.temp_buffer

		self.setpoint_buffer.append(self.setval)
		self.setpoint_list[:] = self.setpoint_buffer

		# if self.start_time == 0:
		# 	self.startplot_time = time.time()
		# 	self.start_time = 1
		# self.time_seconds = round(time.time() - self.startplot_time)
		self.time_list.popleft()
		self.time_list.append(self.time_seconds)

		if self.gcurveOn[0]:
			self.trend_temp.setData(self.time_list, self.temp_list)
		else: self.trend_temp.setData([], [])

		if self.gcurveOn[1]:
			self.trend_setpoint.setData(self.time_list, self.setpoint_list)
		else: self.trend_setpoint.setData([], [])
		# self.trend_temp.setData(self.time_list, self.temp_list)
		# self.trend_setpoint.setData(self.time_list, self.setpoint_list)
	#---------------------------------------------------


	def addValue(self,setval):
		self.setval += 1
		self.pid.setPoint = (self.setval)
		self.setpoint_box.setText(str(self.setval))
		return self.setval
	#---------------------------------------------------


	def subValue(self,setval):
		self.setval -= 1
		self.pid.setPoint = (self.setval)
		self.setpoint_box.setText(str(setval))
		return self.setval
	#---------------------------------------------------




	# The following two methods are utilities for simpler creation
	# and assignment of actions

	def add_actions(self, target, actions):
		for action in actions:
			if action is None:
				target.addSeparator()
			else:
				target.addAction(action)
	#---------------------------------------------------


	def create_action(self, text, slot=None, shortcut=None, icon=None, tip=None, checkable=False, signal="triggered()"):
		action = QAction(text, self)
		if icon is not None:
			action.setIcon(QIcon(":/%s.png" % icon))
		if shortcut is not None:
			action.setShortcut(shortcut)
		if tip is not None:
			action.setToolTip(tip)
			action.setStatusTip(tip)
		if slot is not None:
			self.connect(action, SIGNAL(signal), slot)
		if checkable:
			action.setCheckable(True)

		return action
	#---------------------------------------------------



def main():
	app = QApplication(sys.argv)
	form = BrewMonitor()
	#form.show()								# MacBook
	form.showFullScreen()					# Raspberry Pi
	app.exec_()


if __name__ == "__main__":
	main()













