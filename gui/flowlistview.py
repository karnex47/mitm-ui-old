from PyQt4 import QtCore, QtGui
from detailsview import DetailsView


class FlowListModel(QtCore.QAbstractListModel):
    def __init__(self, data=[], parent=None):
        QtCore.QAbstractListModel.__init__(self, parent)
        self._data = data

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self._data)

    def data(self, QModelIndex, int_role=None):
        if int_role == QtCore.Qt.DisplayRole:
            model = self._data[QModelIndex.row()]
            return '| {0} | {1} {2}'.format(model.request.method, model.request.url, '')

    def setFlowData(self, data):
        self._data = data

    def getFlowData(self, index):
        return self._data[index.row()]



class FlowList(QtGui.QListView):
    def __init__(self):
        super(FlowList, self).__init__()
        self.model = FlowListModel()
        self.setModel(self.model)

        self.clicked.connect(self.on_flow_list_click)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.connect(self, QtCore.SIGNAL("customContextMenuRequested(QPoint)"), self.show_context_menu)

        self.setMaximumSize(2000,2000)
        self.setMinimumSize(400,400)
        self.show()

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_flow_list_click(self, index):
        f = self.model.getFlowData(index)
        self.emit(QtCore.SIGNAL("clicked"), f)

    def show_flow_details(self):
        f = self.model.getFlowData(self.currentIndex())
        DetailsView(f)


    def show_context_menu(self, QPos):
        self.listMenu = QtGui.QMenu()
        view_details = self.listMenu.addAction("View Details")
        add_to_autoresponder = self.listMenu.addAction("Add to auto-responder")
        add_to_replay = self.listMenu.addAction("Add to replay")
        self.connect(view_details, QtCore.SIGNAL("triggered()"), self.show_flow_details)
        self.connect(add_to_replay, QtCore.SIGNAL("triggered()"), self.add_to_replay_clicked)
        self.connect(add_to_autoresponder, QtCore.SIGNAL("triggered()"), self.add_to_autoresponder_clicked)
        parentPosition = self.mapToGlobal(QtCore.QPoint(0, 0))
        self.listMenu.move(parentPosition + QPos)
        self.listMenu.show()

    def add_to_replay_clicked(self):
        f = self.model.getFlowData(self.currentIndex())
        self.emit(QtCore.SIGNAL('ADD_TO_REPLAY'), f)

    def add_to_autoresponder_clicked(self):
        f = self.model.getFlowData(self.currentIndex())
        self.emit(QtCore.SIGNAL('ADD_TO_AUTO_RESPONDER'), f)


    def set_list_data(self, data):
        self.model.setFlowData(data)
        self.reset()
