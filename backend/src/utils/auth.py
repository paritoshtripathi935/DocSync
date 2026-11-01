"""Clerk session-JWT auth (RS256, verified against the issuer's JWKS).

If CLERK_JWT_ISSUER is unset, auth is disabled and every caller is "local".
Env is read per call so config changes (and tests) take effect immediately.
"""
import logging
import os
import time
from typing import Any, Dict, Optional, Tuple

import httpx
from fastapi import Header, HTTPException
from jose import jwt
from jose.exceptions import JWTError

LOCAL_USER = "local"
_jwks_cache: Dict[str, Tuple[float, Dict[str, Any]]] = {}


class ClerkAuthError(Exception):
    pass


def issuer() -> str:
    return os.getenv("CLERK_JWT_ISSUER", "").strip()


def _fetch_jwks(iss: str) -> Dict[str, Any]:
    cached = _jwks_cache.get(iss)
    if cached and cached[0] > time.time():
        return cached[1]
    url = iss.rstrip("/") + "/.well-known/jwks.json"
    try:
        resp = httpx.get(url, timeout=5.0)
        resp.raise_for_status()
        jwks = resp.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise ClerkAuthError(f"Could not fetch JWKS from {url}: {exc}") from exc
    _jwks_cache[iss] = (time.time() + int(os.getenv("CLERK_JWKS_TTL_SECONDS", "3600")), jwks)
    return jwks


def _key_for_kid(jwks: Dict[str, Any], kid: str) -> Optional[Dict[str, Any]]:
    return next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)


def verify_clerk_jwt(token: str) -> Dict[str, Any]:
    iss = issuer()
    try:
        kid = jwt.get_unverified_header(token).get("kid")
    except JWTError as exc:
        raise ClerkAuthError(f"Malformed token: {exc}") from exc
    if not kid:
        raise ClerkAuthError("Token header missing kid")

    key = _key_for_kid(_fetch_jwks(iss), kid)
    if key is None:  # signing key may have rotated: refresh once
        _jwks_cache.pop(iss, None)
        key = _key_for_kid(_fetch_jwks(iss), kid)
        if key is None:
            raise ClerkAuthError(f"No JWKS key for kid={kid}")
    try:
        claims = jwt.decode(token, key, algorithms=["RS256"], issuer=iss, options={"verify_aud": False})
    except JWTError as exc:
        raise ClerkAuthError(f"Token verification failed: {exc}") from exc
    if not claims.get("sub"):
        raise ClerkAuthError("Token missing sub claim")
    return claims


def get_user_id(authorization: Optional[str] = Header(default=None)) -> str:
    """FastAPI dependency: the caller's Clerk user id (`sub`), or "local" if auth is off."""
    if not issuer():
        return LOCAL_USER
    if not authorization or not authorization.startswith("Bearer ") or not authorization[7:].strip():
        raise HTTPException(status_code=401, detail="Missing Bearer token")
    try:
        return verify_clerk_jwt(authorization[7:].strip())["sub"]
    except ClerkAuthError as exc:
        logging.info("Rejected invalid Clerk token: %s", exc)
        raise HTTPException(status_code=401, detail="Invalid token") from exc
