import json

from geventwebsocket import WebSocketApplication


class GeventGunServer(WebSocketApplication):
    """
    Gevent server that handles gun requests.
    It should be initialized with websockcets and a handler that processes the message.

    Args:
        ws (Object): wsgi websocket object.
        handler (Object): An object having the methods process_message, add_peer, remove_peer.
            And peers property.

    """

    def __init__(self, handler, ws):
        super().__init__(ws)
        self.handler = handler

    def on_open(self, *args, **kwargs):
        """Adds the newly created peer to the currents."""
        print("Got client connection")
        self.handler.add_peer(self.ws)

    def on_message(self, message, *args, **kwargs):
        """Processes the incoming message.
        It passes the message to the handler to update the backend db.

        Args:
            message (str): The incoming message.
        """
        if message is not None:
            self.handler.process_message(message)

    def on_close(self, *args, **kwargs):
        """Called on connection termination to remove the pee0r from the currents."""
        reason = args[0] if args else ""
        self.handler.remove_peer(self.ws)
        print("Peers now: {}".format(self.handler.peers))
        print(reason)

    def sendall(self, *args, **kwargs):
        """Send the message in the first argunent to all the current peers."""
        resp = args[0] if args else ""
        for client in self.ws.handler.server.clients.values():
            client.ws.send(json.dumps(resp))


class AppRunner:
    def __init__(self, app, handler):
        self.app = app
        self.handler = handler

    def __call__(self, environ, start_response):
        """Called when a new connection is established. Forwards the request to self.handler object.
        
        Args:
            environ (dict): Enviornment passwd be gevent websocket server
            start_response (function): Provided by wsgi server to interact with the peer (not used).
        
        Returns:
            list: just an empty list. All user interactions is done in self.handler in the websocket session.
        """
        is_websocket_call = "wsgi.websocket" in environ
        current_app = self.app

        if is_websocket_call:
            ws = environ["wsgi.websocket"]
            current_app = current_app(ws, self.handler)
            current_app.handle()
        return []
