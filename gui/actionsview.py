from PyQt4 import QtGui, QtCore
from detailsview import DetailsTabs
from autoresponderview import AutoResponder

class ActionsView(QtGui.QTabWidget):
    def __init__(self, state):
        QtGui.QTabWidget.__init__(self)
        self.state = state
        self.create_tabs()
        self.setStyleSheet("""
            .DetailsTab {
                top: 0;
                left: 0;
            }
        """)
        self.show()

    def create_tabs(self):
        self.auto_responder = AutoResponder(self.state)
        self.replay_flow = ReplayFlow()
        self.details = DetailsTabs()
        self.insertTab(0, self.auto_responder, "Auto Responder")
        self.insertTab(1, self.replay_flow, "Replay Request")
        self.insertTab(2, self.details, "View Details")

    def set_flow_details(self, f):
        self.details.set_flow(f)

    def add_auto_response_flow(self, f):
        self.auto_responder.add_auto_response_flow(f)

class ReplayFlow(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
