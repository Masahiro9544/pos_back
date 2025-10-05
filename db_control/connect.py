import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# AzureのSSL接続要件を満たすため、サーバーの正当性を検証するための
# SSL証明書ファイルを指定します。
# 絶対パスで指定
ssl_cert_path = Path(__file__).parent.parent / "DigiCertGlobalRootG2.crt.pem"
connect_args = {
    "ssl_ca": str(ssl_cert_path)
}

# create_engineに関数を渡して、SSL設定を適用する
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
