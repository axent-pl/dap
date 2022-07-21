from typing import Tuple
from  botocore.response import StreamingBody
from typing import List
from werkzeug.datastructures import FileStorage
from app.adapter.s3 import S3Adapter
from botocore.exceptions import UnknownKeyError
from app.model import Dataset, DatasetVariant, DatasetVariantData

class DatasetNotFoundException(Exception):
    pass


class DatasetExistsException(Exception):
    pass


class DatasetVariantNotFoundException(Exception):
    pass


class DatasetVariantExistsException(Exception):
    pass


class DatasetVariantDataNotFoundException(Exception):
    pass


class DatasetService:

    def list() -> List[Dataset]:
        '''
        List datasets
        '''
        return S3Adapter.list_datasets()

    def create(dataset_name: str) -> None:
        '''
        Create dataset
        '''
        if S3Adapter.dataset_exists(dataset_name): raise DatasetExistsException()
        S3Adapter.create_dataset(dataset_name)

    def read(dataset_name: str) -> Dataset:
        '''
        Read dataset
        '''
        if not S3Adapter.dataset_exists(dataset_name): raise DatasetNotFoundException()
        return S3Adapter.read_dataset(dataset_name)


class DatasetVariantService:

    def list(dataset_name: str) -> List[DatasetVariant]:
        '''
        List dataset variants
        '''
        if not S3Adapter.dataset_exists(dataset_name): raise DatasetNotFoundException()
        return S3Adapter.list_dataset_variants(dataset_name)

    def create(dataset_name: str, variant_name: str) -> DatasetVariant:
        '''
        Create dataset variant
        '''
        if not S3Adapter.dataset_exists(dataset_name): raise DatasetNotFoundException()
        if S3Adapter.dataset_variant_exists(dataset_name, variant_name): raise DatasetVariantExistsException()
        S3Adapter.create_dataset_variant(dataset_name, variant_name)

    def read(dataset_name: str, variant_name: str) -> DatasetVariant:
        '''
        Read dataset variant
        '''
        if not S3Adapter.dataset_exists(dataset_name): raise DatasetNotFoundException()
        if not S3Adapter.dataset_variant_exists(dataset_name, variant_name): raise DatasetVariantNotFoundException()
        return S3Adapter.read_dataset_variant(dataset_name, variant_name)


class DatasetVariantDataService:

    def list(dataset_name: str, variant_name: str) -> List[DatasetVariantData]:
        '''
        List dataset variants
        '''
        if not S3Adapter.dataset_exists(dataset_name): raise DatasetNotFoundException()
        if not S3Adapter.dataset_variant_exists(dataset_name, variant_name): raise DatasetVariantNotFoundException()
        return S3Adapter.list_dataset_variant_data(dataset_name, variant_name)

    def create(dataset_name: str, variant_name: str, filename: str, file: FileStorage) -> None:
        S3Adapter.create_dataset_variant(dataset_name, variant_name)
        S3Adapter.upload_file(f'{dataset_name}/variants/{variant_name}/{filename}', file)

    def read(dataset_name: str, variant_name: str, filename: str) -> Tuple[str, StreamingBody]:
        try:
            return S3Adapter.get_file(f'{dataset_name}/variants/{variant_name}/{filename}')
        except S3Adapter.client.exceptions.NoSuchKey:
            raise DatasetVariantDataNotFoundException()
