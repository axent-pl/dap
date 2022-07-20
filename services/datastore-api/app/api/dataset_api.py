from flask import url_for, send_file, jsonify
from flask_restx import Namespace, Resource, fields
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import BadRequest
from app.service.dataset_service import DatasetService, NotFoundException

ns = Namespace('dataset', description='Dataset operations')

dataset_variant_data_model = ns.model('DatasetVariantData',{
    'filename' : fields.String(required=True, description='Filename'),
    'content_type' : fields.String(required=True, description='Content type'),
    'size' : fields.String(required=True, description='Size in bytes'),
    'uri' : fields.String(attribute=lambda vd: url_for('dataset_dataset_variant_data_resource', dataset_name=vd.dataset_name, variant_name=vd.variant_name, filename=vd.filename, _external=True)),
})

dataset_variant_list_model = ns.model('DatasetVariant', {
    'name' : fields.String(required=True, description='Dataset variant name'),
    'uri' : fields.String(attribute=lambda v: url_for('dataset_dataset_variant_resource', dataset_name=v.dataset_name, variant_name=v.name, _external=True)),
})

dataset_variant_model = ns.model('DatasetVariant', {
    'name' : fields.String(required=True, description='Dataset variant name'),
    'uri' : fields.String(attribute=lambda v: url_for('dataset_dataset_variant_resource', dataset_name=v.dataset_name, variant_name=v.name, _external=True)),
    'data' : fields.Nested(dataset_variant_data_model, skip_none=True)
})

dataset_List_model = ns.model('Dataset', {
    'name' : fields.String(required=True, description='Dataset name'),
    'uri' : fields.String(attribute=lambda d: url_for('dataset_dataset_resource', dataset_name=d.name, _external=True))
})

dataset_input_model = ns.model('Dataset', {
    'name' : fields.String(required=True, description='Dataset name')
})

dataset_model = ns.model('Dataset', {
    'name' : fields.String(required=True, description='Dataset name'),
    'uri' : fields.String(attribute=lambda d: url_for('dataset_dataset_resource', dataset_name=d.name, _external=True)),
    'variants' : fields.Nested(dataset_variant_list_model, skip_none=True)
})

data_post_parser = ns.parser()
data_post_parser.add_argument('file', location='files', type=FileStorage, required=True)


@ns.errorhandler(NotFoundException)
def handle_dataset_not_found_exception(error):
    return {'message': 'Not found'}, 404


@ns.route('/')
class DatasetResourceList(Resource):

    @ns.doc('Get dataset list')
    @ns.marshal_list_with(dataset_List_model, skip_none=True)
    def get(self):
        datasets = DatasetService.list()
        return datasets

    @ns.expect(dataset_input_model)
    def put(self):
        dataset_name: str = ns.payload.get('name')
        DatasetService.create(dataset_name)


@ns.route('/<string:dataset_name>')
class DatasetResource(Resource):

    @ns.marshal_with(dataset_model, skip_none=True)
    @ns.response(404, "Dataset not found")
    def get(self, dataset_name):
        dataset = DatasetService.read(dataset_name)
        return dataset


@ns.route('/<string:dataset_name>/<string:variant_name>')
class DatasetVariantResource(Resource):

    @ns.marshal_with(dataset_variant_model, skip_none=True)
    @ns.response(404, "Dataset variant not found")
    def get(self, dataset_name, variant_name):
        dataset_variant = DatasetService.read_variant(dataset_name, variant_name)
        return dataset_variant

@ns.route('/<string:dataset_name>/<string:variant_name>/<string:filename>')
class DatasetVariantDataResource(Resource):

    def get(self, dataset_name, variant_name, filename):
        file_type, file = DatasetService.read_data(dataset_name, variant_name, filename)
        return send_file(file, mimetype=file_type)

    @ns.expect(data_post_parser)
    def put(self, dataset_name, variant_name, filename):
        args = data_post_parser.parse_args()
        file = args['file']
        DatasetService.put_file(dataset_name, variant_name, filename, file)