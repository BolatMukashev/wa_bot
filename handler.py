"""
Yandex Cloud Function — загрузка файлов в Yandex Object Storage.

Переменные окружения (задаются в настройках функции):
  BUCKET_NAME           — имя бакета (обязательно)
  LOCAL_RUN             — "true" для локального запуска (по умолчанию false)

  Только при LOCAL_RUN=true (статический ключ доступа):
  AWS_ACCESS_KEY_ID     — идентификатор ключа
  AWS_SECRET_ACCESS_KEY — секретный ключ

  В облаке ключи не нужны — boto3 получает IAM-токен автоматически
  через метадата-сервис сервисного аккаунта (роль storage.uploader).
"""

import base64
import json
import logging
import mimetypes
import os
import uuid

from config import BUCKET_NAME, ENDPOINT_URL, IS_LOCAL, MAX_FILE_SIZE, REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# ── S3-клиент ──────────────────────────────────────────────────────────────────
def _get_s3_client():
    """
    Создаёт клиент boto3 для Yandex Object Storage.

    Локально (LOCAL_RUN=true): явно передаёт ключи из переменных окружения.
    В облаке: ключи не передаются — boto3 получает IAM-токен автоматически
    через метадата-сервис сервисного аккаунта.
    """
    session = boto3.session.Session()
    kwargs = dict(
        service_name="s3",
        endpoint_url=ENDPOINT_URL,
        region_name=REGION,
        config = Config(signature_version="s3v4",          # ← обязательно для Yandex
                        retries={"max_attempts": 3, "mode": "standard"},)
    )
    if IS_LOCAL:
        kwargs["aws_access_key_id"] = AWS_ACCESS_KEY_ID
        kwargs["aws_secret_access_key"] = AWS_SECRET_ACCESS_KEY

    return session.client(**kwargs)


s3 = _get_s3_client()


# ── Основная логика ────────────────────────────────────────────────────────────
def upload_bytes(
    data: bytes,
    object_key: str | None = None,
    content_type: str = "application/octet-stream",
) -> dict:
    """
    Загружает bytes в Object Storage.

    :param data:         бинарные данные файла
    :param object_key:   ключ объекта в бакете; если None — генерируется UUID
    :param content_type: MIME-тип файла
    :return:             словарь с результатом
    """
    if not object_key:
        object_key = str(uuid.uuid4())

    if len(data) > MAX_FILE_SIZE:
        raise ValueError(f"Файл слишком большой: {len(data)} байт (макс. {MAX_FILE_SIZE})")

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=object_key,
        Body=data,
        ContentType=content_type,
    )
    url = f"{ENDPOINT_URL}/{BUCKET_NAME}/{object_key}"
    logger.info("Загружен объект: %s (%d байт)", url, len(data))
    return {"object_key": object_key, "url": url, "size": len(data)}


# ── Точка входа Cloud Function ────────────────────────────────────────────────
def handler(event: dict, context=None) -> dict:
    """
    Обработчик Yandex Cloud Function.

    Ожидаемый формат event:
    {
      "file_base64": "<base64-строка>",  # обязательно
      "file_name":   "report.pdf",       # необязательно, используется для определения MIME-типа
      "object_key":  "folder/file.pdf"   # необязательно, по умолчанию генерируется UUID
    }
    """
    try:
        if "file_base64" not in event:
            return _error(400, "Отсутствует обязательное поле: file_base64")

        data = base64.b64decode(event["file_base64"])

        file_name = event.get("file_name", "")
        content_type, _ = mimetypes.guess_type(file_name)
        content_type = content_type or "application/octet-stream"

        result = upload_bytes(data, event.get("object_key"), content_type)

        return {
            "statusCode": 200,
            "body": json.dumps({"status": "ok", **result}, ensure_ascii=False),
        }

    except (BotoCoreError, ClientError) as exc:
        logger.exception("Ошибка S3")
        return _error(502, f"Ошибка Object Storage: {exc}")
    except ValueError as exc:
        logger.warning("Ошибка валидации: %s", exc)
        return _error(400, str(exc))
    except Exception as exc:  # noqa: BLE001
        logger.exception("Непредвиденная ошибка")
        return _error(500, f"Внутренняя ошибка: {exc}")


def _error(code: int, message: str) -> dict:
    return {
        "statusCode": code,
        "body": json.dumps({"status": "error", "message": message}, ensure_ascii=False),
    }


# ── Локальный запуск для тестов ───────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # ── Укажите путь к файлу и ключ здесь ─────────────────────────────────────
    TEST_FILE = r"C:\Users\Astana\Desktop\Client\Болат\Lass mich fallen — Panik _ Перевод и текст песни.pdf"
    TEST_KEY = "7085292078/test.pdf"
    # ──────────────────────────────────────────────────────────────────────────

    if not os.path.exists(TEST_FILE):
        print(f"Файл не найден: {TEST_FILE}", file=sys.stderr)
        sys.exit(1)

    with open(TEST_FILE, "rb") as f:
        file_bytes = f.read()

    test_event = {
        "file_base64": base64.b64encode(file_bytes).decode(),
        "file_name": os.path.basename(TEST_FILE),
    }
    if TEST_KEY:
        test_event["object_key"] = TEST_KEY

    print("Отправляем событие:")
    print(json.dumps({**test_event, "file_base64": "<...>"}, ensure_ascii=False, indent=2))
    print()

    response = handler(test_event)

    print("Ответ:")
    print(json.dumps(response, ensure_ascii=False, indent=2))

