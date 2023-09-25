from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import date


class InserirLogSchema(BaseModel):
    """Define os parâmetros para inserir uma atividade do usuario no log."""	
    IDUsuario: str
    Atividade: str

class IDCadastroLogSchema(BaseModel):
    """Define IDCadastro para buscar as atividade do usuario no log."""	
    IDUsuario: int

class LogSchema(BaseModel):
    ID: int
    IDUsuario: str
    Timestamp: date
    Status: str

class AtividadesLogSchema(BaseModel):
    lista_atividades: List[LogSchema]  


