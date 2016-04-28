from PyQt4 import QtGui
from mainwidget import MainGui

class Gui(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.showMainWindow()

    def showMainWindow(self):
        MainGui()