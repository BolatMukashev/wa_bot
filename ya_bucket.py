import boto3
import logging
from botocore.client import Config
from config import ACCESS_KEY, SECRET_KEY, BUCKET_NAME
from metadata import get_pdf_pages


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
        pages = get_pdf_pages(file_name)
        key = f"{phone}/{file_name}"
        self.s3.upload_file(file_name, self.bucket, key, ExtraArgs={"Metadata": {"pages": str(pages)}})
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
            if name:
                try:
                    pages = self.get_file_pages(phone, name)
                except Exception as e:
                    pages = 0
                finally:
                    files.append({name: pages})

        return files
    
    def get_file_pages(self, phone: str, file_name: str) -> int:
        key = f"{phone}/{file_name}"
        response = self.s3.head_object(
            Bucket=self.bucket,
            Key=key
        )
        return int(response["Metadata"]["Pages"])
    
    def delete_file(self, phone: str, file_name: str):
        key = f"{phone}/{file_name}"
        self.s3.delete_object(
            Bucket=self.bucket,
            Key=key
        )
        logger.info(f"Файл {file_name} удалён из бакета: {self.bucket}")
    
if __name__ == "__main__":
    s3 = S3Storage()

    s3.upload_file(7085292078, "Уведомление(RU).pdf")
    # s3.delete_file(7085292078, "123.txt")

    files = s3.list_files(7085292078)
    print(files)

    res = s3.get_file_pages(7085292078, "Уведомление(RU).pdf")
    print(res)