from flask_openapi3 import OpenAPI, Info, Tag
from flask import Flask, render_template, jsonify, request, redirect, url_for, session, abort, make_response, g
from functools import wraps
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from logger import logger
from typing import Optional
from io import BytesIO

import pandas as pd
import re
import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import string
import random
import datetime
from dateutil.relativedelta import relativedelta
import os
import jwt
import datetime

from functions import send_mail, send_mail_local
from model import db_url, engine
from model.login import Usuario, Verificacao
from model.log import CadastroLog
from model.cadastro import Cadastro

from schemas import *


info = Info(title="API do Portal de Cadastro da Gestora X (MVP - Sprint 3)", version="1.0.0")
app = OpenAPI(__name__, info=info)
app.secret_key = "FSDt4kntc43qtc$QfdsfdsfsdAECTN$#CcaF$#Ckanf"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=2)
app.config['SESSION_TYPE'] = 'redis'

CORS(app)

# definindo tags
doc_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
login_tag = Tag(name="Login", description="Login do usuário")
cadastro_tag = Tag(name="Cadastro", description="Consulta, atualizar as informação e status dos cadastros dos usuários ")
perfil_risco_tag = Tag(name="Perfil de Risco", description="Calcula Perfil de Risco dos Investidores")
log_tag = Tag(name="Log de Atividades", description="Log de atividades do usuário")


SECRET_KEY = "ADKAJSDIAJDADKAPOSDK"

# functions login
def verify_login(cpf, codigo_digitado):
    query = """SELECT codigo, u.CPF, u.Nome, u.DataNascimento, u.Email, u.ID FROM codigos c 
                INNER JOIN usuarios u 
                    ON c.IDUsuario = u.ID
                WHERE u.CPF = :cpf 
                ORDER BY DataCriado DESC"""
    result = engine.execute(query, {"cpf": cpf}).first()
    print("rodou - codigo banco:", result)
    if result:
        codigo_certo = result['Codigo']
        print("codigos", codigo_certo, codigo_digitado, codigo_certo==codigo_digitado)
        if codigo_certo == codigo_digitado:
            payload = {
                "cpf": result['CPF'],
                "nome": result['Nome'],
                "email": result['Email'],
                "IDusuario": result['ID'],
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=12)  # Token expiry in 12 hour
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
            
            Verificacao.criar_acesso(result['ID'])
            return {"token": token, "message": "Successfully logged in"}
        
    return {"message": "wrong_code"}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                token = auth_header.split('Bearer ')[1]
                decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
                g.decoded_token = decoded_token
                return f(*args, **kwargs)
            except jwt.ExpiredSignatureError:
                return jsonify({"detail": "Token has expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"detail": "Invalid token"}), 401
        else:
            return jsonify({"detail": "Authorization header missing"}), 401
    return decorated_function


@app.get('/verificar_login_realizado', tags=[login_tag])
@login_required
def verificar_login_realizado():
    nome_user = g.decoded_token.get('nome')
    IDusuario = g.decoded_token.get('IDusuario')
    return jsonify({"nome": nome_user, "IDusuario": IDusuario})


@app.get('/swagger', tags=[doc_tag])
def swagger():
    """Redireciona para a documentação Swagger."""
    return redirect('/openapi/swagger')


@app.get('/documentacao', tags=[doc_tag])
def documentacao():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')


@app.post('/send_confirmation_code', tags=[login_tag], responses={"200": envioCodigoSchema, "404": ErrorSchema})
def send_confirmation_code(form: consultarCPFSchema):
    """Envia código de verificação para o email do usuário se o CPF estiver cadastrado no sistema. Se o CPF não estiver cadastrado, retorna status 'falso' e mensagem de usuário não cadastrado."""
    cpf = form.CPF
    usuario = Usuario.consulta_por_cpf(cpf)
    if not usuario: 
        response = envioCodigoSchema(status=False, message="Usuário não cadastrado. Por favor, faça seu cadastro.")
        return jsonify(response.dict())
    else:
        codigo = Verificacao.gerar_codigo()
        Verificacao.inserir_codigo(usuario[0], usuario[1], codigo)
        response = envioCodigoSchema(status=True, message="Código gerado e inserido com sucesso")
        return jsonify(response.dict())
    

@app.post('/login', tags=[login_tag], responses={"200": loginResultSchema, "404": ErrorSchema})
def login(form: loginSchema):
    """Efetua login"""
    cpf = form.CPF
    codigo = form.codigo
    return verify_login(cpf, codigo)

# ACERTAR AQUIII
@app.get('/logout', tags=[login_tag])
def logout():
    """Efetua logout"""
    session.pop('cpf', None)
    session.pop('codigo', None)
    session.clear()
    return "success"


@app.post('/cadastrar_novo_usuario', tags=[login_tag], responses={"200": loginResultSchema, "404": ErrorSchema})
def cadastrar_novo_usuario(form: criarUsuarioSchema):
    """Efetua login"""
    IDUsuario = Usuario.insert_usuario(form.cpf, form.nome_usuario, form.data_nascimento, form.email)
    CadastroLog().inserir_log(IDUsuario, "Usuário realizou registro no Portal de Cadastro.")
    return "success"


@app.post('/conferir_se_cpf_existe', tags=[login_tag], responses={"200": confereCPFCadastradoSchema, "404": ErrorSchema})
def conferir_se_cpf_existe(form: consultarCPFSchema):
    """ Conferir se o CPF já está cadastrado no sistema"""
    usuario = Usuario.consulta_por_cpf(form.CPF)
    if not usuario: 
        status=False
        message = "Usuário não cadastrado."
    else:
        status=True
        message = "Usuário já cadastrado."
    return {"status": status, "message": message}


@app.post('/conferir_status_cadastro', tags=[cadastro_tag], responses={"200": ConfereStatusSchema, "404": ErrorSchema})
@login_required
def conferir_status_cadastro(form: IDUsuarioSchema):
    """ Confere o status do cadastro do usuário"""
    status = Cadastro().consultar_status_cadastro(form.IDUsuario)
    return jsonify(status)


@app.post('/inserir_cadastro_banco', tags=[cadastro_tag], responses={"200": IDCadastroSchema, "404": ErrorSchema})
@login_required
def inserir_cadastro_banco(form: IDUsuarioSchema):
    """ Confere o status do cadastro do usuário"""
    status = "Cadastro Inicializado"
    id_cadastro = Cadastro().inserir_cadastro(form.IDUsuario, status)
    return jsonify(id_cadastro)


@app.post('/buscar_info_cadastro', tags=[cadastro_tag], responses={"200": ListaDadosCotistasSchema, "404": ErrorSchema})
@login_required
def buscar_info_cadastro(form: IDCadastroSchema):
    """ Retorna os dados do cadastro do usuário"""
    dados_cadastro = Cadastro().buscar_dados_cadastro(form.IDCadastro)
    return jsonify(dados_cadastro)


@app.post('/buscar_info_cadastro_por_atributo', tags=[cadastro_tag], responses={"200": DadosCotistasSchema, "404": ErrorSchema})
def buscar_info_cadastro_por_atributo(form: InfoPorIDAtributoSchema):
    """ Retorna os dados do cadastro do usuário"""
    dados_cadastro = Cadastro().buscar_info_cadastro_por_atributo(form.IDCadastro, form.IDAtributo, form.Cotitular)
    return jsonify(dados_cadastro)


@app.post('/atualizar_info_cadastro', tags=[cadastro_tag], responses={"200": ListaDadosCotistasSchema, "404": ErrorSchema})
@login_required
def atualizar_info_cadastro(form: atualizarInfoCotistaSchema):
    """ Retorna os dados do cadastro do usuário"""
    id_info_cadastro = Cadastro().atualizar_info_cadastro(form.IDCadastro, form.Cotitular, form.IDAtributo, form.Valor)
    return jsonify(id_info_cadastro)


@app.post('/atualizar_cotitular_cadastro', tags=[cadastro_tag], responses={"200": resultSchema, "404": ErrorSchema})
@login_required
def atualizar_cotitular_cadastro(form: atualizarCotitularSchema):
    """ Atualizar cotitular do cadastro do usuário"""
    result = Cadastro().atualizar_cotitular_cadastro(form.IDCadastro, form.Cotitular)
    return jsonify(result)


@app.post('/inserir_log_atividade', tags=[log_tag], responses={"200": AtividadesLogSchema, "404": ErrorSchema})
@login_required
def inserir_log_atividade(form: InserirLogSchema):
    """ Conferir se o CPF já está cadastrado no sistema"""
    log = CadastroLog().inserir_log(form.IDUsuario, form.Atividade)
    lista_atividades_logs = CadastroLog().consultar_log_por_idCadastro(form.IDUsuario)
    return lista_atividades_logs

# BUSCAR IDCadastro DA SESSION
@app.post('/busca_log_atividade', tags=[log_tag], responses={"200": AtividadesLogSchema, "404": ErrorSchema})
@login_required
def busca_log_atividade(form: IDCadastroLogSchema):
    """ Busca log de atividades do usuário"""
    lista_atividades_logs = CadastroLog().consultar_log_por_idCadastro(form.IDUsuario)
    return lista_atividades_logs

@app.post('/busca_resultado_perfil_risco', tags=[perfil_risco_tag], responses={"200": resultSchema, "404": ErrorSchema})
@login_required
def busca_resultado_perfil_risco(form: IDCadastroSchema):
    """ Calcula perfil de risco do investidor"""
    perfil = Cadastro().busca_resultado_perfil_risco(form.IDCadastro)
    return perfil

@app.post('/envio_cadastro_aprovacao', tags=[cadastro_tag], responses={"200": resultSchema, "404": ErrorSchema})
@login_required
def envio_cadastro_aprovacao(form: IDCadastro_IDUsuarioSchema):
    """ Confirma envio do cadastro por email para o usuario e altera status do IDCadastro no banco de dados."""
    perfil = Cadastro().atualizar_status_cadastro(form.IDUsuario, form.IDCadastro, "Em Aprovação")
    envio = Cadastro().confirme_envio_cadastro(form.IDUsuario)
    return envio

@app.post('/excluir_cadastro', tags=[cadastro_tag], responses={"200": resultSchema, "404": ErrorSchema})
@login_required
def excluir_cadastro(form: IDCadastro_IDUsuarioSchema):
    """ Exclui o cadastro do usuario """
    perfil = Cadastro().excluir_cadastro(form.IDCadastro, form.IDUsuario)
    return perfil


#-------------------------------------------------------------------------------------------------------------------------------------------------

@app.get('/enviar_email_teste', tags=[doc_tag])
@login_required
def enviar_email_teste():

    mail = 'jpereira@atmoscapital.com.br'

    with open("templates/email_template_teste.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    send_mail_local(mail, "Email Teste", html)
    return "true"


@app.get('/enviar_email', tags=[doc_tag])
def enviar_email():

   # conexão com os servidores do google
    smtp_ssl_host = 'smtp.gmail.com'
    smtp_ssl_port = 465
    # username ou email para logar no servidor
    username = 'portalcadastro.emailteste@gmail.com'
    password = 'ambepemmmknvrrzd'

    from_addr = 'portalcadastro.emailteste@gmail.com'
    to_addrs = ['jpereira@atmoscapital.com.br', 'julianahpereira@gmail.com']

    # a biblioteca email possuí vários templates
    # para diferentes formatos de mensagem
    # neste caso usaremos MIMEText para enviar
    # somente texto
    message = MIMEText('Hello World')
    message['subject'] = 'Hello'
    message['from'] = from_addr
    message['to'] = ', '.join(to_addrs)

    # conectaremos de forma segura usando SSL
    server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
    # para interagir com um servidor externo precisaremos
    # fazer login nele
    server.login(username, password)
    server.sendmail(from_addr, to_addrs, message.as_string())
    server.quit()
        
    return "true"


