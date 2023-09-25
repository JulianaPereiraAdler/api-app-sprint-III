from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import date


class CPFSchema(BaseModel):
    """Define CPF do usuário."""
    CPF: str

class consultarCPFSchema(BaseModel):
    """Define os parâmetros para consultar o CPF do usuário."""
    CPF: str

class envioCodigoSchema(BaseModel):
    """Define a resposta do envio do código de verificação."""
    status: bool
    message: str

class loginSchema(BaseModel):
    """Define os parâmetros para login."""
    CPF: str
    codigo: str
    
class loginResultSchema(BaseModel):
    """Define a resposta do login."""	
    codigo: str
    cpf: str
    data_nascimento: str
    email: str
    nome: str

class criarUsuarioSchema(BaseModel):
    """Define a resposta do login."""	
    cpf: str
    nome_usuario: str
    data_nascimento: date
    email: str

class confereCPFCadastradoSchema(BaseModel):
    """Retorna de CPF já está cadastrado."""
    status: bool
    message: str

