from io import BytesIO, BufferedReader
import boto3
from typing import IO, List, Tuple
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

    def _folder_exists(path: str) -> bool:
        path = path.rstrip('/')
        objects = S3Adapter.client.list_objects(
            Bucket = S3Config.bucket,
            Prefix = path,
            Delimiter = '/',
            MaxKeys = 1)
        return 'CommonPrefixes' in objects

    def _bucket_objects(path: str = None):
        '''
        Return collection of bucket objects filtered optionally by key prefix
        '''
        bucket = S3Adapter.resource.Bucket(S3Config.bucket)
        if path:
            return bucket.objects.filter(Prefix=path).all()
        else:
            return bucket.objects.all()

    ###########################################################################

    def list_datasets() -> List[Dataset]:
        '''
        List all datasets in the S3 bucket
        '''
        datasets = []
        datasets_names = set()
        for bucket_object in S3Adapter._bucket_objects():
            dataset_name = bucket_object.key.split('/')[0]
            datasets_names.add(dataset_name)
        for dataset_name in sorted(list(datasets_names)):
            dataset = Dataset(dataset_name)
            datasets.append(dataset)
        return datasets

    def dataset_exists(name: str) -> bool:
        '''
        Checks if a dataset exists
        '''
        return S3Adapter._folder_exists(name)

    def create_dataset(dataset_name: str) -> None:
        S3Adapter.client.put_object(
            Bucket = S3Config.bucket,
            Key = (f'/{dataset_name}/'))

    def read_dataset(dataset_name: str) -> Dataset:
        '''
        Read dataset data
        '''
        dataset = Dataset(dataset_name)
        return dataset

    ###########################################################################

    def list_dataset_variants(dataset_name: str) -> List[DatasetVariant]:
        '''
        List dataset variants
        '''
        variants: List[DatasetVariant] = []
        variants_names = set()
        for bucket_object in S3Adapter._bucket_objects(f'{dataset_name}/variants'):
            variant_name = bucket_object.key.split('/')[2]
            variants_names.add(variant_name)
        for variant_name in sorted(list(variants_names)):
            variant = DatasetVariant(variant_name, dataset_name)
            variants.append(variant)
        return variants

    def dataset_variant_exists(dataset_name: str, variant_name: str) -> bool:
        '''
        Checks if a dataset exists
        '''
        return S3Adapter._folder_exists(f'{dataset_name}/variants/{variant_name}')

    def read_dataset_variant(dataset_name: str, variant_name: str) -> DatasetVariant:
        '''
        Read dataset variant
        '''
        variant = DatasetVariant(variant_name, dataset_name)
        return variant

    def create_dataset_variant(dataset_name: str, variant_name: str) -> None:
        '''
        Create dataset variant
        '''
        S3Adapter.client.put_object(
            Bucket = S3Config.bucket,
            Key = (f'/{dataset_name}/variants/{variant_name}/'))

    ###########################################################################

    def list_dataset_variant_data(dataset_name: str, variant_name: str) -> List[DatasetVariantData]:
        '''
        List dataset variant files
        '''
        data_list: List[DatasetVariantData] = []
        for bucket_object in S3Adapter._bucket_objects(f'{dataset_name}/variants/{variant_name}'):
            key_parts = bucket_object.key.split('/')
            filename = key_parts[3]
            if filename:
                data = DatasetVariantData(filename, dataset_name, variant_name, bucket_object.Object().content_type, bucket_object.size)
                data_list.append(data)
        return data_list

    def save_dataset_variant_data(dataset_name: str, variant_name: str, content_type: str, filename: str, contents: IO[bytes]):
        '''
        Create or update dataset variant file
        '''
        S3Adapter.client.upload_fileobj(
            contents,
            S3Config.bucket,
            f'{dataset_name}/variants/{variant_name}/{filename}',
            ExtraArgs = {'ContentType': content_type})

    def read_dataset_variant_data(dataset_name: str, variant_name: str, filename: str) -> Tuple[str, BufferedReader]: 
        '''
        Read dataset variant file
        '''
        object = S3Adapter.resource.Object(
            S3Config.bucket,
            f'{dataset_name}/variants/{variant_name}/{filename}').get()
        return object['ContentType'], BufferedReader(object['Body']._raw_stream)