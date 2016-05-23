from PyQt4 import QtGui, QtCore
from libmproxy import flow
from copy import deepcopy


class FlowDetails(QtGui.QWidget):
    def __init__(self, conn, parent=None, editable=False):
        QtGui.QWidget.__init__(self, parent)
        self.conn = conn
        layout = QtGui.QVBoxLayout()
        self.flow_details_tabs = FlowDetailsTabs(conn, editable)
        layout.addWidget(self.flow_details_tabs)
        if editable:
            button = QtGui.QPushButton('Save')
            button.clicked.connect(self.on_save)
            layout.addWidget(button)

        self.setLayout(layout)
        self.show()

    def on_save(self):
        f = self.flow_details_tabs.get_edited_flow()
        if self.conn.headers.get_first('content-encoding'):
            f.encode(self.conn.headers.get_first('content-encoding'))
        self.emit(QtCore.SIGNAL('onSave'), f)


class FlowDetailsTabs(QtGui.QTabWidget):
    def __init__(self, conn, editable=False):
        QtGui.QTabWidget.__init__(self)
        self.conn = deepcopy(conn)
        self.create_tabs(editable)

    def create_tabs(self, editable):
        self.header_details = Headers(self.conn, editable)
        self.content_details = ContentDetails(self.conn, editable)
        self.insertTab(0, self.header_details, "Headers")
        self.insertTab(1, self.content_details, "Content")

    def get_edited_flow(self):
        self.conn.headers = self.header_details.get_headers()
        if hasattr(self.conn, 'code'):
            self.conn.code = self.header_details.get_code()
        self.conn.content = self.content_details.get_content()
        return self.conn


class Headers(QtGui.QWidget):
    def __init__(self, conn, editable=False):
        QtGui.QWidget.__init__(self)
        layout = QtGui.QVBoxLayout()

        if hasattr(conn, 'url'):
            layout.addWidget(QtGui.QLabel(conn.url))

        self.headers = HeaderDetails(conn, editable)
        layout.addWidget(self.headers)

        if hasattr(conn, 'code'):
            self.code = QtGui.QLineEdit(str(conn.code))
            if not editable:
                self.code.setReadOnly(True)
            layout.addWidget(self.code)
        self.setLayout(layout)

    def get_headers(self):
        return self.headers.get_headers()

    def get_code(self):
        return int(str(self.code.text()))


class HeaderDetails(QtGui.QListWidget):
    def __init__(self, conn, editable=False):
        QtGui.QListWidget.__init__(self)
        if editable:
            self.connect(self, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem*)"), self.editItem)
        for key, value in conn.headers:
            item = QtGui.QListWidgetItem(str(key)+': '+str(value))
            if editable:
                item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
            self.addItem(item)

    def get_headers(self):
        headers = []
        for i in range(0, self.count()):
            item = self.item(i)
            key = str(item.text().split(':')[0]).strip()
            value = str(item.text().split(':')[1]).strip()
            headers.append([key, value])
        return flow.ODictCaseless(headers)


class ContentDetails(QtGui.QTextEdit):
    def __init__(self, conn, editable=False):
        QtGui.QTextEdit.__init__(self)
        self.doc = QtGui.QTextDocument()
        if 'content-encoding' in conn.headers.keys():
            conn.decode()
        self.doc.setPlainText(conn.content)
        self.setDocument(self.doc)

    def get_content(self):
        return str(self.toPlainText())