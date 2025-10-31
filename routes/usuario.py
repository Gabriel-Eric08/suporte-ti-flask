# Adicione este import no topo do seu arquivo, caso não exista
from flask import Flask, Blueprint, render_template, request, jsonify
from models.models import Usuario
from db_config import db

user_route = Blueprint('User',__name__)

@user_route.route('/')
def user_page():
    return render_template('info_user.html')

# ROTA AJUSTADA PARA COMPARAÇÃO DIRETA DE STRINGS (NÃO RECOMENDADO)
@user_route.route('/alterar-senha', methods=['POST'])
def alterar_senha():
    # 1. Garante que o corpo da requisição é JSON
    data = request.get_json()
    if not data:
        return jsonify({"error": "Requisição inválida, corpo JSON ausente."}), 400

    # 2. Valida se todos os campos necessários foram enviados
    username = data.get('username')
    senha_atual = data.get('senha')
    nova_senha = data.get('nova_senha')

    if not all([username, senha_atual, nova_senha]):
        return jsonify({"error": "Campos 'username', 'senha' e 'nova_senha' são obrigatórios."}), 400

    # 3. Busca o usuário no banco de dados
    #    Use .first() para obter o objeto do usuário ou None se não existir
    usuario = Usuario.query.filter_by(login=username).first()

    # 4. MUDANÇA PRINCIPAL: Comparação direta de strings (NÃO RECOMENDADO)
    #    Verifica se o usuário existe e se a senha atual é exatamente igual à do banco
    if not usuario or usuario.senha != senha_atual:
        return jsonify({"error": "Usuário ou senha atual incorreta."}), 401 # 401 Unauthorized

    # 5. Salva a nova senha diretamente em texto plano (NÃO RECOMENDADO)
    usuario.senha = nova_senha
    
    # 6. Salva a alteração no banco de dados usando a sessão
    db.session.commit()

    # 7. Retorna uma resposta de sucesso
    return jsonify({"message": "Senha alterada com sucesso!"}), 200