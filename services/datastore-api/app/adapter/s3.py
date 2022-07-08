import boto3
from typing import Tuple
from  botocore.response import StreamingBody
from werkzeug.datastructures import FileStorage
from app.config.s3config import S3Config


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

    def put_folder(path):
        S3Adapter.client.put_object(
            Bucket = S3Config.bucket,
            Key = (f'/{path}/'))

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
            f'{path}/{file.filename}',
            ExtraArgs = {'ContentType': file.mimetype})

    def get_file(path: str) -> Tuple[str, StreamingBody]: 
        object = S3Adapter.resource.Object(
            S3Config.bucket,
            path).get()
        return object['ContentType'], object['Body']