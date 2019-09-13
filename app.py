from gundb.server import app
from gundb.gunrequesthandler import GUNRequestHandler

def build_app(backend):
    app.config["handler"] = GUNRequestHandler(app, backend)
    return app
