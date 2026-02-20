import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")

ENDPOINTS = {
    "upload_free_text": "/api/rfq/upload-free-text",
    "upload_url_html": "/api/rfq/upload-url-html"
}

HEADERS = {
    "Authorization": f"ApiKey {API_KEY}",
    "Content-Type": "application/json"
}