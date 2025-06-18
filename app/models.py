from pydantic import BaseModel
from typing import List, Optional

class Endereco(BaseModel):
    rua: str
    numero: Optional[int] = None

class Pessoa(BaseModel):
    nome: str
    endereco: Endereco
    filhos: Optional[List[str]] = []
