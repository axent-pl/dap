from io import BufferedReader
import random
import string
from mimetypes import guess_extension
from typing import IO, Tuple
from botocore.response import StreamingBody
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
        List variant files
        '''
        if not S3Adapter.dataset_exists(dataset_name): raise DatasetNotFoundException()
        if not S3Adapter.dataset_variant_exists(dataset_name, variant_name): raise DatasetVariantNotFoundException()
        return S3Adapter.list_dataset_variant_data(dataset_name, variant_name)

    def create(dataset_name: str, variant_name: str, content_type: str, contents: IO[bytes]) -> None:
        '''
        Create variant file
        '''
        random_name: str = ''.join(random.choice(string.ascii_letters) for _ in range(16))
        extension: str = guess_extension(content_type)
        filename = f'{random_name}{extension}'
        S3Adapter.save_dataset_variant_data(dataset_name, variant_name, content_type, filename, contents)

    def save(dataset_name: str, variant_name: str, content_type: str, filename: str, contents: IO[bytes]) -> None:
        '''
        Create or update variant file
        '''
        S3Adapter.save_dataset_variant_data(dataset_name, variant_name, content_type, filename, contents)

    def read(dataset_name: str, variant_name: str, filename: str) -> Tuple[str, BufferedReader]:
        '''
        Read variant file
        '''
        return S3Adapter.read_dataset_variant_data(dataset_name, variant_name, filename)
