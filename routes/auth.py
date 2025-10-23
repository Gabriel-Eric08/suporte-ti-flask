from flask import Blueprint,request, jsonify, make_response 
from models.models import Usuario

auth_route=Blueprint('Auth',__name__)





@auth_route.route('/', methods=['POST'])
def validate_login():
    data = request.get_json()
    
    if not data or 'login' not in data or 'senha' not in data:
        return jsonify({
            "success": False,
            "message": "Dados de login incompletos!"
        }), 400
    
    login = data['login']
    senha = data['senha']

    usuario = Usuario.query.filter_by(login=login).first()

    if not usuario:
        return jsonify({
            "success": False,
            "message": "Login ou senha incorretos."
        }), 401
    
    if usuario.senha != senha:
        return jsonify({
            "success": False,
            "message": "Login ou senha incorretos."
        }), 401
    
    response = make_response(jsonify({
        "success": True,
        "message": "Login efetuado com sucesso!",
        "username": login 
    }), 200)
    
    # 2. Define o cookie 'username' (armazena o login)
    # httponly=False é necessário se você planeja ler este cookie com JavaScript
    response.set_cookie('username', login, httponly=True, secure=True) 
    
    # 3. Define o cookie 'password' (armazena a senha em texto puro - MUITO INSEGURO)
    response.set_cookie('password', senha, httponly=True, secure=True)

    # RECOMENDAÇÃO: Use httponly=True para evitar que scripts do lado do cliente (XSS) roubem o cookie.
    # RECOMENDAÇÃO: Use secure=True em produção (requer HTTPS).
    
    return response