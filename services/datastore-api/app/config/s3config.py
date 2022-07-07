import os

class S3Config:
    host: str = os.environ.get('S3_HOST')
    port: str = os.environ.get('S3_PORT')
    bucket: str = os.environ.get('S3_BUCKET')
    auth_key_id: str = os.environ.get('S3_AUTH_KEY_ID')
    auth_secret_key: str = os.environ.get('S3_AUTH_SECRET_KEY')