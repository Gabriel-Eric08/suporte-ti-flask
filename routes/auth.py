from flask import Blueprint, request, jsonify, redirect, url_for, render_template, make_response
from models.models import Usuario

auth_route=Blueprint('Auth',__name__)

@auth_route.route('/', methods=['GET'])
def login_page():
    return render_template('login_page.html')

@auth_route.route('/', methods=['POST'])
def validate_login():
    data = request.get_json()
    
    # ... (Verificação de dados incompletos - mantida)
    if not data or 'login' not in data or 'senha' not in data:
        return jsonify({
            "success": False,
            "message": "Dados de login incompletos!"
        }), 400
    
    login = data['login']
    senha = data['senha']

    usuario = Usuario.query.filter_by(login=login).first()

    # 1. Validação de Usuário
    if not usuario or usuario.senha != senha:
        return jsonify({
            "success": False,
            "message": "Login ou senha incorretos."
        }), 401
    
    # --- COMEÇO DA CORREÇÃO PARA SALVAR O COOKIE ---
    
    # 2. Prepara o conteúdo JSON de sucesso
    json_content = jsonify({
        "success": True,
        "message": "Login efetuado com sucesso!",
        # Usamos url_for para gerar a URL correta para a rota home
        "redirect_url": url_for('Home.home_page') 
    })
    
    # 3. Cria o objeto de resposta final a partir do JSON (make_response é essencial aqui)
    response = make_response(json_content)
    
    # 4. Define o cookie na resposta final
    # AVISO DE SEGURANÇA: NUNCA use senhas em cookies em produção.
    # user_id é muito mais seguro, mas para fins de exemplo:
    
    # Define o cookie 'username' (para identificar o usuário)
    # httponly=True: O cookie não pode ser acessado por JavaScript (segurança contra XSS)
    # secure=True: O cookie só será enviado em HTTPS (remova se estiver em HTTP local)
    response.set_cookie('username', login, httponly=True, secure=False) 
    response.set_cookie('senha', senha, httponly=True, secure=False) 
    # Se você realmente precisa do cookie 'password' (mas, novamente, é inseguro):
    # response.set_cookie('password', senha, httponly=True, secure=False)
    
    # Retorna a resposta que contém tanto o JSON quanto os cabeçalhos de Set-Cookie
    return response