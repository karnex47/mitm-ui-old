from PyQt4 import QtGui
from mainwidget import MainGui
from libmproxy.proxy.config import ProxyConfig
from libmproxy.proxy.server import ProxyServer

class MainWindow(QtGui.QMainWindow):
    def __init__(self, server, options):
        QtGui.QMainWindow.__init__(self)

        self.proxy_config = ProxyConfig(
            port=int(1026),
            # mode="upstream",
            # upstream_server=(False, False, "localhost", 8081)
        )

        self.ui = MainGui(server, options)
        self.setCentralWidget(self.ui)

        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')

        toolbar = self.addToolBar('toolbar')
        clear_action = QtGui.QAction(QtGui.QIcon('clear-icon.png'), "Clear", self)
        clear_action.triggered.connect(self.ui.clear_view)
        search_field = QtGui.QLineEdit();
        search_field.textChanged.connect(self.ui.search_changed)
        settings_action = QtGui.QAction(QtGui.QIcon('gear-icon.png'), "Settings", self)
        settings_action.triggered.connect(self.show_settings)
        toolbar.addAction(clear_action)
        toolbar.addAction(settings_action)
        toolbar.addSeparator()
        toolbar.addWidget(QtGui.QLabel("Filter:"))
        toolbar.addWidget(search_field)
        toolbar.setMovable(False)

        self.show()

    def startServer(self):
        pass

    def stopServer(self):
        pass

    def show_settings(self):
        pass

    def closeEvent(self, event):
        self.ui.terminate()