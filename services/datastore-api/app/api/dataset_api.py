from flask import url_for, send_file, jsonify
from flask_restx import Namespace, Resource, fields
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import BadRequest
from app.service.dataset_service import DatasetService, DatasetVariantService, DatasetVariantDataService, DatasetNotFoundException, DatasetExistsException, DatasetVariantExistsException

ns = Namespace('dataset', description='Dataset operations')


dataset_variant_data_model = ns.model('DatasetVariantData',{
    'filename' : fields.String(required=True, description='Filename'),
    'content_type' : fields.String(required=True, description='Content type'),
    'size' : fields.String(required=True, description='Size in bytes'),
    'url' : fields.String(attribute=lambda vd: url_for('dataset_dataset_variant_data_resource', dataset_name=vd.dataset_name, variant_name=vd.variant_name, filename=vd.filename, _external=True))
})


dataset_variant_model = ns.model('DatasetVariant', {
    'name' : fields.String(required=True, description='Dataset variant name'),
    'url' : fields.String(attribute=lambda v: url_for('dataset_dataset_variant_resource', dataset_name=v.dataset_name, variant_name=v.name, _external=True)),
    'dataset_url' : fields.String(attribute=lambda v: url_for('dataset_dataset_resource', dataset_name=v.dataset_name, _external=True)),
    'data_list_url' : fields.String(attribute=lambda v: url_for('dataset_dataset_variant_data_resource_list', dataset_name=v.dataset_name, variant_name=v.name, _external=True))
})


dataset_variant_input_model = ns.model('DatasetVariant', {
    'name' : fields.String(required=True, description='Dataset variant name')
})


dataset_model = ns.model('Dataset', {
    'name' : fields.String(required=True, description='Dataset name'),
    'url' : fields.String(attribute=lambda d: url_for('dataset_dataset_resource', dataset_name=d.name, _external=True)),
    'variants_url' : fields.String(attribute=lambda d: url_for('dataset_dataset_variant_resource_list', dataset_name=d.name, _external=True))
})


dataset_input_model = ns.model('Dataset', {
    'name' : fields.String(required=True, description='Dataset name')
})


data_post_parser = ns.parser()
data_post_parser.add_argument('file', location='files', type=FileStorage, required=True)


@ns.errorhandler(DatasetNotFoundException)
def handle_dataset_not_found_exception(error):
    return {'message': 'Dataset not found'}, 404


@ns.errorhandler(DatasetExistsException)
def handle_dataset_exists_exception(error):
    return {'message': 'Dataset already exists'}, 409


@ns.errorhandler(DatasetVariantExistsException)
def handle_dataset_variant_not_found_exception(error):
    return {'message': 'Dataset variant already exists'}, 409



@ns.route('/')
class DatasetResourceList(Resource):

    @ns.doc('Get dataset list')
    @ns.marshal_list_with(dataset_model, skip_none=True)
    def get(self):
        return DatasetService.list()

    @ns.expect(dataset_input_model)
    @ns.marshal_with(dataset_model, skip_none=True)
    @ns.response(409, "Dataset already exists")
    def post(self):
        dataset_name: str = ns.payload.get('name')
        DatasetService.create(dataset_name)
        return DatasetService.read(dataset_name), 201


@ns.route('/<string:dataset_name>')
class DatasetResource(Resource):

    @ns.marshal_with(dataset_model, skip_none=True)
    @ns.response(404, "Dataset not found")
    def get(self, dataset_name):
        return DatasetService.read(dataset_name)


@ns.route('/<string:dataset_name>/variants')
class DatasetVariantResourceList(Resource):

    @ns.marshal_list_with(dataset_variant_model, skip_none=True)
    @ns.response(404, "Dataset not found")
    def get(self, dataset_name):
        return DatasetVariantService.list(dataset_name)

    @ns.expect(dataset_variant_input_model)
    @ns.marshal_with(dataset_variant_model, skip_none=True)
    @ns.response(404, "Dataset not found")
    def post(self, dataset_name):
        variant_name: str = ns.payload.get('name')
        DatasetVariantService.create(dataset_name, variant_name)
        return DatasetVariantService.read(dataset_name, variant_name), 201


@ns.route('/<string:dataset_name>/variants/<string:variant_name>')
class DatasetVariantResource(Resource):

    @ns.marshal_with(dataset_variant_model, skip_none=True)
    @ns.response(404, "Dataset variant not found")
    def get(self, dataset_name, variant_name):
        return DatasetVariantService.read(dataset_name, variant_name)

@ns.route('/<string:dataset_name>/variants/<string:variant_name>/data')
class DatasetVariantDataResourceList(Resource):

    @ns.marshal_list_with(dataset_variant_data_model, skip_none=True)
    def get(self, dataset_name, variant_name):
        return DatasetVariantDataService.list(dataset_name, variant_name)

@ns.route('/<string:dataset_name>/variants/<string:variant_name>/data/<string:filename>')
class DatasetVariantDataResource(Resource):

    def get(self, dataset_name, variant_name, filename):
        file_type, file = DatasetVariantDataService.read(dataset_name, variant_name, filename)
        return send_file(file, mimetype=file_type)

    @ns.expect(data_post_parser)
    def put(self, dataset_name, variant_name, filename):
        args = data_post_parser.parse_args()
        file = args['file']
        DatasetVariantDataService.create(dataset_name, variant_name, filename, file)