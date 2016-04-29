from PyQt4 import QtCore, QtGui
from flowdetails import FlowDetails

class DetailsView(QtGui.QDialog):
    def __init__(self, f):
        QtGui.QDialog.__init__(self)
        tabs = DetailsTabs(self)
        tabs.set_flow(f)
        tabs.move(0,0)
        self.setWindowTitle(f.request.url)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.exec_()


class DetailsTabs(QtGui.QTabWidget):
    def __init__(self, parent=None):
        QtGui.QTabWidget.__init__(self, parent)
        self.show()

    def set_flow(self, f):
        self.clear()
        if f.request:
            self.addTab(FlowDetails(f.request), "Request")
        if f.response:
            self.addTab(FlowDetails(f.response), "Response")