import functools
from flask import request, redirect, url_for
from models.models import Usuario  # Importe o modelo de Usuário
from utils.getUsername import getUsername
# Suponho que getUsername() já exista neste arquivo
# from your_app import getUsername 

def is_default_password():
    """
    Verifica se o usuário logado atualmente está usando a senha padrão '123'.
    Retorna True se a senha for a padrão, caso contrário False.
    """
    try:
        # Pega o nome de usuário do cookie/sessão
        username = getUsername()
        if not username:
            return False

        # Busca o usuário no banco de dados
        usuario = Usuario.query.filter_by(login=username).first()

        # Compara a senha (sem hash, como solicitado anteriormente)
        if usuario and usuario.senha == '123':
            return True
        
        return False
    except Exception as e:
        # Em caso de qualquer erro, assume que não é a senha padrão
        print(f"Erro ao checar senha padrão: {e}")
        return False


def password_change_required(f):
    """
    DECORADOR: Se a senha do usuário for a padrão ('123'),
    redireciona para a página de alteração de senha, a menos que
    o usuário já esteja nessa página.
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        # Verifica se a senha é a padrão E se a rota atual NÃO É a página de troca de senha
        # A checagem 'request.endpoint' evita um loop de redirecionamento infinito.
        if is_default_password() and request.endpoint != 'User.user_page':
            # Redireciona para a página de alteração de senha
            return redirect(url_for('User.user_page'))
        
        # Se a senha não for a padrão ou se já estiver na página correta, executa a rota original
        return f(*args, **kwargs)
    return decorated_function