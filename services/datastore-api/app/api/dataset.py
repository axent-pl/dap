
from flask import jsonify
from flask_restx import Resource, fields, reqparse
from werkzeug.datastructures import FileStorage
from app.api.api import api
from app.service.dataset import Dataset

ns = api.namespace('dataset', description='Dataset operations')

dataset_model = api.model('Dataset', {
    'name' : fields.String(required=True, description='Dataset name'),
    'raw-data' : fields.List(fields.String())
})

data_post_parser = api.parser()
data_post_parser.add_argument('file', location='files', type=FileStorage, required=True)

@ns.route('/')
class DatasetResourceList(Resource):

    @ns.doc('Get dataset list')
    @ns.marshal_list_with(dataset_model)
    def get(self):
        datasets = Dataset.search()
        ns.logger.debug(datasets)
        return datasets

    @ns.expect(dataset_model)
    def put(self):
        dataset_name: str = api.payload.get('name')
        Dataset.create(dataset_name)


@ns.route('/<string:name>')
class DatasetResource(Resource):

    @ns.marshal_with(dataset_model)
    def get(self, name):
        return Dataset.read(name)


@ns.route('/<string:name>/data')
class DatasetDataResource(Resource):

    @ns.expect(data_post_parser)
    def post(self, name):
        args = data_post_parser.parse_args()
        file = args['file']
        Dataset.put_input_file(name, file)