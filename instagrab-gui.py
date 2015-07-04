import sys
from PyQt4 import QtGui
from PyQt4.QtCore import SIGNAL,SLOT
from instagrab import Client,Downloader
import Queue

class InstagrabApp(QtGui.QWidget):
	def __init__(self):
		super(InstagrabApp, self).__init__()
		self.init_layout()
		self.queue = Queue.Queue()
		self.client = Client("206279665.74069ea.3e7744ba4dfd4d6384661e55ae69d5ed",self.queue)

	def changeText(self, text):
		self.start_button.setEnabled(text != "")

	def runcollector(self):
		account_id = str(self.input_edit.text())
		self.log.append("Loading images for account "+account_id+".")
		self.log.append("collecting..")
		for i in range(3):
		 	t = Downloader(self.queue)
		 	t.setDaemon(True)
		 	t.start()
		#start collecting
		self.client.collect(account_id)
		#termination
		self.queue.join()
		self.log.append("Loading images from account "+account_id+" completed.")


	def init_layout(self):
		self.input_box = QtGui.QLabel("Enter instagram ID:")
		self.input_edit = QtGui.QLineEdit()
		self.start_button = QtGui.QPushButton("Start")
		self.start_button.setEnabled(False)
		self.log = QtGui.QTextEdit("Welcome to the Instagrab\n")
		self.log.setEnabled(True)
		self.log.setReadOnly(True)
		self.quit_button = QtGui.QPushButton("Quit")

		grid = QtGui.QGridLayout()
		grid.setSpacing(10)
		grid.addWidget(self.input_box,1,0)
		grid.addWidget(self.input_edit,1,1,1,4)
		grid.addWidget(self.log,2,0,3,4)
		grid.addWidget(self.start_button,5,1)
		grid.addWidget(self.quit_button,5,2)

		self.setLayout(grid)
		self.setWindowTitle('Instagrab')    
		self.show()

		#setup signal slot
		#enter -> start
		self.input_edit.returnPressed.connect(self.start_button.click)
		#has text -> enable button
		self.input_edit.textChanged.connect(self.changeText)
		#quit button to quit
		self.quit_button.clicked.connect(self.close)
		self.start_button.clicked.connect(self.runcollector)


def main():
	app = QtGui.QApplication(sys.argv)
	ex = InstagrabApp()

	sys.exit(app.exec_())

if __name__ == '__main__':
	main()