from sqlalchemy import text
from flask import jsonify, session, redirect, url_for
import pandas as pd
import json
import string
import random

from . import engine
from functions import send_mail_local

class Usuario:
    @staticmethod
    def consulta_por_cpf(cpf):
        query = text("SELECT ID, Email FROM usuarios WHERE CPF= :cpf")
        result = engine.execute(query, {"cpf": cpf}).fetchone()
        return result if result else None
    
    @staticmethod
    def insert_usuario(cpf, nome_usuario, data_nascimento, email):
        query = text("""INSERT INTO usuarios (CPF, Nome, DataNascimento, Email) VALUES (:cpf, :nome_usuario, :data_nascimento, :email)""")
        result = engine.execute(query, {"cpf": cpf, "nome_usuario": nome_usuario, "data_nascimento": data_nascimento,"email": email})
        return result.lastrowid

class Verificacao:
    @staticmethod
    def gerar_codigo():
        letters = string.ascii_lowercase
        return ''.join(random.choice(string.digits) for i in range(10))
    
    @staticmethod
    def inserir_codigo(id_usuario, email, codigo):
        query = text("INSERT INTO codigos (IDUsuario, Codigo) VALUES (:id_usuario, :codigo)")
        result = engine.execute(query, {"id_usuario": id_usuario, "codigo": codigo})
        send_mail_local(email, "Codigo de Verificação", "Seu codigo de verificação para o sistema Portal de Cadastro é: " + codigo)
        return codigo

    @staticmethod
    def criar_acesso(id_usuario):
        query = text("INSERT INTO acessos (IDUsuario) VALUES (:id_usuario)")
        result = engine.execute(query, {"id_usuario": id_usuario})
        return result.lastrowid
    