#!/usr/bin/python
import sys
from PyQt4 import QtGui
from gui import MainGui

def send_message(message):
    print message

try:
    from libmproxy import proxy, flow
    from libmproxy.proxy import config
    from libmproxy.protocol.http import HTTPResponse
    from libmproxy.proxy.config import ProxyConfig
    from libmproxy.proxy.server import ProxyServer
    from libmproxy.encoding import decode_gzip
    from libmproxy.proxy.primitives import ProxyServerError
    import OpenSSL
except:
    send_message('Could not start proxy, error loading libraries')
    sys.exit(1)


def check_pyopenssl_version():
    version = OpenSSL.__version__.split('.')
    version = {
        'major': int(version[0]),
        'minor': int(version[1]),
        'patch': int(version[2])
    }

    if version['major'] == 0 and version['minor'] < 14:
        send_message('Could not start proxy, pyOpenSSL version is ' + OpenSSL.__version__ + ' (Path: ' + OpenSSL.__file__[0:OpenSSL.__file__.rfind('/')] + ')')
        sys.exit(1)


def get_server(options):
    try:
        return ProxyServer(options)
    except:
        send_message('Error running proxy server')
        sys.exit(1)


def main(argv):
    check_pyopenssl_version()
    proxy_config = ProxyConfig(
        port=int(1025),
        # mode="upstream",
        # upstream_server=(False, False, "localhost", 8081)
    )
    server = get_server(proxy_config)
    options = None
    app = QtGui.QApplication(sys.argv)
    # window = QtGui.QMainWindow()
    # window.show()
    ui = MainGui(server, options)
    ui.setWindowTitle('Name TBD')
    ui.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main(sys.argv)