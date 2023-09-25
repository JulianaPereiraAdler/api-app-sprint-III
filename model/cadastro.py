from sqlalchemy import text
from flask import jsonify, session, redirect, url_for
import pandas as pd
import json
import string
import random

from . import engine
from .log import CadastroLog
from functions import send_mail_local

class Cadastro:
    def __init__(self):
        pass

    def consultar_status_cadastro(self, id_usuario):
        query = text("SELECT * FROM cadastros WHERE IDUsuario = :id_usuario ORDER BY id DESC LIMIT 1")
        result = engine.execute(query, {"id_usuario": id_usuario}).fetchone()

        if result is None:
            dic_status = {
                'Status': "Sem Cadastro",
                'IDCadastro': None,
                'Cotitular': None,
                'DataVencimento': None }
        else:    
            dic_status = {
                'Status': result['Status'],
                'IDCadastro': result['ID'],
                'Cotitular': result['Cotitular'],
                'DataVencimento': result['DataVencimento'] }

        return dic_status

    def inserir_cadastro(self, id_usuario, status):
        query = text("""INSERT INTO cadastros (IDUsuario, Status) VALUES (:id_usuario, :status)""")
        result = engine.execute(query, {"id_usuario": id_usuario, "status": status})
        id_cadastro = result.lastrowid
        CadastroLog().inserir_log(id_usuario, "Preenchimento do cadastro inicializado pelo usuário. Status: " + status)
        return id_cadastro
    
    def atualizar_status_cadastro(self, id_usuario, id_cadastro, status):
        query = text("""UPDATE cadastros SET Status = :status WHERE ID = :id_cadastro""")
        result = engine.execute(query, {"id_cadastro": id_cadastro, "status": status})
        CadastroLog().inserir_log(id_usuario, "Status: " + status)
        return "success"

    def atualizar_cotitular_cadastro(self, id_cadastro, cotitular):
        query = text("""UPDATE cadastros SET Cotitular = :cotitular WHERE ID = :id_cadastro""")
        result = engine.execute(query, {"id_cadastro": id_cadastro, "cotitular": cotitular})
        return "success"

    def atualizar_vencimento_cadastro(self, id_usuario, id_cadastro, DataVencimento):
        query = text("""UPDATE cadastros SET DataVencimento = :DataVencimento WHERE ID = :id_cadastro""")
        result = engine.execute(query, {"id_cadastro": id_cadastro, "DataVencimento": DataVencimento})
        return "success"
    
    def buscar_dados_cadastro(self, id_cadastro):
        query = text("""SELECT d.*, a.Tipo, a.TipoFicha
                        FROM dados_cotistas as d
                        INNER JOIN (
                            SELECT IDAtributo, Cotitular, MAX(ID) as MaxID
                            FROM dados_cotistas
                            WHERE IDCadastro = :id_cadastro
                            GROUP BY IDAtributo, Cotitular
                        ) as sub_d ON d.IDAtributo = sub_d.IDAtributo AND d.Cotitular = sub_d.Cotitular AND d.ID = sub_d.MaxID
                        INNER JOIN atributos as a ON d.IDAtributo = a.ID
                        WHERE d.IDCadastro = :id_cadastro;""")
        results = engine.execute(query, {"id_cadastro": id_cadastro}).fetchall()
        if results is None:
            return None
        
        dados_list = []
        for row in results:
            dados_dict = {
                'ID': row['ID'],
                'IDCadastro': row['IDCadastro'],
                'Cotitular': row['Cotitular'],
                'IDAtributo': row['IDAtributo'],
                'Valor': row['Valor'],
                'Tipo': row['Tipo'],
                'TipoFicha': row['TipoFicha']
            }
            dados_list.append(dados_dict)
        return dados_list

    def buscar_info_cadastro_por_atributo(self, id_cadastro, id_atributo, cotitular):
        dados_dict = {}
        query = text("""SELECT d.*, a.Tipo, a.TipoFicha
                        FROM dados_cotistas as d
                        INNER JOIN (
                            SELECT IDAtributo, Cotitular, MAX(ID) as MaxID
                            FROM dados_cotistas
                            WHERE IDCadastro = :id_cadastro AND IDAtributo = :id_atributo AND Cotitular = :cotitular
                            GROUP BY IDAtributo, Cotitular
                        ) as sub_d ON d.IDAtributo = sub_d.IDAtributo AND d.Cotitular = sub_d.Cotitular AND d.ID = sub_d.MaxID
                        INNER JOIN atributos as a ON d.IDAtributo = a.ID
                        WHERE d.IDCadastro = :id_cadastro AND d.IDAtributo = :id_atributo AND d.Cotitular = :cotitular;""")
        results = engine.execute(query, {"id_cadastro": id_cadastro, "id_atributo": id_atributo, "cotitular": cotitular}).fetchall()
        if results is None:
            return None
        
        for row in results:
            dados_dict = {
                'ID': row['ID'],
                'IDCadastro': row['IDCadastro'],
                'Cotitular': row['Cotitular'],
                'IDAtributo': row['IDAtributo'],
                'Valor': row['Valor'],
                'Tipo': row['Tipo'],
                'TipoFicha': row['TipoFicha']
            }
            print(dados_dict)
        return dados_dict

    def atualizar_info_cadastro(self, id_cadastro, cotitular, id_atributo, valor):
        query = text("""INSERT INTO dados_cotistas (IDCadastro, IDAtributo, Valor, Cotitular) 
                        VALUES (:id_cadastro, :id_atributo, :valor, :cotitular)""")
    
        result = engine.execute(query, {"id_cadastro": id_cadastro, "id_atributo": id_atributo, "valor": valor, "cotitular": cotitular})
        return result.lastrowid
    
    def busca_resultado_perfil_risco(self, id_cadastro):
        query = text("""SELECT 
                            SUM(prp.pontos) AS total_pontos
                        FROM dados_cotistas as d
                        INNER JOIN (
                            SELECT IDAtributo, Cotitular, MAX(ID) as MaxID
                            FROM dados_cotistas
                            WHERE IDCadastro = :id_cadastro AND Cotitular=0
                            GROUP BY IDAtributo, Cotitular
                        ) as sub_d 
                            ON d.IDAtributo = sub_d.IDAtributo 
                            AND d.Cotitular = sub_d.Cotitular 
                            AND d.ID = sub_d.MaxID
                        INNER JOIN atributos as a 
                            ON d.IDAtributo = a.ID
                        LEFT JOIN perfil_risco_pontos as prp
                            ON CAST(a.Nome AS TEXT) = prp.questao
                            AND d.Valor = prp.resposta
                        WHERE d.IDCadastro = :id_cadastro AND a.TipoFicha = "perfil_risco";""")
        result = engine.execute(query, {"id_cadastro": id_cadastro}).fetchone()
    
        if result is None or result['total_pontos'] is None:
            return None  # or return a default value or raise a specific exception
        
        pontos = result['total_pontos']
        if int(pontos) < 10:
            perfil = "Conservador"
        elif 10 < int(pontos) < 24: 
            perfil = "Moderado"
        else: 
            perfil = "Sofisticado"

        return perfil
    
    def confirme_envio_cadastro(self, id_usuario):
        query = text("SELECT Email FROM usuarios WHERE ID = :id_usuario;")
        result = engine.execute(query, {"id_usuario": id_usuario}).fetchone()
        email =  result['Email']
        send_mail_local(email, "Cadastro Enviado com Sucesso", "O seu cadastro foi submetido para aprovação e será analisado tanto pelo gestor quanto pelo administrador do fundo. Após a verificação dos dados e a aprovação no processo de diligência de compliance, você será notificado por e-mail. O prazo para essa análise é de até 3 dias úteis")
        return "success"
    
    def excluir_cadastro(self, id_cadastro, id_usuario):

        query = text("DELETE FROM cadastros WHERE ID  = :id_cadastro;")
        result = engine.execute(query, {"id_cadastro": id_cadastro})

        query = text("DELETE FROM dados_cotistas WHERE IDCadastro  = :id_cadastro;")
        result_excluir = engine.execute(query, {"id_cadastro": id_cadastro})

        CadastroLog().inserir_log(id_usuario, "Status: " + "Cadastro "+str(id_cadastro) + " foi excluido com sucesso.")

        query = text("SELECT Email FROM usuarios WHERE ID = :id_usuario;")
        result = engine.execute(query, {"id_usuario": id_usuario}).fetchone()
        email =  result['Email']
        send_mail_local(email, "Cadastro Excluir com Sucesso", "Os dados do seu cadastro foram excluídos com sucesso e não poderão ser recuperados.")
        return "success"

