from datetime import datetime, timedelta
from urllib.parse import urlparse

import jwt
from passlib.context import CryptContext

SECRET_KEY = "your_secret_key_here"  # change this!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


import uuid

from fastapi import HTTPException, status
from jwt import ExpiredSignatureError


def generate_tracking_key() -> str:
    return f"trk_{uuid.uuid4().hex[:12]}"


def decode_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=401, detail="Token expired. Please login again."
        )


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_domain(origin: str | None, referer: str | None):
    url = origin or referer
    if not url:
        return None
    return urlparse(url).netloc
