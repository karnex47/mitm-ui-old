from PyQt4 import QtGui
from mainwidget import MainGui
from libmproxy.proxy.server import ProxyServer
from config import AppConfig
from settingsview import SettingsDialog

appStyle = """
QToolBar {{background: black}}
QIcon {{height: 10px; width: 10px}}
"""

class MainWindow(QtGui.QMainWindow):
    def __init__(self, options):
        QtGui.QMainWindow.__init__(self)

        self.appConfig = AppConfig()
        self.proxy_config = self.appConfig.getProxyConfig()

        self.ui = MainGui(self.get_server(), options)
        self.setCentralWidget(self.ui)

        self.status_bar = self.statusBar()
        self.status_bar.showMessage('Server started on port '+ str(self.proxy_config.port))
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(QtGui.QAction("Settings", self))

        toolbar = self.addToolBar('toolbar')
        self.server_control_action = QtGui.QAction(self.get_server_status_icon(), "Server start/stop", self)
        self.server_control_action.triggered.connect(self.toggle_server)
        clear_action = QtGui.QAction(QtGui.QIcon('assets/clear-icon.png'), "Clear", self)
        clear_action.triggered.connect(self.ui.clear_view)
        settings_action = QtGui.QAction(QtGui.QIcon('assets/gear-icon.png'), "Settings", self)
        settings_action.triggered.connect(self.show_settings)
        search_field = QtGui.QLineEdit();
        search_field.textChanged.connect(self.ui.search_changed)
        toolbar.addAction(clear_action)
        toolbar.addAction(self.server_control_action)
        toolbar.addAction(settings_action)
        toolbar.addSeparator()
        toolbar.addWidget(QtGui.QLabel("Filter:"))
        toolbar.addWidget(search_field)
        toolbar.addSeparator()
        toolbar.setMovable(False)
        self.setStyleSheet(appStyle)

        self.show()

    def toggle_server(self):
        if self.ui.isServerRunning():
            self.stopServer()
        else:
            self.startServer()

    def startServer(self):
        self.status_bar.showMessage('Server started on port '+ str(self.proxy_config.port))
        self.ui.start_server(self.get_server())
        self.server_control_action.setIcon(self.get_server_status_icon())

    def stopServer(self):
        self.status_bar.showMessage('Server stopped')
        self.ui.shut_down()
        self.server_control_action.setIcon(self.get_server_status_icon())

    def get_server(self):
        try:
            return ProxyServer(self.proxy_config)
        except:
            self.status_bar.showMessage('Error running proxy server')

    def get_server_status_icon(self):
        if self.ui.isServerRunning():
            return QtGui.QIcon('assets/off-icon.png')
        return QtGui.QIcon('assets/on-icon.png')

    def show_settings(self):
        settings_dialog = SettingsDialog(self.appConfig)


    def closeEvent(self, event):
        self.ui.terminate()