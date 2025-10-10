from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Optional
import math
import json
import db_control.models as models
import db_control.schemas as schemas
from db_control.connect import SessionLocal


def myselect_by_code(model, code: str):
    db = SessionLocal()
    try:
        result = db.query(model).filter(model.code == code).first()
        if result:
            return json.dumps([{
                "prd_id": result.prd_id,
                "code": result.code,
                "name": result.name,
                "price": result.price
            }])
        return None
    finally:
        db.close()


def create_transaction(emp_cd: Optional[str], store_cd: str, pos_no: str, total_amt: int, ttl_amt_ex_tax: int):
    """
    Transactionテーブルに新規レコードを作成
    """
    db = SessionLocal()
    try:
        # 現在の日時を取得
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # emp_cdが空の場合は"9999999999"を設定
        if not emp_cd:
            emp_cd = "9999999999"

        new_transaction = models.Transaction(
            datetime=now,
            emp_cd=emp_cd,
            store_cd=store_cd,
            pos_no=pos_no,
            total_amt=total_amt,
            ttl_amt_ex_tax=ttl_amt_ex_tax
        )

        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)

        return new_transaction.trd_id
    finally:
        db.close()


def create_detail(trd_id: int, dtl_id: int, prd_id: int, prd_code: str, prd_name: str, prd_price: int, tax_id: int = 2):
    """
    Detailsテーブルに新規レコードを作成
    """
    db = SessionLocal()
    try:
        new_detail = models.Details(
            trd_id=trd_id,
            dtl_id=dtl_id,
            prd_id=prd_id,
            prd_code=prd_code,
            prd_name=prd_name,
            prd_price=prd_price,
            tax_id=tax_id
        )

        db.add(new_detail)
        db.commit()

        return True
    finally:
        db.close()


def update_transaction_amounts(trd_id: int, total_amt: int, ttl_amt_ex_tax: int):
    """
    Transactionテーブルの金額を更新
    """
    db = SessionLocal()
    try:
        transaction = db.query(models.Transaction).filter(models.Transaction.trd_id == trd_id).first()

        if transaction:
            transaction.total_amt = total_amt
            transaction.ttl_amt_ex_tax = ttl_amt_ex_tax
            db.commit()
            return True

        return False
    finally:
        db.close()


def get_tax_rate(tax_id: int):
    """
    Taxテーブルから税率を取得
    """
    db = SessionLocal()
    try:
        tax = db.query(models.Tax).filter(models.Tax.tax_id == tax_id).first()
        if tax:
            return tax.tax
        return None
    finally:
        db.close()
