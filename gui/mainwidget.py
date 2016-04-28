from PyQt4 import QtGui, QtCore
from flowlistview import FlowList
from actionsview import ActionsView
from libmproxy.proxy.primitives import ProxyServerError
from controller import ControllerMaster, ControllerState


class ControllerThread(QtCore.QThread):
    def __init__(self, server, state, options):
        QtCore.QThread.__init__(self)
        self.controller = ControllerMaster(server, state, options)
        self.flow_list = QtCore.pyqtSignal(object)

    def run(self):
        try:
            self.controller.run()
        except ProxyServerError:
            print 'Could not run server'


class MainGui(QtGui.QWidget):
    def __init__(self, server, options):
        super(MainGui, self).__init__()
        self.state = ControllerState()
        self.flow_list = FlowList()
        self.actions_view = ActionsView(self.state)
        self.show_main_widget(server, options)

    def show_main_widget(self, server, options):
        layout = QtGui.QHBoxLayout()
        layout.addStretch(1)
        layout.addWidget(self.flow_list)
        layout.addWidget(self.actions_view)
        self.setLayout(layout)

        self.controllerThread = ControllerThread(server, self.state, options)
        self.state.signal.connect(self.set_flow)
        self.connect(self.flow_list, QtCore.SIGNAL("clicked"), self.set_flow_details)
        # self.connect(self.flow_list, QtCore.SIGNAL("ADD_TO_REPLAY"), self.show_flow_details)
        self.connect(self.flow_list, QtCore.SIGNAL("ADD_TO_AUTO_RESPONDER"), self.add_auto_response)
        self.controllerThread.start()
        # self.setMinimumSize(800, 400)

    def set_flow_details(self, f):
        self.actions_view.set_flow_details(f)

    def add_auto_response(self, f):
        self.actions_view.add_auto_response_flow(f)

    def shut_down(self):
        self.controllerThread.terminate()

    def set_flow(self):
        self.flow_list.set_list_data(self.state.view)