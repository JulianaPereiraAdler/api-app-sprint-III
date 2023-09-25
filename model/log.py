from sqlalchemy import text
from flask import jsonify, session, redirect, url_for
import pandas as pd
import json
import string
import random

from . import engine
from functions import send_mail_local

class CadastroLog:
    def __init__(self):
        pass

    def inserir_log(self, id_usuario, status):
        query = text("INSERT INTO cadastros_log (IDUsuario, Status) VALUES (:id_usuario, :status)")
        result = engine.execute(query, {"id_usuario": id_usuario, "status": status })
        id_log = result.lastrowid
        return id_log 

    def consultar_log_por_idCadastro(self, id_usuario):
        resposta = []
        query = text("""SELECT * FROM cadastros_log WHERE IDUsuario = :id_usuario ORDER BY Timestamp DESC""")
        result = engine.execute(query, {"id_usuario": id_usuario}).fetchall()

        for i in result:
            dic_log = { 'ID': i['ID'],
                        'IDUsuario': i['IDUsuario'],
                        'Timestamp': i['Timestamp'],
                        'Status': i['Status'],
                    }
            resposta.append(dic_log)
        return resposta


    