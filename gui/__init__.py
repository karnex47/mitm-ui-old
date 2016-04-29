from PyQt4 import QtGui
from mainwidget import MainGui

class MainWindow(QtGui.QMainWindow):
    def __init__(self, server, options):
        QtGui.QMainWindow.__init__(self)
        self.ui = MainGui(server, options)
        self.setCentralWidget(self.ui)
        self.show()

    def closeEvent(self, event):
        self.ui.terminate()
