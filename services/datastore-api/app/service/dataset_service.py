from typing import Tuple
from  botocore.response import StreamingBody
from dataclasses import dataclass, field
from typing import List
from werkzeug.datastructures import FileStorage
from app.adapter.s3 import S3Adapter
from botocore.exceptions import UnknownKeyError

class NotFoundException(Exception):
    pass

@dataclass
class DatasetVariantData:
    filename: str = field(default=None)
    dataset_name: str = field(default=None)
    variant_name: str = field(default=None)


@dataclass
class DatasetVariant:
    name: str = field(default=None)
    dataset_name: str = field(default=None)
    data: List[DatasetVariantData] = field(default_factory=lambda : [])


@dataclass
class Dataset:
    name: str = field(default=None)
    variants: List[DatasetVariant] = field(default_factory=lambda : [])


class DatasetService:

    def search() -> List[Dataset]:
        datasets = []
        folders = S3Adapter.get_root_folders()
        for folder in folders:
            dataset = DatasetService.read(folder)
            datasets.append(dataset)
        return datasets

    def create(name: str) -> None:
        S3Adapter.put_folder(name)

    def read(name: str) -> Dataset:
        if not S3Adapter.folder_exists(name): raise NotFoundException()
        dataset = Dataset()
        dataset.name = name
        dataset_contents = S3Adapter.get_files_and_folers(name)
        for item in dataset_contents:
            if item.startswith('variants/') and item.endswith('/'):
                dataset_variant = DatasetVariant(item[len('variants/'):-1], name)
                dataset.variants.append(dataset_variant)
        return dataset

    def read_variant(dataset_name: str, variant_name: str) -> DatasetVariant:
        path: str = f'{dataset_name}/variants/{variant_name}'
        if not S3Adapter.folder_exists(path): raise NotFoundException()
        v = DatasetVariant()
        v.dataset_name = dataset_name
        v.name = variant_name
        s3_contens = S3Adapter.get_files_and_folers(path)
        for item in s3_contens:
            vd = DatasetVariantData()
            vd.filename = item
            vd.dataset_name = dataset_name
            vd.variant_name = variant_name
            v.data.append(vd)
        return v

    def read_data(dataset_name: str, variant_name: str, filename: str) -> Tuple[str, StreamingBody]:
        try:
            return S3Adapter.get_file(f'{dataset_name}/variants/{variant_name}/{filename}')
        except S3Adapter.client.exceptions.NoSuchKey:
            raise NotFoundException()

    def put_input_file(name: str, file: FileStorage) -> None:
        S3Adapter.put_folder(f'{name}/variants/input')
        S3Adapter.put_folder(f'{name}/variants/canonical')
        S3Adapter.put_folder(f'{name}/variants/series')
        S3Adapter.upload_file(f'{name}/variants/input', file)