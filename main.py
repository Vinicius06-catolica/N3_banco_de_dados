from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
connection = os.getenv("CONNECTION_STRING")

client = MongoClient(connection)
db = client['martim_python']
collection = db['customers']

app = FastAPI()


class Endereco(BaseModel):
    rua: str
    numero: Optional[int] = None


class Pessoa(BaseModel):
    nome: str
    endereco: Endereco
    filhos: Optional[List[str]] = []


@app.post("/cadastrar")
def cadastrar_pessoa(pessoa: Pessoa):
    try:
        collection.insert_one(pessoa.model_dump())
        return {"mensagem": "Pessoa cadastrada com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/pesquisar_nome")
def pesquisar_por_nome(nome: str = Query(...)):
    resultados = list(collection.find({"nome": {"$regex": nome, "$options": "i"}}))
    for doc in resultados:
        doc["_id"] = str(doc["_id"])
    return resultados

@app.get("/pesquisar_rua")
def pesquisar_por_rua(rua: str = Query(...)):
    resultados = list(collection.find({"endereco.rua": {"$regex": rua, "$options": "i"}}))
    for doc in resultados:
        doc["_id"] = str(doc["_id"])
    return resultados


@app.get("/pesquisar_filhos")
def pesquisar_por_filho(nome_filho: str = Query(...)):
    resultados = list(collection.find({"filhos": {"$regex": nome_filho, "$options": "i"}}))
    for doc in resultados:
        doc["_id"] = str(doc["_id"])
    return resultados
