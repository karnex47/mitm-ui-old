from PyQt4 import QtGui, QtCore
from flowlistview import FlowList
from actionsview import ActionsView
from libmproxy.proxy.primitives import ProxyServerError
from controller import ControllerMaster, ControllerState
from cPickle import dump, load, PicklingError, UnpicklingError, HIGHEST_PROTOCOL


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

    def terminate(self):
        self.controller.shutdown()
        QtCore.QThread.terminate(self)


class MainGui(QtGui.QWidget):
    def __init__(self, server, options, parent=None):
        QtGui.QWidget.__init__(self, parent)
        prev_instatnce_state = self.get_prev_instance_state()
        self.state = ControllerState()
        if prev_instatnce_state:
            self.state.set_data_from_saved_state(prev_instatnce_state)
        self.flow_list = FlowList(self.state)
        self.actions_view = ActionsView(self.state)
        self.show_main_widget(server, options)

    def show_main_widget(self, server, options):
        layout = QtGui.QHBoxLayout()
        splitter = QtGui.QSplitter()
        splitter.addWidget(self.flow_list)
        splitter.addWidget(self.actions_view)
        layout.addWidget(splitter)
        self.setLayout(layout)
        self.flow_list.setStyleSheet( """QListView:item:selected:active {background-color:red;}""")

        self.controllerThread = ControllerThread(server, self.state, options)
        self.connect(self.flow_list, QtCore.SIGNAL("clicked"), self.set_flow_details)
        # self.connect(self.flow_list, QtCore.SIGNAL("ADD_TO_REPLAY"), self.show_flow_details)
        self.connect(self.flow_list, QtCore.SIGNAL("ADD_TO_AUTO_RESPONDER"), self.add_auto_response)
        self.controllerThread.start()

    def set_flow_details(self, f):
        self.actions_view.set_flow_details(f)

    def add_auto_response(self, f):
        self.actions_view.add_auto_response_flow(f)

    def search_changed(self, newSearch):
        self.state.set_search_string(newSearch)

    def clear_view(self):
        self.state.clear()

    def shut_down(self):
        self.controllerThread.terminate()

    def start_thread(self):
        self.controllerThread.start()

    def start_thread(self, server):
        self.controllerThread = ControllerThread(server, self.state)

    def get_prev_instance_state(self):
        try:
            f = open('data', 'rb')
            data = load(f)
            f.close()
            return data
        except UnpicklingError:
            print 'Error loading data file, falling back to empty state'
            return None
        except IOError:
            print 'Error could not find file, falling back to empty state'
            return None

    def terminate(self):
        state_data = {}
        state_data['auto_response'] = self.state._auto_respond
        state_data['replay'] = self.state._replay
        try:
            f = open('data', 'wb')
            dump(state_data, f, HIGHEST_PROTOCOL)
            f.close()
        except PicklingError:
            print 'Error writing data file'
        self.controllerThread.terminate()