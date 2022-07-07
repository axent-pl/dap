from flask import Flask

from app.api.api import api
from app.api.dataset import ns as dataset_ns


app = Flask(__name__)

api.add_namespace(dataset_ns)
api.init_app(app)
