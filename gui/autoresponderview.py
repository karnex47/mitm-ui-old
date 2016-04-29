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

        self.model = CustomStandardListModel()
        for key in self.state.get_auto_response_keys():
            list_item = QtGui.QStandardItem(key)
            list_item.setCheckable(True)
            list_item.setFlags(list_item.flags() | QtCore.Qt.ItemIsEditable)
            if self.state.get_auto_response_data(key)['active']:
                list_item.setCheckState(2)
            else:
                list_item.setCheckState(0)
            self.model.appendRow(list_item)
        self.model.onItemChange.connect(self.on_list_item_change)
        self.response_list = QtGui.QListView()
        self.response_list.setModel(self.model)
        self.response_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.response_list.clicked.connect(self.set_stored_file_path)
        self.connect(self.response_list, QtCore.SIGNAL("customContextMenuRequested(QPoint)"), self.show_context_menu)
        # self.connect(self.response_list, QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem*)"), self.response_list.editItem)

        self.file_selector = FileSelector()
        self.connect(self.file_selector, QtCore.SIGNAL('FILE_CONTENT_SET'), self.set_content_from_file)

        layout.addWidget(self.response_list)
        layout.addWidget(self.file_selector)

        layout.setStretchFactor(self.response_list, 99)
        layout.setStretchFactor(self.file_selector, 1)
        self.setLayout(layout)

    def add_auto_response_flow(self, f):
        url = f.request.url
        list_item = QtGui.QStandardItem(url)
        list_item.setCheckable(True)
        list_item.setCheckState(2)
        list_item.setFlags(list_item.flags() | QtCore.Qt.ItemIsEditable)
        self.model.appendRow(list_item)
        response = copy.deepcopy(f.response)
        response.decode()
        data = {
            "active": True,
            "response": response,
            "match": url,
            "matchType": "EXACT",
            "file": ''
        }

        self.state.add_auto_response(url, data)

    def on_list_item_change(self, oldItem, newItem):
        if not oldItem.text() == newItem.text():
            self.state.replace_auto_response_key(str(oldItem.text()), str(newItem.text()))
        if not oldItem.checkState() == newItem.checkState():
            self.state.set_auto_response_active(str(newItem.text()), newItem.checkState())

        
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

    def set_stored_file_path(self, index):
        key = str(self.model.itemFromIndex(index).text())
        self.file_selector.set_file_path(self.state.get_content_file_path(key))

    def set_content_from_file(self, file_path):
        try:
            content_file = open(file_path, 'r')
            key = str(self.model.itemFromIndex(self.response_list.currentIndex()).text())
            self.state.set_content_file_path(key, file_path)
            response = self.state.get_cached_response(key)
            response.content = str(content_file.read())
            if response.headers.get_first('content-encoding'):
                response.encode(self.conn.headers.get_first('content-encoding'))
            self.state.set_auto_response(key, response)
            content_file.close()
        except IOError:
            show_dialog("Cannot read file")


class CustomStandardListModel(QtGui.QStandardItemModel):
    onItemChange = QtCore.pyqtSignal(QtGui.QStandardItem, QtGui.QStandardItem)

    def setData(self, index, value, role):
        if role == QtCore.Qt.EditRole or role == QtCore.Qt.DisplayRole:
            old = self.itemFromIndex(index).clone()
            QtGui.QStandardItemModel.setData(self, index, value, role)
            new = self.itemFromIndex(index)
            self.onItemChange.emit(old, new)
        return




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
        save_button = QtGui.QPushButton('Save')
        save_button.clicked.connect(self.send_file_content)

        layout.addWidget(label)
        layout.addWidget(self.file_name)
        layout.addWidget(file_dialog_button)
        layout.addWidget(save_button)

        self.setLayout(layout)
        self.show()

    def show_file_dialog(self):
        fileDialog = QtGui.QFileDialog()
        fileDialog.fileSelected.connect(self.set_file_path)
        fileDialog.exec_()
        
    def send_file_content(self):
        self.emit(QtCore.SIGNAL('FILE_CONTENT_SET'), str(self.file_name.text()).strip())

    def set_file_path(self, path):
        self.file_name.setText(path)



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