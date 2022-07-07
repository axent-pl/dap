from typing import List
from werkzeug.datastructures import FileStorage
from app.adapter.s3 import S3Adapter

class Dataset:

    def search() -> List[dict]:
        datasets = []
        folders = S3Adapter.get_root_folders()
        for folder in folders:
            dataset = Dataset.read(folder)
            datasets.append(dataset)
        return datasets

    def create(name: str) -> None:
        S3Adapter.put_folder(name)

    def read(name: str) -> dict:
        dataset = {}
        dataset['name'] = name
        dataset_contents = S3Adapter.get_files_and_folers(name)
        dataset['raw-data'] = [ item[len('raw/'):] for item in dataset_contents if item.startswith('raw/') ]
        return dataset

    def put_input_file(name: str, file: FileStorage) -> None:
        S3Adapter.upload_file(f'{name}/raw', file)