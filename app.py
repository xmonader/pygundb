from gundb.test import app
from gundb.gunrequesthandler import GUNRequestHandler
def build_app(backend):
    app.config["handler"] = GUNRequestHandler(backend)
    return app
