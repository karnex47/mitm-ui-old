from PyQt4 import QtCore, QtGui
from detailsview import DetailsView


class FlowListModel(QtCore.QAbstractListModel):
    def __init__(self, state, parent=None):
        QtCore.QAbstractListModel.__init__(self, parent)
        self.state = state
        self._data = self.state.view
        self.connect(self.state, QtCore.SIGNAL('UPDATE_LIST'), self.update_list)

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return len(self._data)

    def data(self, QModelIndex, int_role=None):
        if int_role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self._data[QModelIndex.row()])
        return QtCore.QVariant()

    def update_list(self, index, mode):
        if not index:
            self.reset()
        elif mode == 'add':
            self.emit(QtCore.SIGNAL('rowsInserted(const QModelIndex&,int,int)'), self.createIndex(index, 0), index, index)
        elif mode == 'update':
            pass
        elif mode == 'delete':
            pass

    def getFlowData(self, index):
        return self._data[index.row()]


class FlowListItemDelegate(QtGui.QStyledItemDelegate):
    def __init__(self, parent=None, *args):
        QtGui.QStyledItemDelegate.__init__(self, parent, *args)
        self.model = parent.model

    def paint(self, painter, option, index):
        options = QtGui.QStyleOptionViewItemV4(option)
        self.initStyleOption(options, index)
        painter.save()
        style = QtGui.QApplication.style() if options.widget is None else options.widget.style()
        doc = QtGui.QTextDocument()
        text = self.getHTMLFromFlow(self.model.getFlowData(index))
        doc.setHtml(text)
        options.text = ""
        style.drawControl(QtGui.QStyle.CE_ItemViewItem, options, painter)
        ctx = QtGui.QAbstractTextDocumentLayout.PaintContext()
        textRect = style.subElementRect(QtGui.QStyle.SE_ItemViewItemText, options)
        painter.save()
        painter.translate(textRect.topLeft())
        painter.setClipRect(textRect.translated(-textRect.topLeft()))
        doc.documentLayout().draw(painter, ctx)
        painter.restore()

    def sizeHint(self, option, index):
        options = QtGui.QStyleOptionViewItemV4(option)
        self.initStyleOption(options,index)
        doc = QtGui.QTextDocument()
        doc.setHtml(options.text)
        doc.setTextWidth(doc.textWidth())
        return QtCore.QSize(doc.textWidth(), doc.size().height())

    def getHTMLFromFlow(self, f):
        html = '<div style="{0}">' \
               '<span>{1}</span>' \
               '<span class="spacer">  </span>' \
               '<span"><strong>{2}</strong></span>' \
               '<span class="space"r>  </span>' \
               '<span>{3}</span>' \
               '</div>'
        style = 'color: black'
        code = '   '
        if f.live:
            style = 'color: grey'
        if f.error:
            style = 'color: red'
        if f.response:
            code = f.response.code
        return html.format(style, code, f.request.method, f.request.url)


class FlowList(QtGui.QListView):
    def __init__(self, state):
        super(FlowList, self).__init__()
        self.model = FlowListModel(state)
        self.setModel(self.model)
        self.setItemDelegate(FlowListItemDelegate(self))
        self.setStyleSheet(':item:selected:active {background: lightblue}')

        self.clicked.connect(self.on_flow_list_click)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.connect(self, QtCore.SIGNAL("customContextMenuRequested(QPoint)"), self.show_context_menu)

        # self.setMaximumSize(2000,2000)
        # self.setMinimumSize(400,400)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
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
