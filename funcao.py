# Importar a chave secreta do config
from config import SECRET_KEY

# Importar o con da main
from main import con

# Bibliotecas para envio de e-mail
import smtplib
from email.mime.text import MIMEText

# Bibliotecas para token
import jwt
import datetime

def verificar_existente(valor, tipo, id_usuarios = None):
    try:
        cur = con.cursor()
        if tipo == 1:
            if id_usuarios:
                cur.execute("""SELECT 1
                               FROM USUARIOS
                               WHERE CPF_CNPJ = ? AND ID_USUARIOS != ?""", (valor, id_usuarios))
            cur.execute("""SELECT 1
                           FROM USUARIOS
                           WHERE CPF_CNPJ = ?""", (valor,))
        elif tipo == 2:
            if id_usuarios:
                cur.execute("""SELECT 1
                               FROM USUARIOS
                               WHERE EMAIL = ? AND ID_USUARIOS != ?""", (valor, id_usuarios))
            cur.execute("""SELECT 1
                           FROM USUARIOS
                           WHERE EMAIL = ?""", (valor, ))

        if not cur.fetchone():
            return True
        return False
    except Exception as e:
        print(f"Erro na validação do e-mail ou cpf/cnpj: {e}")
        return False

def senha_correspondente(senha, confirmar_senha):
    try:
        if senha == confirmar_senha:
            return True
        return False
    except Exception as e:
        print(f"Erro na validação da senha: {e}")
        return False


def senha_forte(senha):
    try:
        if len(senha) < 8:
            return False
        criterios = {
            "maiuscula": False,
            "minuscula": False,
            "numero": False,
            "especial": False
        }
        for s in senha:
            if s.isupper():
                criterios["maiuscula"] = True
            elif s.islower():
                criterios["minuscula"] = True
            elif s.isdigit():
                criterios["numero"] = True
            elif s.isalnum() is False:
                criterios["especial"] = True
        if criterios["maiuscula"] == True and criterios["minuscula"] == True and criterios["numero"] == True and criterios["especial"] == True:
            return True
        return False
    except Exception as e:
        print(f"Erro na validação da senha: {e}")
        return False

def enviando_email(destinatario, assunto, mensagem):
    user = 'luisa.michelinr@gmail.com'
    senha = 'hqca hibi tndj trfk'

    msg = MIMEText(mensagem)
    msg['From'] = user
    msg['To'] = destinatario
    msg['Subject'] = assunto

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(user, senha)
    server.send_message(msg)
    server.quit()

def gerar_token(tipo, id_usuarios):
    payload = { 'tipo': tipo,
                'id_usuarios': id_usuarios,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
               }
    senha_secreta = SECRET_KEY
    token = jwt.encode(payload, senha_secreta, algorithm='HS256')

    return token

def remover_bearer(token):
    if token.startswith('Bearer '):
        return token[len('Bearer '):]
    else:
        return token