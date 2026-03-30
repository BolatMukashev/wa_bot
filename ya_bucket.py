import boto3
import logging
from botocore.client import Config
from config import ACCESS_KEY, SECRET_KEY, BUCKET_NAME


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class S3Storage:
    def __init__(self):
        self.s3 = boto3.client(
            service_name="s3",
            endpoint_url="https://storage.yandexcloud.kz",
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            region_name="ru-central1",
            config=Config(signature_version="s3v4")
        )
        self.bucket = BUCKET_NAME

    def upload_file(self, phone: str, file_name: str):
        key = f"{phone}/{file_name}"
        self.s3.upload_file(file_name, self.bucket, key)
        logger.info(f"Файл {file_name} загружен в бакет: {self.bucket}/{key}")

    def list_files(self, phone: str) -> list[str]:
        prefix = f"{phone}/"
        response = self.s3.list_objects_v2(
            Bucket=self.bucket,
            Prefix=prefix
        )

        files = []
        for obj in response.get("Contents", []):
            name = obj["Key"].removeprefix(prefix)
            if name:  # чтобы не было пустого элемента
                files.append(name)

        return files
    
if __name__ == "__main__":
    s3 = S3Storage()
    files = s3.list_files(7085292078)
    print(files)