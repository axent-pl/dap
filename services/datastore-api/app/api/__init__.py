from flask_restx import Api

from .dataset_api import ns as dataset_ns

api = Api(version='1.0', title='DAP Dataset API', description='Abstraction layer over different datastores')

api.add_namespace(dataset_ns)