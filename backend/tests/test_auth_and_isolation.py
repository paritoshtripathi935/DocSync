import os
import sys
import time

import fakeredis
import mongomock
import pytest
from fastapi.testclient import TestClient
from jose import jwt
from jose.backends import RSAKey

BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND)
os.environ.setdefault("MONGO_URI", "mongodb://x")
os.environ.setdefault("REDIS_URI", "redis://x")
os.environ.pop("CLERK_JWT_ISSUER", None)

import src.database.connectors.mongo_connector as mc  # noqa: E402
import src.database.connectors.redis_connector as rc  # noqa: E402

DB, REDIS = mongomock.MongoClient()["t"], fakeredis.FakeRedis()
mc.get_mongo_instance = lambda: DB
rc.get_redis_client = lambda: REDIS

import main  # noqa: E402
import src.utils.auth as auth  # noqa: E402
from cryptography.hazmat.primitives.asymmetric import rsa  # noqa: E402
from cryptography.hazmat.primitives import serialization  # noqa: E402

ISS = "https://clerk.test"
_priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_pem = _priv.private_bytes(
    serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
).decode()
_jwk = RSAKey(_priv.public_key().public_bytes(
    serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode(), "RS256").to_dict()
_jwk.update(kid="k1", use="sig")


def token(sub, iss=ISS, exp=3600, pem=_pem):
    return jwt.encode({"sub": sub, "iss": iss, "exp": int(time.time()) + exp}, pem,
                      algorithm="RS256", headers={"kid": "k1"})


def bearer(sub, **kw):
    return {"Authorization": f"Bearer {token(sub, **kw)}"}


@pytest.fixture(autouse=True)
def clean():
    DB.documents.delete_many({})
    DB.document_history.delete_many({})
    REDIS.flushall()
    auth._jwks_cache.clear()


@pytest.fixture
def client():
    return TestClient(main.app)


@pytest.fixture
def clerk(monkeypatch):
    monkeypatch.setenv("CLERK_JWT_ISSUER", ISS)
    monkeypatch.setattr(auth, "_fetch_jwks", lambda iss: {"keys": [_jwk]})


def test_auth_disabled_works(client):
    r = client.post("/v1/documents/", json={"title": "A"})
    assert r.status_code == 201
    assert client.get("/v1/documents/").json()["total"] == 1
    assert DB.documents.find_one({"id": r.json()["id"]})["owner_id"] == "local"


def test_missing_and_invalid_token_401(client, clerk):
    assert client.get("/v1/documents/").status_code == 401
    assert client.get("/v1/documents/", headers={"Authorization": "Bearer junk"}).status_code == 401
    assert client.get("/v1/documents/", headers={"Authorization": "Basic abc"}).status_code == 401
    other = rsa.generate_private_key(public_exponent=65537, key_size=2048).private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()).decode()
    assert client.get("/v1/documents/", headers=bearer("u", pem=other)).status_code == 401
    assert client.get("/v1/documents/", headers=bearer("u", iss="https://evil")).status_code == 401
    assert client.get("/v1/documents/", headers=bearer("u", exp=-10)).status_code == 401
    assert client.get("/health").status_code == 200


def test_valid_token_200(client, clerk):
    assert client.get("/v1/documents/", headers=bearer("user_a")).status_code == 200


def test_user_isolation(client, clerk):
    A, B = bearer("user_a"), bearer("user_b")
    a = client.post("/v1/documents/", json={"title": "secret", "content": "needle"}, headers=A).json()
    b = client.post("/v1/documents/", json={"title": "mine"}, headers=B).json()
    assert a["id"] != b["id"]  # global ids
    i = a["id"]
    assert client.get(f"/v1/documents/{i}", headers=A).status_code == 200  # also warms cache
    assert client.get(f"/v1/documents/{i}", headers=B).status_code == 404
    assert client.patch(f"/v1/documents/{i}", json={"title": "x"}, headers=B).status_code == 404
    assert client.get(f"/v1/documents/{i}/history", headers=B).json() == []
    assert client.delete(f"/v1/documents/{i}", headers=B).status_code == 404
    assert [d["id"] for d in client.get("/v1/documents/", headers=B).json()["items"]] == [b["id"]]
    assert client.get("/v1/documents/", params={"q": "needle"}, headers=B).json()["total"] == 0
    assert client.get("/v1/documents/", params={"q": "needle"}, headers=A).json()["total"] == 1
    # A's doc is untouched
    g = client.get(f"/v1/documents/{i}", headers=A).json()
    assert g["title"] == "secret" and g["version"] == 1
    assert len(client.get(f"/v1/documents/{i}/history", headers=A).json()) == 1
    assert client.delete(f"/v1/documents/{i}", headers=A).status_code == 204


def test_id_race_retry(client):
    from pymongo.errors import DuplicateKeyError
    from src.utils.database.mongo_handler import MongoHandler
    orig, calls = MongoHandler.insert_one, []

    async def flaky(self, coll, doc):
        calls.append(1)
        if coll == "documents" and len(calls) == 1:
            raise DuplicateKeyError("dup")
        return await orig(self, coll, doc)

    MongoHandler.insert_one = flaky
    try:
        assert client.post("/v1/documents/", json={"title": "r"}).status_code == 201
    finally:
        MongoHandler.insert_one = orig
