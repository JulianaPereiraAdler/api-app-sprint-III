from typing import Dict, List, Optional
from pydantic import BaseModel
from datetime import date


class IDUsuarioSchema(BaseModel):
    """Define o IDUsuario para buscar as informações e statos do cadastro deste usuario."""	
    IDUsuario: int

class ConfereStatusSchema(BaseModel):
    """Retorna Status do cadastro do usuário."""	
    Status: str
    IDCadastro: int
    Cotitular: bool
    DataVencimento: date

class IDCadastroSchema(BaseModel):
    """Retorna o IDCadastro do usuário."""
    IDCadastro: int

class IDCadastro_IDUsuarioSchema(BaseModel):
    """Define o IDCadastro e o IDUsuario."""
    IDCadastro: int
    IDUsuario: int

class InfoPorIDAtributoSchema(BaseModel):
    """Retorna o IDCadastro do usuário."""
    IDCadastro: int
    IDAtributo: int
    Cotitular: bool

class DadosCotistasSchema(BaseModel):
    """Retorna os dados do cadastro do usuário."""
    ID: int
    IDCadastro: int
    Cotitular: bool
    IDAtributo: int
    Valor: str
    Tipo: str
    TipoFicha: str

class ListaDadosCotistasSchema(BaseModel):
    model: List[DadosCotistasSchema]

class atualizarInfoCotistaSchema(BaseModel):
    """Define informações para atualizar o cadastro do usuário."""
    IDCadastro: int
    Cotitular: bool
    IDAtributo: int
    Valor: str

class IDInfoCadastroSchema(BaseModel):
    """Retorna o ID da informação do cadastro do usuário."""
    IDInfoCadastro: int

class atualizarCotitularSchema(BaseModel):
    """Retorna o ID da informação do cadastro do usuário."""
    IDCadastro: int
    Cotitular:bool

class resultSchema(BaseModel):
    """Retorna o resultado da inserção do cadastro do usuário."""
    Resul: str

