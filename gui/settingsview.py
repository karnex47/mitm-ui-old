from PyQt4 import QtCore, QtGui


class SettingsDialog(QtGui.QDialog):
    def __init__(self, config):
        QtGui.QDialog.__init__(self)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(SettingsView(config))
        layout.setMargin(0)
        self.setLayout(layout)
        self.setWindowTitle("Settings")
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.exec_()


class SettingsView(QtGui.QWidget):
    def __init__(self, config):
        QtGui.QWidget.__init__(self)
        proxy_config = config.getProxyConfig()
        layout = QtGui.QVBoxLayout()
        layout.addWidget(TextEditWithLabel("Proxy port:", proxy_config.port))
        self.setLayout(layout)


class TextEditWithLabel(QtGui.QWidget):
    def __init__(self, label, text):
        QtGui.QWidget.__init__(self)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(QtGui.QLabel(label))
        layout.addWidget(QtGui.QLineEdit(str(text)))
        self.setLayout(layout)