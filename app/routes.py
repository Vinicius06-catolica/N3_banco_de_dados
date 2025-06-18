from fastapi import APIRouter, HTTPException, Query
from .models import Pessoa
from .database import collection

router = APIRouter()

@router.post("/cadastrar")
def cadastrar_pessoa(pessoa: Pessoa):
    try:
        collection.insert_one(pessoa.model_dump())
        return {"mensagem": "Pessoa cadastrada com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pesquisar_nome")
def pesquisar_por_nome(nome: str = Query(...)):
    resultados = list(collection.find({"nome": {"$regex": nome, "$options": "i"}}))
    for doc in resultados:
        doc["_id"] = str(doc["_id"])
    return resultados

@router.get("/pesquisar_rua")
def pesquisar_por_rua(rua: str = Query(...)):
    resultados = list(collection.find({"endereco.rua": {"$regex": rua, "$options": "i"}}))
    for doc in resultados:
        doc["_id"] = str(doc["_id"])
    return resultados

@router.get("/pesquisar_filhos")
def pesquisar_por_filho(nome_filho: str = Query(...)):
    resultados = list(collection.find({"filhos": {"$regex": nome_filho, "$options": "i"}}))
    for doc in resultados:
        doc["_id"] = str(doc["_id"])
    return resultados
