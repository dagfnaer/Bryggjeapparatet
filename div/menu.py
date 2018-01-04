import sys

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class Main(QMainWindow):

	def __init__(self):
		super().__init__()
		self.initUI()



	def initUI(self):

		menubar = self.menuBar()
		menubar.setNativeMenuBar(False)
		fileMenu = menubar.addMenu('Fil')
		viewMenu = menubar.addMenu('Vis')

		self.statusbar = self.statusBar()
		self.statusbar.showMessage('Klar')

		impMenu = QMenu('Importer', self)
		impAct = QAction('Importer oppskrift', self)
		impAct.setStatusTip('Importer oppskrift')	
		impMenu.addAction(impAct)

		exitAct = QAction(QIcon('exit.png'), '&Avslutt', self)
		exitAct.setShortcut('Ctrl+Q')
		exitAct.setStatusTip('Avslutt programvare')
		exitAct.triggered.connect(qApp.quit)

		newAct = QAction(QIcon('beer.png'),'&Start brygging', self)
		newAct.setStatusTip('Brygg øl')

		fileMenu.addAction(newAct)
		fileMenu.addMenu(impMenu)
		fileMenu.addAction(exitAct)

		viewStatAct = QAction('Vis statusbar', self, checkable=True)
		viewStatAct.setStatusTip('Vis statusbar')
		viewStatAct.setChecked(True)
		viewStatAct.triggered.connect(self.statusbarToggleMenu)

		viewGraphAct = QAction('Vis temperatur', self, checkable=True)
		viewGraphAct.setStatusTip('Vis temperaturgraf')
		viewGraphAct.setChecked(True)

		viewMenu.addAction(viewStatAct)
		viewMenu.addAction(viewGraphAct)

		self.resize(300, 300)
		self.center
		self.setWindowTitle('Bryggjeapparatet')
		self.show()



	def contextMenuEvent(self, event):

		cmenu = QMenu(self)

		newAct = cmenu.addAction("New")
		opnAct = cmenu.addAction("Open")
		quitAct = cmenu.addAction("Quit")
		action = cmenu.exec_(self.mapToGlobal(event.pos()))

		if action == quitACt:
			qApp.quit()



	def statusbarToggleMenu(self, state):
		if state:
			self.statusbar.show()
		else:
			self.statusbar.hide()



	def center(self):

		qr = self.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def grid(self):
		grid = QGridLayout()
		self.setLayout(grid)

		numpad = ['7', '8', '9',
				  '4', '5', '6',
				  '1', '2', '3',
				  'OK', '0', 'Cancel']
		position = [(i,j) for i in range(4) for j in range(3)]

		for position, numb in zip(positions, numpad):
			if numb == '':
				continue
			button = QPushButton(numb)
			grid.addWidget(button, *position)

	
if __name__ == '__main__':

	app = QApplication(sys.argv)
	ex = Main()
	sys.exit(app.exec_())

