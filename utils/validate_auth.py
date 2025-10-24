from flask import request
from models.models import Usuario 

def check_auth_status():
    login_usuario = request.cookies.get('username')
    senha_hash_cookie = request.cookies.get('senha') 

    if not login_usuario or not senha_hash_cookie:
        return False 
    
    usuario = Usuario.query.filter_by(login=login_usuario).first()

    if usuario is None:
        return False # Usuário não existe

    # 4. Verifica a senha/hash
    # ATENÇÃO: Substitua esta linha pela sua lógica real e segura de verificação de hash!
    if usuario.senha == senha_hash_cookie: 
        return True # Autenticado com sucesso
    else:
        return False # Senha inválida (autenticação falhou)

# Função auxiliar para pegar apenas o username (pode ser útil em outras partes)
def getUsername():
    return request.cookies.get('username')

# Função auxiliar para pegar a senha do cookie (se necessário)
def getPasswordCookie():
    return request.cookies.get('senha')