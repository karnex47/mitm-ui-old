import ConfigParser
from libmproxy import platform
from libmproxy.proxy.config import ProxyConfig
from netlib import http_auth
import os, sys

TRANSPARENT_SSL_PORTS = [443, 8443]
PROXY_OPTIONS = "ProxyOptions"

class AppConfig:
    proxy_config = None
    def parseConfig(self, section):
        configParser = ConfigParser.SafeConfigParser()
        if not os.path.isfile('./config.ini'):
            return {}
        configParser.read('./config.ini')
        return configParser._sections[section]

    def getProxyConfig(self):
        if not self.proxy_config:
            config = self.parseConfig(PROXY_OPTIONS)
            config = Config(config)
            self.proxy_config = self.parse_proxy_options(config)
        return self.proxy_config

    def parse_proxy_options(self, options):
        c = 0
        mode, upstream_server = None, None
        if options.transparent_proxy:
            c += 1
            if not platform.resolver:
                return self.error("Transparent mode not supported on this platform.")
            mode = "transparent"
        if options.socks_proxy:
            c += 1
            mode = "socks5"
        if options.reverse_proxy:
            c += 1
            mode = "reverse"
            upstream_server = options.reverse_proxy
        if options.upstream_proxy:
            c += 1
            mode = "upstream"
            upstream_server = options.upstream_proxy
        if c > 1:
            self.error("Transparent, SOCKS5, reverse and upstream proxy mode are mutually exclusive.")

        if options.clientcerts:
            options.clientcerts = os.path.expanduser(options.clientcerts)
            if not os.path.exists(options.clientcerts) or not os.path.isdir(options.clientcerts):
                self.error("Client certificate directory does not exist or is not a directory: %s" % options.clientcerts)

        if (options.auth_nonanonymous or options.auth_singleuser or options.auth_htpasswd):
            if options.auth_singleuser:
                if len(options.auth_singleuser.split(':')) != 2:
                    return self.error("Invalid single-user specification. Please use the format username:password")
                username, password = options.auth_singleuser.split(':')
                password_manager = http_auth.PassManSingleUser(username, password)
            elif options.auth_nonanonymous:
                password_manager = http_auth.PassManNonAnon()
            elif options.auth_htpasswd:
                try:
                    password_manager = http_auth.PassManHtpasswd(options.auth_htpasswd)
                except ValueError, v:
                    return self.error(v.message)
            authenticator = http_auth.BasicProxyAuth(password_manager, "mitmproxy")
        else:
            authenticator = http_auth.NullProxyAuth(None)

        certs = []
        for i in options.certs:
            parts = i.split("=", 1)
            if len(parts) == 1:
                parts = ["*", parts[0]]
            parts[1] = os.path.expanduser(parts[1])
            if not os.path.exists(parts[1]):
                self.error("Certificate file does not exist: %s" % parts[1])
            certs.append(parts)

        ssl_ports = options.ssl_ports
        if options.ssl_ports != TRANSPARENT_SSL_PORTS:
            ssl_ports = ssl_ports[len(TRANSPARENT_SSL_PORTS):]

        return ProxyConfig(
            host=options.addr,
            port=int(options.port),
            confdir=options.confdir,
            clientcerts=options.clientcerts,
            no_upstream_cert=options.no_upstream_cert,
            mode=mode,
            upstream_server=upstream_server,
            ignore_hosts=options.ignore_hosts,
            tcp_hosts=options.tcp_hosts,
            authenticator=authenticator,
            ciphers=options.ciphers,
            certs=certs,
            certforward=options.certforward,
            ssl_ports=ssl_ports
        )

    def error(self, msg):
        print msg
        sys.exit(1)


class Config(object):
        def __init__(self, adict):
            self.__dict__ = {
                "addr": '',
                "ignore_hosts": [],
                "tcp_hosts": [],
                "port": 8080,
                "reverse_proxy": None,
                "socks_proxy": False,
                "transparent_proxy": False,
                "upstream_proxy": None,
                "certs": [],
                "clientcerts": None,
                "ciphers":None,
                "certforward": False,
                "no_upstream_cert": False,
                "confdir": "~/.mitmproxy",
                "ssl_ports": list(TRANSPARENT_SSL_PORTS)
            }
            self.__dict__.update(adict)

        def __getattr__(self, item):
            if not item in self.__dict__:
                return None
            return object.__getattribute__(self, item)