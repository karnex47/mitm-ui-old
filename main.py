#!/usr/bin/python
import sys
from PyQt4 import QtGui
from gui import MainWindow

try:
    from libmproxy.proxy.config import ProxyConfig
    from libmproxy.proxy.server import ProxyServer
    import OpenSSL
except ImportError:
    print 'Could not start proxy, error loading libraries'
    sys.exit(1)


def check_pyopenssl_version():
    version = OpenSSL.__version__.split('.')
    version = {
        'major': int(version[0]),
        'minor': int(version[1]),
        'patch': int(version[2])
    }

    if version['major'] == 0 and version['minor'] < 14:
        print 'Could not start proxy, pyOpenSSL version is ' + OpenSSL.__version__ + ' (Path: ' + OpenSSL.__file__[0:OpenSSL.__file__.rfind('/')] + ')'
        sys.exit(1)


def get_server(options):
    try:
        return ProxyServer(options)
    except:
        print 'Error running proxy server'
        sys.exit(1)


def main(argv):
    check_pyopenssl_version()
    proxy_config = ProxyConfig(
        port=int(1026),
        mode="upstream",
        upstream_server=(False, False, "localhost", 8081)
    )
    server = get_server(proxy_config)
    options = None
    app = QtGui.QApplication(sys.argv)
    ui = MainWindow(server, options)
    ui.setWindowTitle('Name TBD')
    ui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main(sys.argv)