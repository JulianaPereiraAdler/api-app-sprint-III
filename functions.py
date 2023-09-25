from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from sqlalchemy import text
import datetime
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
import os



def send_mail(to_address, titulo, html):
    from_address = 'portalcadastro.emailteste@gmail.com'
    msg = MIMEMultipart('alternative')
    msg['Subject'] = titulo
    msg['From'] = from_address
    # if isinstance(to_address,list):
    #     msg['To'] = ", ".join(to_address)
    # else:
    #     msg['To'] = to_address
    part1 = MIMEText(html, 'html')
    msg.attach(part1)
    username = 'portalcadastro.emailteste@gmail.com'
    password = 'ambepemmmknvrrzd'
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(username, password)
    server.sendmail(from_address, to_address, msg.as_string())
    server.quit()


def send_mail_local(to_address, titulo, html):

   # conexão com os servidores do google
    smtp_ssl_host = 'smtp.gmail.com'
    smtp_ssl_port = 465
    # username ou email para logar no servidor
    username = 'portalcadastro.emailteste@gmail.com'
    password = 'ambepemmmknvrrzd'

    from_addr = 'portalcadastro.emailteste@gmail.com'

    # a biblioteca email possuí vários templates
    # para diferentes formatos de mensagem
    # neste caso usaremos MIMEText para enviar
    # somente texto
    message = MIMEText(html, 'html')
    message['subject'] = titulo
    message['from'] = from_addr
    message['to'] = to_address

    # conectaremos de forma segura usando SSL
    server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
    # para interagir com um servidor externo precisaremos
    # fazer login nele
    server.login(username, password)
    server.sendmail(from_addr, to_address, message.as_string())
    server.quit()
        
    return "true"





""" 
def send_mail(to_address, titulo, html):
    from_address = "Portal de Cadastro"
    msg = MIMEMultipart('alternative')
    msg['Subject'] = titulo
    msg['From'] = from_address
    part1 = MIMEText(html, 'html')
    msg.attach(part1)
    username = 'portalcadastro.emailteste@gmail.com'
    password = 'llxchgedbqmvqudp'
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(username, password)
        server.sendmail(from_address, to_address, msg.as_string())
        server.quit()
    except smtplib.SMTPException as e:
        print(f"Error sending email: {e}") """