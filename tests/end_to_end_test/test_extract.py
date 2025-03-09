import json
import os
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(
    app=app,
)

auth = (os.environ["HTTP_BASIC_AUTH_USERNAME"], os.environ["HTTP_BASIC_AUTH_PASSWORD"])

url = "/api/v1/extract"
base_dir = Path(__file__).resolve().parent


def test_api_v1_extract_no_content():
    response = client.post(
        url,
        auth=auth,
    )
    assert response.status_code == 422


def test_api_v1_extract_with_content():
    pdf_path = base_dir / "data/pdf/Enfothelial dysfunction.pdf"

    with open(pdf_path, "rb") as pdf_file:
        response = client.post(
            url,
            auth=auth,
            files={
                "content": ("Enfothelial dysfunction.pdf", pdf_file, "application/pdf")
            },
        )

    assert response.status_code == 200

    response_json = response.json()
    json_path = base_dir / "data/Enfothelial dysfunction.json"
    with open(json_path, "rb") as json_file:
        expected_json = json.load(json_file)

    assert response_json == expected_json


def test_api_without_auth():
    response = client.post(
        url,
        auth=auth,
    )
    assert response.status_code == 422
