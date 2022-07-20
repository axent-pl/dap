from typing import Tuple
from  botocore.response import StreamingBody
from typing import List
from werkzeug.datastructures import FileStorage
from app.adapter.s3 import S3Adapter
from botocore.exceptions import UnknownKeyError
from app.model import Dataset, DatasetVariant, DatasetVariantData

class NotFoundException(Exception):
    pass

class DatasetService:

    def list() -> List[Dataset]:
        '''
        List datasets
        '''
        return S3Adapter.list_datasets()

    def create(name: str) -> None:
        '''
        Create dataset
        '''
        S3Adapter.create_dataset(name)

    def read(name: str) -> Dataset:
        '''
        Read dataset with with variants list
        '''
        if not S3Adapter.folder_exists(name): raise NotFoundException()
        return S3Adapter.read_dataset(name)

    def read_variant(dataset_name: str, variant_name: str) -> DatasetVariant:
        if not S3Adapter.folder_exists(f'{dataset_name}/variants/{variant_name}'): raise NotFoundException()
        return S3Adapter.read_dataset_variant(dataset_name, variant_name)

    def read_data(dataset_name: str, variant_name: str, filename: str) -> Tuple[str, StreamingBody]:
        try:
            return S3Adapter.get_file(f'{dataset_name}/variants/{variant_name}/{filename}')
        except S3Adapter.client.exceptions.NoSuchKey:
            raise NotFoundException()

    def put_file(dataset_name: str, variant_name: str, filename: str, file: FileStorage) -> None:
        S3Adapter.put_folder(f'{dataset_name}/variants/{variant_name}')
        S3Adapter.upload_file(f'{dataset_name}/variants/{variant_name}/{filename}', file)
