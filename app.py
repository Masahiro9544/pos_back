from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
from db_control import crud, models, schemas

app = FastAPI()

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def index():
    return {"message": "FastAPI top page!"}

@app.get("/products")
def get_product_by_code(code: str = Query(...)):
    result = crud.myselect_by_code(models.Products, code)
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    result_obj = json.loads(result)
    return result_obj[0] if result_obj else None


