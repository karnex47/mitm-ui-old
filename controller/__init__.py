from libmproxy import flow
from PyQt4 import QtCore
from copy import deepcopy

class ControllerMaster(flow.FlowMaster):
    def __init__(self, server, state, options):
        flow.FlowMaster.__init__(self, server, state)
        if not options:
            options = []

    def run(self):
        try:
            flow.FlowMaster.run(self)
        except KeyboardInterrupt:
            self.shutdown()

    def handle_request(self, f):
        flow.FlowMaster.handle_request(self, f)

        auto_response = self.state.get_auto_response_data(f.request.url)
        if auto_response and auto_response['active']:
            response = deepcopy(auto_response['response'])
            response_headers = []
            for key, value in response.headers:
                if key == "Content-Length":
                    response_headers.append(["Content-Length", len(response.content)])
                elif key == 'Cache-Control' or key == 'Pragma' or key == 'Expires':
                    continue
                else:
                    response_headers.append([key, value])

            response_headers.append(['Cache-Control', 'no-cache, no-store, must-revalidate'])
            response_headers.append(['Pragma', 'no-cache'])
            response_headers.append(['Expires', '0'])
            response.headers = flow.ODictCaseless(response_headers)
            f.reply(response)

        elif f:
            f.reply()

    def handle_response(self, f):
        flow.FlowMaster.handle_response(self, f)
        if f:
            f.reply()

    def get_headers(self, conn):
        hdr_items = tuple(tuple(i) for i in conn.headers.lst)
        return flow.ODictCaseless([list(i) for i in hdr_items])



class ControllerState(flow.State, QtCore.QObject):
    def __init__(self):
        flow.State.__init__(self)
        QtCore.QObject.__init__(self)
        self._replay = []
        self._auto_respond = {}

    def set_data_from_saved_state(self, saved_sate):
        self._auto_respond = saved_sate['auto_response']
        self._replay = saved_sate['replay']

    def add_request(self, f):
        ret = flow.State.add_request(self, f)
        self.update_view(self.view.index(f), 'add')
        return ret

    def add_response(self, f):
        ret = flow.State.add_response(self, f)
        self.update_view(self.view.index(f), 'update')
        return ret

    def add_error(self, f):
        ret = flow.State.add_error(self, f)
        self.update_view(self.view.index(f), 'update')
        return ret

    def recalculate_view(self):
        ret = flow.State.recalculate_view(self)
        self.update_view()
        return ret

    def delete_flow(self, f):
        index = self.view.index(f)
        ret = flow.State.delete_flow(self, f)
        self.update_view(index, 'delete')
        return ret

    def update_view(self, index=None, mode=''):
        self.emit(QtCore.SIGNAL('UPDATE_LIST'), index, mode)

    def get_auto_response_keys(self):
        return self._auto_respond.keys()

    def add_auto_response(self, key, value):
        self._auto_respond[key] = value

    def remove_auto_response(self, key):
        self._auto_respond.pop(key, None)

    def get_auto_response_data(self, key):
        try:
            return self._auto_respond[key]
        except KeyError:
            return False

    def set_auto_response_active(self, key, active):
        self._auto_respond[key]['active'] = bool(active)

    def set_auto_response(self, key, response):
        self._auto_respond[key]['response'] = response

    def get_cached_response(self, key):
        return self._auto_respond[key]['response']

    def set_content_file_path(self, key, file_path):
        self._auto_respond[key]['file'] = file_path

    def get_content_file_path(self, key):
        return self._auto_respond[key]['file']

    def replace_auto_response_key(self, oldKey, newKey):
        value = deepcopy(self._auto_respond[oldKey])
        self.remove_auto_response(oldKey)
        self.add_auto_response(newKey, value)