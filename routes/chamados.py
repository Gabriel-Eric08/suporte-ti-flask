from flask import Flask, Blueprint, request, jsonify
# Importe todos os modelos necessários para validação
from models.models import Chamado, TipoChamado, Setor, Plataforma, Cargo, UnidadeSEI
from datetime import datetime
from db_config import db
# from utils.getUsername import getUsername # (Não usado na rota, mas mantido)

chamados_route = Blueprint('Chamados', __name__)

@chamados_route.route('/', methods=['POST'])
def enviar_chamado():
    data = request.get_json()
    
    if not data:
        return jsonify({
            "success": False,
            "message": "Requisição feita sem dados ou mal formatada!"
        }), 400
    
    # --- 1. Inicialização de Variáveis e Extração de Dados ---
    
    # Campos base obrigatórios
    nome_completo = data.get('nome_completo')  # Nome completo é obrigatório para o Chamado
    setor_id = data.get('setor_id')
    tipo_id = data.get('tipo_id')
    
    # Campos opcionais ou condicionais
    desc = data.get('desc')
    cpf = data.get('cpf')
    plataforma_id = data.get('plataforma_id')
    cargo_id = data.get('cargo_id')
    unidade_sei_id = data.get('unidade_sei_id')
    user_login = data.get('user') # Assumindo que 'user' é o login, se houver
    
    # --- 2. Validação de Campos Base ---
    
    if not nome_completo or not setor_id or not tipo_id:
        return jsonify({
            "success": False,
            "message": "Requisição necessita dos campos: nome_completo, setor_id e tipo_id."
        }), 400
    
    # --- 3. Validação de Campos Condicionais (Tipo de Chamado) ---
    
    # Tipo 5: Recuperação de Senha de Acesso (Requer plataforma)
    if tipo_id == 5:
        if not plataforma_id:
            return jsonify({
                "success": False,
                "message": "Chamado para recuperação de senha (tipo 5) necessita do campo plataforma_id."
            }), 400
            
    # Tipo 6: Criação de Novo Login (Requer cpf, cargo e unidade_sei)
    elif tipo_id == 6:
        if not cpf or not cargo_id or not unidade_sei_id:
            return jsonify({
                "success": False,
                "message": "Chamado para criação de login (tipo 6) necessita dos campos: cpf, cargo_id e unidade_sei_id."
            }), 400

    # --- 4. Validação de Integridade de Chaves Estrangeiras ---
    # Garante que os IDs fornecidos existam no banco de dados.

    if not Setor.query.get(setor_id):
        return jsonify({"success": False, "message": f"Setor ID {setor_id} inválido."}), 400
    if not TipoChamado.query.get(tipo_id):
        return jsonify({"success": False, "message": f"Tipo de Chamado ID {tipo_id} inválido."}), 400
    
    if plataforma_id and not Plataforma.query.get(plataforma_id):
        return jsonify({"success": False, "message": f"Plataforma ID {plataforma_id} inválida."}), 400
    
    if cargo_id and not Cargo.query.get(cargo_id):
        return jsonify({"success": False, "message": f"Cargo ID {cargo_id} inválido."}), 400
    
    if unidade_sei_id and not UnidadeSEI.query.get(unidade_sei_id):
        return jsonify({"success": False, "message": f"Unidade SEI ID {unidade_sei_id} inválida."}), 400
    
    # --- 5. Criação e Inserção do Novo Chamado ---
    
    novo_chamado = Chamado(
        # Campos obrigatórios
        nome_completo=nome_completo,
        setor_id=setor_id,
        tipo_id=tipo_id,
        
        # Campos de dados
        user=user_login, # Se houver um login
        tipo_desc=desc,
        cpf=cpf,
        
        # Chaves Estrangeiras opcionais/condicionais
        plataforma_id=plataforma_id,
        cargo_id=cargo_id,
        unidade_sei_id=unidade_sei_id,
        
        # status_id é definido por DEFAULT=1 no banco de dados (Enviado)
        # datetime é definido por DEFAULT no banco de dados ou no modelo (datetime.utcnow)
    )
    
    try:
        db.session.add(novo_chamado)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Chamado registrado com sucesso!",
            "id": novo_chamado.id
        }), 201 # 201 Created
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao salvar chamado: {e}")
        return jsonify({
            "success": False,
            "message": "Erro interno ao salvar chamado no banco de dados."
        }), 500