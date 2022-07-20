import boto3
from typing import List, Tuple
from botocore.response import StreamingBody
from werkzeug.datastructures import FileStorage
from app.config.s3config import S3Config
from app.model import Dataset, DatasetVariant, DatasetVariantData


class S3Adapter:

    client = boto3.client(
                's3',
                endpoint_url = f'http://{S3Config.host}:{S3Config.port}',
                aws_access_key_id = S3Config.auth_key_id,
                aws_secret_access_key = S3Config.auth_secret_key)

    resource = boto3.resource(
                's3',
                endpoint_url = f'http://{S3Config.host}:{S3Config.port}',
                aws_access_key_id = S3Config.auth_key_id,
                aws_secret_access_key = S3Config.auth_secret_key)

    def _bucket_objects(path: str = None):
        '''
        Return collection of bucket objects filtered optionally by key prefix
        '''
        bucket = S3Adapter.resource.Bucket(S3Config.bucket)
        if path:
            return bucket.objects.filter(Prefix=path).all()
        else:
            return bucket.objects.all()

    def list_datasets() -> List[Dataset]:
        '''
        List all datasets in the S3 bucket
        '''
        datasets = []
        datasets_names = set()
        for bucket_object in S3Adapter._bucket_objects():
            key_parts = bucket_object.key.split('/')
            dataset_name = key_parts[0]
            datasets_names.add(dataset_name)
        for dataset_name in sorted(list(datasets_names)):
            dataset = Dataset(dataset_name)
            datasets.append(dataset)
        return datasets

    def read_dataset(dataset_name: str) -> Dataset:
        '''
        Read dataset data with a list of variants (without data)
        '''
        dataset = Dataset(dataset_name)
        variants_names = set()
        for bucket_object in S3Adapter._bucket_objects(f'{dataset_name}/variants'):
            key_parts = bucket_object.key.split('/')
            variant_name = key_parts[2]
            variants_names.add(variant_name)
        for variant_name in sorted(list(variants_names)):
            variant = DatasetVariant(variant_name, dataset_name)
            dataset.variants.append(variant)
        return dataset

    def create_dataset(dataset_name: str) -> None:
        S3Adapter.client.put_object(
            Bucket = S3Config.bucket,
            Key = (f'/{dataset_name}/'))

    def read_dataset_variant(dataset_name: str, variant_name: str) -> DatasetVariant:
        '''
        Read dataset variant with a list of data
        '''
        variant = DatasetVariant(variant_name, dataset_name)
        for bucket_object in S3Adapter._bucket_objects(f'{dataset_name}/variants/{variant_name}'):
            key_parts = bucket_object.key.split('/')
            filename = key_parts[3]
            if filename:
                data = DatasetVariantData(filename, dataset_name, variant_name, bucket_object.Object().content_type, bucket_object.size)
                variant.data.append(data)
        return variant

    ###

    def put_folder(path):
        S3Adapter.client.put_object(
            Bucket = S3Config.bucket,
            Key = (f'/{path}/'))

    def list_folders(path: str):
        pass        

    def get_all():
        objects_list = S3Adapter.client.list_objects(
                Bucket = S3Config.bucket
            )
        objects = []
        for index, object in enumerate(objects_list.get('Contents')):
            objects.append(S3Adapter.resource.Object(
                S3Config.bucket,
                object.get('Key')
            ))
        return objects

    def get_root_folders():
        objects = S3Adapter.client.list_objects(
            Bucket = S3Config.bucket,
            Delimiter = '/')
        folders = [ item['Prefix'].strip('/') for item in objects['CommonPrefixes'] ] if 'CommonPrefixes' in objects else []
        return folders

    def folder_exists(path:str) -> bool:
        path = path.rstrip('/')
        objects = S3Adapter.client.list_objects(
            Bucket = S3Config.bucket,
            Prefix = path,
            Delimiter = '/',
            MaxKeys = 1)
        return 'CommonPrefixes' in objects

    def get_files_and_folers(path):
        objects = S3Adapter.client.list_objects(
            Bucket = S3Config.bucket,
            Prefix = f'{path}/')
        files = [ item['Key'][len(f'{path}/'):] for item in objects['Contents'] if item['Key'] != f'{path}/' ] if 'Contents' in objects else []
        return sorted(files)

    def upload_file(path: str, file: FileStorage):
        S3Adapter.client.upload_fileobj(
            file.stream,
            S3Config.bucket,
            path,
            ExtraArgs = {'ContentType': file.mimetype})

    def get_file(path: str) -> Tuple[str, StreamingBody]: 
        object = S3Adapter.resource.Object(
            S3Config.bucket,
            path).get()
        return object['ContentType'], object['Body']