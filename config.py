import os
from dotenv import dotenv_values


config = dotenv_values(".env")

IS_LOCAL = (os.environ.get("IS_LOCAL") or config.get("IS_LOCAL", "false")).lower() == "true"

GREEN_API_idInstance = os.environ.get("GREEN_API_idInstance") or config.get('GREEN_API_idInstance')
GREEN_API_apiToken = os.environ.get("GREEN_API_apiToken") or config.get('GREEN_API_apiToken')

wa_url = f"https://7107.api.greenapi.com/waInstance{GREEN_API_idInstance}/sendMessage/{GREEN_API_apiToken}"

GPT_KEY = os.environ.get("GPT_KEY") or config.get('GPT_KEY')


# ── Константы  для бакета ──────────────────────────────────────────────────────────────────
ENDPOINT_URL = "https://storage.yandexcloud.net"
REGION = "ru-central1"
BUCKET_NAME = os.environ.get("BUCKET_NAME") or config.get('BUCKET_NAME')
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 МБ — лимит для base64-тела события

ACCESS_KEY = os.environ.get("sa_copy_center_key_id") or config.get('sa_copy_center_key_id')
SECRET_KEY = os.environ.get("sa_copy_center_secret_key") or config.get('sa_copy_center_secret_key')