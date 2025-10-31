from flask import Flask, Blueprint, render_template
from flask import jsonify
from models.models import Setor,Usuario
from db_config import db
from sqlalchemy.exc import SQLAlchemyError
from utils.validate_auth import check_auth_status
from utils.getUsername import getUsername
from utils.changePasswordRequired import password_change_required

home_route=Blueprint('Home',__name__)

@home_route.route('/')
@password_change_required
def home_page():
    validate_status=check_auth_status()
    if validate_status == False:
        return render_template('auth_error.html')
    
    username= getUsername()
    usuario = Usuario.query.filter_by(login=username).first()
    nome = usuario.nome

    return render_template('home.html', nome=nome)

@home_route.route('/test-db')
def test_db():
    try:
        # Tenta buscar o primeiro registro da tabela 'setores'
        setor = Setor.query.first()
        if setor:
            return jsonify({
                "mensagem": "Conexão com o banco bem-sucedida!",
                "setor_exemplo": setor.nome_setor,
                "codigo": 200
            }), 200
        else:
            return jsonify({
                "mensagem": "Conexão OK, mas a tabela 'setores' está vazia.",
                "codigo": 200
            }), 200
    except SQLAlchemyError as e:
        # Caso dê erro de conexão ou de consulta
        return jsonify({
            "mensagem": f"Erro ao conectar ou consultar o banco: {str(e)}",
            "codigo": 500
        }), 500