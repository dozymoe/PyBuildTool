'''
CSS-Live-Reloader notifier

see: https://github.com/sergiosgc/CSS-Live-Reloader

Requirements:

    * ws4py
      to install, run `pip install ws4py`

'''
from threading import Thread
from wsgiref.simple_server import make_server
from ws4py.websocket import WebSocket
from ws4py.server.wsgirefserver import WSGIServer, WebSocketWSGIRequestHandler
from ws4py.server.wsgiutils import WebSocketWSGIApplication

clients = set()

class BrowserReloadProtocol(WebSocket):

    def closed(self, code, reason):
        global clients
        clients.discard(self)


    def opened(self):
        global clients
        clients.add(self)
        print('css-reload client', self.peer_address)


    def received_message(self, message):
        print(message)


class BrowserReloadNotifier(object):

    host = None
    server = None
    server_thread = None

    def __init__(self, host):
        self.host = host


    def start(self):
        if self.server:
            return
        self.server = make_server(self.host, 3000, server_class=WSGIServer,
                handler_class=WebSocketWSGIRequestHandler,
                app=WebSocketWSGIApplication(handler_cls=BrowserReloadProtocol))
        self.server.initialize_websockets_manager()
        self.server_thread = Thread(target=self.server.serve_forever)
        self.server_thread.start()


    def stop(self):
        if self.server is None:
            return
        for client in clients:
            client.close()
        self.server.shutdown()
        self.server_thread.join()


    def trigger(self):
        for client in clients:
            client.send('notification\n')
