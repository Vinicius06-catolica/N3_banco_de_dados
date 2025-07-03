from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Faixa(BaseModel):
    numero: int
    titulo: str
    duracao_segundos: int
    compositores: List[str]

class Album(BaseModel):
    id: Optional[str] = Field(default_factory=str, alias="_id") 
    titulo: str
    artista: str
    anoLancamento: int
    generos: List[str]
    formato: str
    gravadora: str
    numeroCatalogo: str
    urlCapa: str
    adicionadoEm: datetime
    faixas: List[Faixa]

    class Config:
        populate_by_name = True

class AlbumUpdateAno(BaseModel):
    anoLancamento: int

class AlbumUpdateGenero(BaseModel):
    genero: str

class UpdateCompositorNome(BaseModel):
    nome_antigo: str
    nome_novo: str