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
