from PyQt4 import QtCore, QtGui
from flowdetails import FlowDetails
import copy

class AutoResponder(QtGui.QWidget):
    def __init__(self, state):
        QtGui.QWidget.__init__(self)
        self.state = state
        self.create_window()
        self.show()

    def create_window(self):
        layout = QtGui.QVBoxLayout()
        layout.addStretch(1)

        self.model = QtGui.QStandardItemModel()
        self.model.itemChanged.connect(self.on_list_item_change)
        self.response_list = QtGui.QListView()
        self.response_list.setModel(self.model)
        self.response_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.connect(self.response_list, QtCore.SIGNAL("customContextMenuRequested(QPoint)"), self.show_context_menu)

        file_selector = FileSelector()

        layout.addWidget(self.response_list)
        layout.addWidget(file_selector)

        layout.setStretchFactor(self.response_list, 99)
        layout.setStretchFactor(file_selector, 1)
        self.setLayout(layout)

    def add_auto_response_flow(self, f):
        url = f.request.url
        list_item = QtGui.QStandardItem(url)
        list_item.setCheckable(True)
        list_item.setCheckState(2)
        self.model.appendRow(list_item)
        response = copy.deepcopy(f.response)
        response.decode()
        data = {
            "active": True,
            "response": response,
            "match": url,
            "matchType": "EXACT"
        }

        self.state.add_auto_response(url, data)

    def on_list_item_change(self, item):
        self.state.set_auto_response_active(str(item.text()), item.checkState())
        
    def show_context_menu(self, QPos):
        self.listMenu = QtGui.QMenu()
        edit_response = self.listMenu.addAction("Edit Response")
        self.connect(edit_response, QtCore.SIGNAL("triggered()"), self.edit_response_clicked)
        remove_response = self.listMenu.addAction("Remove Response")
        self.connect(remove_response, QtCore.SIGNAL("triggered()"), self.remove_response_clicked)
        parentPosition = self.mapToGlobal(QtCore.QPoint(0, 0))
        self.listMenu.move(parentPosition + QPos)
        self.listMenu.show()

    def edit_response_clicked(self):
        key = str(self.model.itemFromIndex(self.response_list.currentIndex()).text())
        EditResponseDialog(key, self.state.get_cached_response(key), self.on_response_change)

    def on_response_change(self, key, response):
        self.state.set_auto_response(key, response)

    def remove_response_clicked(self):
        index = self.response_list.currentIndex()
        key = str(self.model.itemFromIndex(index).text())
        self.model.removeRow(index.row())
        self.state.remove_auto_response(key)


class FileSelector(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.create()

    def create(self):
        layout = QtGui.QHBoxLayout()

        label = QtGui.QLabel("Respond with:")
        self.file_name = QtGui.QLineEdit()
        file_dialog_button = QtGui.QPushButton('...')
        file_dialog_button.clicked.connect(self.show_file_dialog)

        layout.addWidget(label)
        layout.addWidget(self.file_name)
        layout.addWidget(file_dialog_button)

        self.setLayout(layout)
        self.show()

    def show_file_dialog(self):
        fileDialog = QtGui.QFileDialog()
        fileDialog.fileSelected.connect(self.set_file_path)
        fileDialog.exec_()

    def set_file_path(self, path):
        self.file_name.setText(path)

    def get_file(self):
        try:
            msg_file = open(self.file_name.text().strip())
            return msg_file
        except IOError:
            show_dialog('Error opening file, check the path')


class EditResponseDialog(QtGui.QDialog):
    def __init__(self, key, conn, callback):
        QtGui.QDialog.__init__(self)
        self.key = key
        self.callback = callback
        editor = FlowDetails(conn, self, True)
        self.connect(editor, QtCore.SIGNAL('onSave'), self.on_save)
        editor.move(0,0)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.exec_()

    def on_save(self, response):
        print response
        self.callback(self.key, response)


def show_dialog(msg):
    dialog = QtGui.QDialog(str(msg))
    dialog.exec_()