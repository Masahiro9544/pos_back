from fastapi import FastAPI, HTTPException, Query, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
import os
from db_control import crud, models, schemas
from auth import create_access_token, verify_token, generate_user_id

# 環境変数の読み込み
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
ALLOWED_IPS = os.getenv("ALLOWED_IPS", "").split(",")

# 本番環境ではSwaggerUIを無効化
app = FastAPI(
    docs_url="/docs" if ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if ENVIRONMENT == "development" else None,
    openapi_url="/openapi.json" if ENVIRONMENT == "development" else None
)

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# IPアドレス制限ミドルウェア（開発環境のみ）
@app.middleware("http")
async def ip_restriction_middleware(request: Request, call_next):
    # 開発環境でSwagger関連のパスにアクセスする場合のみIP制限
    if ENVIRONMENT == "development" and request.url.path in ["/docs", "/redoc", "/openapi.json"]:
        client_ip = request.client.host
        if client_ip not in ALLOWED_IPS:
            raise HTTPException(status_code=403, detail="Access forbidden: IP not allowed")

    response = await call_next(request)
    return response


@app.get("/")
def index():
    return {"message": "FastAPI top page!"}


@app.post("/auth/start")
def start_shopping():
    """
    買い物開始時に呼ばれるエンドポイント
    ユーザーIDとアクセストークンを生成して返す
    """
    # ユニークなユーザーIDを生成
    user_id = generate_user_id()

    # アクセストークンを生成
    access_token = create_access_token(user_id)

    return {
        "user_id": user_id,
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.get("/products")
def get_product_by_code(code: str = Query(...), user_id: str = Depends(verify_token)):
    """
    商品コードで商品を検索するエンドポイント
    認証が必要
    """
    result = crud.myselect_by_code(models.Products, code)
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    result_obj = json.loads(result)
    return result_obj[0] if result_obj else None


@app.get("/tax/{tax_id}", response_model=schemas.TaxResponse)
def get_tax(tax_id: int, user_id: str = Depends(verify_token)):
    """
    税率情報を取得するエンドポイント
    認証が必要
    """
    tax_rate = crud.get_tax_rate(tax_id)
    if tax_rate is None:
        raise HTTPException(status_code=404, detail="Tax not found")
    return schemas.TaxResponse(tax_id=tax_id, tax_rate=tax_rate)


@app.post("/purchase", response_model=schemas.PurchaseResponse)
def process_purchase(request: schemas.PurchaseRequest, user_id: str = Depends(verify_token)):
    """
    購入処理エンドポイント
    1. transactionレコード作成（初期値で合計金額0）
    2. detailsレコード作成
    3. 合計金額と税額を計算
    4. transactionレコードを更新
    5. 計算結果を返却
    """
    try:
        # ①transactionテーブルに初期レコードを作成（金額は仮で0）
        trd_id = crud.create_transaction(
            emp_cd=request.emp_cd,
            store_cd="30",
            pos_no="90",
            total_amt=0,
            ttl_amt_ex_tax=0
        )

        # ②detailsテーブルに商品情報を登録
        for idx, item in enumerate(request.items, start=1):
            for _ in range(item.quantity):
                crud.create_detail(
                    trd_id=trd_id,
                    dtl_id=idx,
                    prd_id=item.prd_id,
                    prd_code=str(item.code),
                    prd_name=item.name,
                    prd_price=item.price,
                    tax_id=2
                )

        # ③合計金額と税額を計算（消費税10%）
        total_price_ex_tax = sum(item.price * item.quantity for item in request.items)
        tax_amt = int(total_price_ex_tax * 0.1)
        total_amt = total_price_ex_tax + tax_amt

        # ④transactionテーブルを更新
        crud.update_transaction_amounts(
            trd_id=trd_id,
            total_amt=total_amt,
            ttl_amt_ex_tax=total_price_ex_tax
        )

        # ⑤結果を返す
        return schemas.PurchaseResponse(
            trd_id=trd_id,
            total_amt=total_amt,
            ttl_amt_ex_tax=total_price_ex_tax,
            tax_amt=tax_amt
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Purchase processing failed: {str(e)}")


