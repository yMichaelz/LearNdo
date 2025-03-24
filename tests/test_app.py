from http import HTTPStatus

from fastapi.testclient import TestClient  # type: ignore

from learndo.app import app


def test_read_root_returns_ok():
    client = TestClient(app)  # ARRANGE (ORGANIZAÇÃO)
    client.get("/")  # ACT (AÇÃO)
    response = client.get("/")  # ACT (AÇÃO)
    assert response.status_code == HTTPStatus.OK  # ASSERT (AFIRMAÇÃO)


def test_read_root_returns_hello_world():
    client = TestClient(app)  # ARRANGE (ORGANIZAÇÃO)
    response = client.get("/")  # ACT (AÇÃO)
    assert response.json() == {"message": "Hello World"}  # ASSERT (AFIRMAÇÃO)
