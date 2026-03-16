from flask import jsonify, request, make_response
from funcao import senha_forte, enviando_email, gerar_token, verificar_existente, senha_correspondente
from flask_bcrypt import generate_password_hash, check_password_hash
from main import app, con
import threading
import os
import datetime
from random import randint
import jwt


# Criar usuário
@app.route('/criar_usuarios', methods=['POST'])
def criar_usuarios():
    nome = request.form.get('nome', None)
    email = request.form.get('email')
    cpf_cnpj = request.form.get('cpf_cnpj')
    telefone = request.form.get('telefone', None)
    descricao_breve = request.form.get('descricao_breve', None)
    descricao_longa = request.form.get('descricao_longa', None)
    cod_banco = request.form.get('cod_banco', None)
    num_agencia = request.form.get('num_agencia', None)
    num_conta = request.form.get('num_conta', None)
    tipo_conta = request.form.get('tipo_conta', None)
    chave_pix = request.form.get('chave_pix', None)
    categoria = request.form.get('categoria', None)
    localizacao = request.form.get('localizacao', None)
    senha = request.form.get('senha')
    confirmar_senha = request.form.get('confirmar_senha')
    tipo = request.form.get('tipo')
    foto_perfil = request.files.get('imagem')
    data_cadastro = datetime.datetime.now()
    status = 1
    aprovacao = 0
    email_confirmacao = 0


    cur = con.cursor()

    try:
        if nome == None or nome == "":
            return jsonify({"error": "Nome é uma informação obrigatória."}), 400

        if verificar_existente(cpf_cnpj, 1) == False:
            return jsonify({"error": "CPF ou CNPJ já cadastrado."}), 400

        if verificar_existente(email, 2) == False:
            return jsonify({"error": "E-mail já cadastrado"}, 400)

        if senha_forte(senha) == False:
            return jsonify({"error": "Senha fraca. A senha deve conter pelo menos 8 caracteres, incluindo letras maiúsculas, minúsculas, números e caracteres especiais."}), 400

        if senha_correspondente(senha, confirmar_senha) == False:
            return jsonify({"error": "Senhas não correspondem."}), 400

        senha_cripto = generate_password_hash(senha).decode('utf-8')
        codigo_confirmacao = randint(100000, 999999)
        tentativa = 0

        cur.execute("""INSERT INTO USUARIOS (NOME, EMAIL, SENHA, CPF_CNPJ, TELEFONE, 
                                             DESCRICAO_BREVE, DESCRICAO_LONGA, 
                                             APROVACAO, COD_BANCO, NUM_AGENCIA, NUM_CONTA,
                                             TIPO_CONTA, CHAVE_PIX, CATEGORIA, STATUS, LOCALIZACAO, 
                                             TIPO, DATA_CADASTRO, EMAIL_CONFIRMACAO, CODIGO_CONFIRMACAO, TENTATIVA
                                             )
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) RETURNING ID_USUARIOS""",
                    (nome, email, senha_cripto, cpf_cnpj, telefone, descricao_breve,
                     descricao_longa, aprovacao, cod_banco, num_agencia, num_conta, tipo_conta,
                     chave_pix, categoria, status, localizacao, tipo, data_cadastro, email_confirmacao, codigo_confirmacao, tentativa))
        codigo_usuarios = cur.fetchone()[0]
        con.commit()

        caminho_imagem_destino = None

        if foto_perfil:
            nome_imagem = f'{codigo_usuarios}.jpeg'
            caminho_imagem_destino = os.path.join(app.config['UPLOAD_FOLDER'], "Usuários")
            os.makedirs(caminho_imagem_destino, exist_ok=True)
            caminho_imagem = os.path.join(caminho_imagem_destino, nome_imagem)
            foto_perfil.save(caminho_imagem)

        assunto = f'Confirmação do e-mail'
        mensagem = (f'Primeirmente, agradecemos o cadastro na Doar+!'
                    f'Aqui o código para verificar seu e-mail:'
                    f'{codigo_confirmacao}')
        thread = threading.Thread(target=enviando_email,
                                  args=(email, assunto, mensagem)
                                  )

        thread.start()

        return jsonify({'message': "Usuário cadastrado com sucesso",
                        'usuario': {
                            'tipo': tipo,
                            'nome': nome,
                            'email': email,
                            'cpf_cnpj': cpf_cnpj,
                            'telefone': telefone,
                            'descricao_breve': descricao_breve,
                            'descricao_longa': descricao_longa,
                            'cod_banco': cod_banco,
                            'num_agencia': num_agencia,
                            'num_conta': num_conta,
                            'tipo_conta': tipo_conta,
                            'chave_pix': chave_pix,
                            'categoria': categoria,
                            'localizacao': localizacao
                        }
                        }), 201
    except Exception as e:
        return jsonify(mensagem=f'Erro ao consultar o banco de dados: {e}'), 500
    finally:
        cur.close()

@app.route('/editar_usuario/<int:id_usuarios>', methods=['PUT'])
def editar_usuario(id_usuarios):
    cur = con.cursor()

    try:
        cur.execute("""SELECT ID_USUARIOS, NOME, EMAIL, SENHA, 
                              CPF_CNPJ, TELEFONE, DESCRICAO_BREVE, 
                              DESCRICAO_LONGA, APROVACAO, COD_BANCO, 
                              NUM_AGENCIA, NUM_CONTA, TIPO_CONTA, 
                              CHAVE_PIX, CATEGORIA, STATUS, LOCALIZACAO,
                              TIPO, DATA_CADASTRO, EMAIL_CONFIRMACAO, CODIGO_CONFIRMACAO, TENTATIVA
                       FROM USUARIOS
                       WHERE ID_USUARIOS = ?""", (id_usuarios,))
        tem_usuario = cur.fetchone()

        nome = request.form.get('nome', tem_usuario[1])
        email = request.form.get('email', tem_usuario[2])
        senha_cripto = tem_usuario[3]
        cpf_cnpj = request.form.get('cpf_cnpj', tem_usuario[4])
        telefone = request.form.get('telefone', tem_usuario[5])
        descricao_breve = request.form.get('descricao_breve', tem_usuario[6])
        descricao_longa = request.form.get('descricao_longa', tem_usuario[7])
        cod_banco = request.form.get('cod_banco', tem_usuario[8])
        aprovacao = tem_usuario[9]
        num_agencia = request.form.get('num_agencia', tem_usuario[10])
        num_conta = request.form.get('num_conta', tem_usuario[11])
        tipo_conta = request.form.get('tipo_conta', tem_usuario[12])
        chave_pix = request.form.get('chave_pix', tem_usuario[13])
        categoria = request.form.get('categoria', tem_usuario[14])
        status = tem_usuario[15]
        localizacao = request.form.get('localizacao', tem_usuario[16])
        senha = request.form.get('senha')
        confirmar_senha = request.form.get('confirmar_senha')
        foto_perfil = request.files.get('imagem')
        tipo = tem_usuario[17]
        data_cadastro = tem_usuario[18]
        email_confirmacao = tem_usuario[19]
        codigo_confirmacao = tem_usuario[20]
        tentativa = tem_usuario[21]

        if not tem_usuario:
            return jsonify({"error": "Usuário não encontrado"}), 404

        if nome == None or nome == "":
            return jsonify({"error": "Nome é uma informação obrigatória."}), 400

        if verificar_existente(cpf_cnpj, 1, id_usuarios) == False:
            return jsonify({"error": "CPF ou CNPJ já cadastrado."}), 400

        if verificar_existente(email, 2, id_usuarios) == False:
            return jsonify({"error": "E-mail já cadastrado"}, 400)

        # if senha_forte(senha) == False:
        #     return jsonify({"error": "Senha fraca. A senha deve conter pelo menos 8 caracteres, incluindo letras maiúsculas, minúsculas, números e caracteres especiais."}), 400

        if senha_correspondente(senha, confirmar_senha) == False:
            return jsonify({"error": "Senhas não correspondem."}), 400

        if email != tem_usuario[2]:
            codigo_confirmacao = randint(100000, 999999)
            email_confirmacao = 0

        if senha != None:
            senha_cripto = generate_password_hash(senha).decode('utf-8')

        cur.execute("""UPDATE USUARIOS SET NOME = ?, EMAIL = ?, SENHA = ?, CPF_CNPJ = ?, TELEFONE = ?,
                                             DESCRICAO_BREVE = ?, DESCRICAO_LONGA = ?,
                                             APROVACAO = ?, COD_BANCO = ?, NUM_AGENCIA = ?, NUM_CONTA = ?,
                                             TIPO_CONTA = ?, CHAVE_PIX = ?, CATEGORIA = ?, STATUS = ?, LOCALIZACAO = ?,
                                             TIPO = ?, DATA_CADASTRO = ?, EMAIL_CONFIRMACAO = ?, CODIGO_CONFIRMACAO = ?, TENTATIVA = ?
                    WHERE ID_USUARIOS = ?""", (nome, email, senha_cripto, cpf_cnpj, telefone, descricao_breve,
                     descricao_longa, aprovacao, cod_banco, num_agencia, num_conta, tipo_conta,
                     chave_pix, categoria, status, localizacao, tipo, data_cadastro, email_confirmacao,
                     codigo_confirmacao, tentativa, id_usuarios))
        con.commit()

        caminho_imagem_destino = None

        if foto_perfil:
            nome_imagem = f'{id_usuarios}.jpeg'
            caminho_imagem_destino = os.path.join(app.config['UPLOAD_FOLDER'], "Usuários")
            os.makedirs(caminho_imagem_destino, exist_ok=True)
            caminho_imagem = os.path.join(caminho_imagem_destino, nome_imagem)
            foto_perfil.save(caminho_imagem)

        assunto = f'Confirmação do e-mail'
        mensagem = (f'Primeirmente, agradecemos a sua participação na Doar+!'
                    f'Aqui o código para verificar seu e-mail:'
                    f'{codigo_confirmacao}')
        thread = threading.Thread(target=enviando_email,
                                  args=(email, assunto, mensagem)
                                  )

        thread.start()

        return jsonify({'message': "Usuário cadastrado com sucesso",
                        'usuario': {
                            'tipo': tipo,
                            'nome': nome,
                            'email': email,
                            'cpf_cnpj': cpf_cnpj,
                            'telefone': telefone,
                            'descricao_breve': descricao_breve,
                            'descricao_longa': descricao_longa,
                            'cod_banco': cod_banco,
                            'num_agencia': num_agencia,
                            'num_conta': num_conta,
                            'tipo_conta': tipo_conta,
                            'chave_pix': chave_pix,
                            'categoria': categoria,
                            'localizacao': localizacao
                        }
                        }), 201
    except Exception as e:
        return jsonify(mensagem=f'Erro ao consultar o banco de dados: {e}'), 500
    finally:
        cur.close()

# Excluir usuário
@app.route('/deletar_usuarios/<int:id>', methods=['DELETE'])
def deletar_usuarios(id):
    try:
        cur = con.cursor()
        cur.execute("""SELECT ID_USUARIOS
                        FROM USUARIOS
                        WHERE ID_USUARIOS = ?""", (id,))

        if not cur.fetchone():
            return jsonify({"error": "Usuário não encontrado"}), 404

        cur.execute("""DELETE FROM USUARIOS
                        WHERE ID_USUARIOS = ?""", (id,))
        con.commit()

        return jsonify({"message": "Usuário excluído com sucesso"})

    except Exception as e:
        return jsonify(mensagem=f'Erro ao consultar o banco de dados: {e}'), 500
    finally:
        cur.close()

@app.route('/buscar_usuarios', methods=['GET'])
def buscar_usuarios():
    cpf_cnpj = request.form.get('cpf_cnpj')
    cur = con.cursor()

    try:
        cur.execute("""SELECT ID_USUARIOS, NOME 
                       FROM USUARIOS WHERE cpf_cnpj = ?""", (cpf_cnpj,))
        if cur.fetchone():
            id_usuarios = cur.fetchone()[0]
            nome = cur.fetchone()[1]
            return jsonify({
                'usuario': id_usuarios,
                'nome': nome
            }), 200
        else:
            return jsonify({
                'error': 'Não foi possível encontrar esse usuário'
            }), 404

    except Exception as e:
        return jsonify(mensagem=f'Erro ao consultar o banco de dados: {e}'), 500
    finally:
        cur.close()

# Login
@app.route('/login', methods=['POST'])
def login():
    cpf_cnpj = request.form.get('cpf_cnpj')
    senha = request.form.get('senha')

    cur = con.cursor()

    try:
        cur.execute("""SELECT ID_USUARIOS, TIPO, NOME, CPF_CNPJ, SENHA, TENTATIVA
                        FROM USUARIOS WHERE CPF_CNPJ = ?""", (cpf_cnpj,))
        usuario = cur.fetchone()

        if not usuario:
            return jsonify({"error": "Usuário não encontrado"}), 404

        id_usuarios = usuario[0]
        tipo = usuario[2]
        nome = usuario[3]
        senha_hash = usuario[4]
        tentativa = usuario[5]

        if tentativa > 3:
            return jsonify(
                {"error": "Esse usuário está bloqueado! Entre em contato com o administrador"}
            ), 400

        if check_password_hash(senha_hash, senha):
            id_usuarios = usuario[0]
            token = gerar_token(tipo, id_usuarios)
            resp = make_response(jsonify({'mensagem': f'Bem-vindo {nome}!'}))
            resp.set_cookie('acess_token', token,
                            httponly=True,
                            secure=False,
                            samesite='Lax',
                            path="/",
                            max_age=3600)
            return resp
        tentativa += 1
        cur.execute("""UPDATE USUARIOS SET TENTATIVA = ? WHERE ID_USUARIOS = ?""", (tentativa, id_usuarios))
        return jsonify({"error": "Senha incorreta"}), 400
    except Exception as e:
        return jsonify(mensagem=f'Erro ao consultar o banco de dados: {e}'), 500
    finally:
        cur.close()

@app.route('/desbloquear_usuarios/<int:id_usuarios>', methods=['UPDATE'])
def desbloquear_usuarios(id_usuarios):
    token = request.cookies.get("acess_token")
    if not token:
        return jsonify({'message': 'Token necessário'}), 401
    senha_secreta = app.config['SECRET_KEY']

    cur = con.cursor()

    try:
        payload = jwt.decode(token, senha_secreta, algorithms=['HS256'])
        tipo = payload['tipo']
        if tipo == 0:
            tentativa = 0
            cur.execute("""UPDATE USUARIOS
                           SET TENTATIVA = ?
                           WHERE ID_USUARIOS = ?""", (tentativa, id_usuarios))
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token expirado'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Token invalido'}), 401

