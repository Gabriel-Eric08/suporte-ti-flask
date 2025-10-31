from flask import Blueprint, render_template, request, jsonify
from models.models import Usuario, Cargo 
from db_config import db
from utils.getUsername import getUsername 
from utils.validate_auth import check_auth_status

user_route = Blueprint('User', __name__)


@user_route.route('/')
def user_page():
    """
    Renderiza a página de informações do usuário.
    - Verifica se o usuário está logado.
    - Busca o nome completo e o nome do cargo do usuário no banco.
    - Envia esses dados para o template HTML.
    """
    # 1. Valida se o usuário está autenticado
    if not check_auth_status():
        return render_template('auth_error.html')
    
    # 2. Obtém o login do usuário a partir do cookie seguro (lido pelo backend)
    username = getUsername()
    if not username:
        return render_template('auth_error.html', message="Sessão inválida. Não foi possível identificar o usuário.")

    # 3. Busca as informações do usuário e do seu cargo usando um JOIN
    #    Corrigido para usar `Cargo.nome_cargo` conforme seu modelo.
    usuario_info = db.session.query(
        Usuario.nome,
        Cargo.nome_cargo.label('cargo_nome')
    ).join(Cargo, Usuario.cargo_id == Cargo.cargo_id).filter(Usuario.login == username).first()

    if not usuario_info:
        # Se o usuário do cookie não for encontrado no banco de dados
        return render_template('auth_error.html', message="Usuário não encontrado no sistema.")

    # 4. Renderiza o template, passando os dados encontrados
    return render_template('info_user.html', 
                           nome_usuario=usuario_info.nome, 
                           cargo_usuario=usuario_info.cargo_nome)


@user_route.route('/alterar-senha', methods=['POST'])
def alterar_senha():
    """
    Processa a requisição de alteração de senha.
    - Identifica o usuário pelo cookie seguro (não pelo JSON).
    - Valida a senha atual e atualiza para a nova senha.
    - Retorna uma resposta JSON de sucesso ou erro.
    """
    # 1. Identifica o usuário a partir da sessão/cookie seguro, não do frontend
    username = getUsername()
    if not username:
        return jsonify({"error": "Sessão inválida ou expirada. Faça login novamente."}), 401

    # 2. Pega os dados enviados pelo JavaScript
    data = request.get_json()
    if not data:
        return jsonify({"error": "Requisição inválida, corpo JSON ausente."}), 400

    senha_atual = data.get('senha')
    nova_senha = data.get('nova_senha')

    # 3. Valida se os campos necessários foram enviados
    if not all([senha_atual, nova_senha]):
        return jsonify({"error": "Os campos 'senha' e 'nova_senha' são obrigatórios."}), 400

    # 4. Busca o usuário no banco de dados
    usuario = Usuario.query.filter_by(login=username).first()

    # 5. Verifica se a senha atual fornecida corresponde à senha no banco
    #    (Lembre-se do aviso: esta comparação direta não é segura)
    if not usuario or usuario.senha != senha_atual:
        return jsonify({"error": "A senha atual está incorreta."}), 401 # 401 Unauthorized

    # 6. Atualiza a senha e salva no banco
    usuario.senha = nova_senha
    db.session.commit()

    # 7. Retorna uma resposta de sucesso
    return jsonify({"message": "Senha alterada com sucesso!"}), 200