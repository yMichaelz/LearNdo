from fastapi.testclient import TestClient # type: ignore
from learndo.app import app

client = TestClient(app)
