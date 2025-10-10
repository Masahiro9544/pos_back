import jwt
import uuid
import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# セキュリティスキーム
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "24"))

security = HTTPBearer()

# アクティブなトークンを保存する辞書（本番環境ではRedisなどを使用すべき）
active_tokens = {}


def create_access_token(user_id: str) -> str:
    """
    アクセストークンを生成する
    """
    expires_delta = timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    expire = datetime.utcnow() + expires_delta

    to_encode = {
        "user_id": user_id,
        "exp": expire,
        "iat": datetime.utcnow()
    }

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    # トークンをアクティブなトークンとして保存
    active_tokens[encoded_jwt] = {
        "user_id": user_id,
        "created_at": datetime.utcnow(),
        "expires_at": expire
    }

    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """
    トークンを検証し、ユーザーIDを返す
    """
    token = credentials.credentials

    # トークンがアクティブかチェック
    if token not in active_tokens:
        raise HTTPException(
            status_code=401,
            detail="無効なトークンです"
        )

    try:
        # トークンをデコード
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="トークンが無効です"
            )

        # トークンの有効期限をチェック
        token_data = active_tokens[token]
        if datetime.utcnow() > token_data["expires_at"]:
            # 有効期限切れのトークンを削除
            del active_tokens[token]
            raise HTTPException(
                status_code=401,
                detail="トークンの有効期限が切れています"
            )

        return user_id

    except jwt.ExpiredSignatureError:
        # 有効期限切れのトークンを削除
        if token in active_tokens:
            del active_tokens[token]
        raise HTTPException(
            status_code=401,
            detail="トークンの有効期限が切れています"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="トークンの検証に失敗しました"
        )


def generate_user_id() -> str:
    """
    ユニークなユーザーIDを生成する
    """
    return str(uuid.uuid4())


def revoke_token(token: str) -> bool:
    """
    トークンを無効化する
    """
    if token in active_tokens:
        del active_tokens[token]
        return True
    return False
