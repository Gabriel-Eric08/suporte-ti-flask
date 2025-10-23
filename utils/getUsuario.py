from flask import request, make_response, jsonify
from models.models import Usuario

def return_user():
    login = request.cookies.get('username')
    user=Usuario.query.filter_by(login=login)
    if not login:
        return jsonify({
            "sucess":False,
            "message":"Login não encontrado nos cookies!"
        })
    elif not user:
        return jsonify({
            "sucess":False,
            "message":"Nenhum usuário encontrado com login presente nos cookies"
        })
    return user