
from flask import url_for, send_file
from flask_restx import Resource, fields
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import BadRequest
from app.api.api import api
from app.service.dataset_service import DatasetService, NotFoundException

ns = api.namespace('dataset', description='Dataset operations')

dataset_variant_data_model = api.model('DatasetVariantData',{
    'filename' : fields.String(required=True, description='Data file name'),
    'uri' : fields.String(attribute=lambda vd: url_for('dataset_dataset_variant_data_resource', dataset_name=vd.dataset_name, variant_name=vd.variant_name, filename=vd.filename, _external=True)),
})

dataset_variant_model = api.model('DatasetVariant', {
    'name' : fields.String(required=True, description='Dataset variant name'),
    'uri' : fields.String(attribute=lambda v: url_for('dataset_dataset_variant_resource', dataset_name=v.dataset_name, variant_name=v.name, _external=True)),
    'data' : fields.Nested(dataset_variant_data_model, skip_none=True)
})

dataset_model = api.model('Dataset', {
    'name' : fields.String(required=True, description='Dataset name'),
    'uri' : fields.String(attribute=lambda d: url_for('dataset_dataset_resource', dataset_name=d.name, _external=True)),
    'variants' : fields.Nested(dataset_variant_model, skip_none=True)
})

data_post_parser = api.parser()
data_post_parser.add_argument('file', location='files', type=FileStorage, required=True)


@ns.errorhandler(NotFoundException)
def handle_dataset_not_found_exception(error):
    return {'message': 'Not found'}, 404


@ns.route('/')
class DatasetResourceList(Resource):

    @ns.doc('Get dataset list')
    @ns.marshal_list_with(dataset_model, skip_none=True)
    def get(self):
        datasets = DatasetService.search()
        return datasets

    @ns.expect(dataset_model)
    def put(self):
        dataset_name: str = api.payload.get('name')
        DatasetService.create(dataset_name)


@ns.route('/<string:dataset_name>')
class DatasetResource(Resource):

    @ns.marshal_with(dataset_model, skip_none=True)
    def get(self, dataset_name):
        dataset = DatasetService.read(dataset_name)
        return dataset


@ns.route('/<string:dataset_name>/<string:variant_name>')
class DatasetVariantResource(Resource):

    @ns.marshal_with(dataset_variant_model, skip_none=True)
    def get(self, dataset_name, variant_name):
        dataset_variant = DatasetService.read_variant(dataset_name, variant_name)
        return dataset_variant

    @ns.expect(data_post_parser)
    def put(self, dataset_name, variant_name):
        if variant_name != 'input':
            raise BadRequest("Method only allowed for `input` variant")
        args = data_post_parser.parse_args()
        file = args['file']
        DatasetService.put_input_file(dataset_name, file)


@ns.route('/<string:dataset_name>/<string:variant_name>/<string:filename>')
class DatasetVariantDataResource(Resource):

    def get(self, dataset_name, variant_name, filename):
        file_type, file = DatasetService.read_data(dataset_name, variant_name, filename)
        return send_file(file, mimetype=file_type)