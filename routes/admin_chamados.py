from flask import Blueprint, request, render_template, jsonify
# Certifique-se que TipoChamado está importado!
from models.models import Chamado, TipoChamado, StatusChamado 
from db_config import db
from datetime import datetime, timezone 

admin_chamado_route = Blueprint('Admin_chamados', __name__)

@admin_chamado_route.route('/')
def admin_page():
    # 1. Obter parâmetros de consulta do URL
    data_inicial_str = request.args.get('data_inicial')
    data_final_str = request.args.get('data_final')
    status_id_str = request.args.get('status_id')
    tipo_id_str = request.args.get('tipo_id') # Valor selecionado para pré-seleção

    # 2. Iniciar a consulta base
    query = Chamado.query
    
    # 3. Aplicar filtros dinamicamente (mantendo a lógica anterior)

    # Filtro de Data Inicial 
    if data_inicial_str:
        try:
            data_inicial = datetime.strptime(data_inicial_str, '%Y-%m-%d')
            query = query.filter(Chamado.datetime >= data_inicial)
        except ValueError:
            pass

    # Filtro de Data Final 
    if data_final_str:
        try:
            data_final_base = datetime.strptime(data_final_str, '%Y-%m-%d')
            data_final_limite = data_final_base.replace(hour=23, minute=59, second=59)
            query = query.filter(Chamado.datetime <= data_final_limite)
        except ValueError:
            pass

    # Filtro de Status
    if status_id_str and status_id_str.isdigit():
        status_id = int(status_id_str)
        query = query.filter(Chamado.status_id == status_id)

    # Filtro de Tipo de Chamado
    if tipo_id_str and tipo_id_str.isdigit():
        tipo_id = int(tipo_id_str)
        query = query.filter(Chamado.tipo_id == tipo_id)

    # 4. Finalizar a ordenação e executar a consulta dos CHAMADOS
    chamados = query.order_by(Chamado.datetime.desc()).all()

    # *************************************************************
    # NOVO PASSO 1: Consultar os TIPOS DE CHAMADO
    # *************************************************************
    tipos_chamado = TipoChamado.query.order_by(TipoChamado.nome_tipo).all()
    
    # Se o filtro de Status já estiver OK, você não precisa buscar ele novamente
    # Apenas para garantir que o Status funcione se você o estiver usando na página
    # status_chamado = StatusChamado.query.order_by(StatusChamado.status_id).all() 
    
    # 5. Renderizar o template com os chamados filtrados e a lista de tipos
    return render_template(
        'admin_page.html', 
        chamados=chamados,
        tipos=tipos_chamado,        # <-- PASSANDO A LISTA DE TIPOS
        # status_list=status_chamado, # <-- Manter ou remover se não for necessário
        request=request             # <-- Necessário para pré-selecionar o filtro
    )

@admin_chamado_route.route('/<int:id_chamado>', methods=['PUT'])
def atender_chamado(id_chamado):
    # Seu código existente...
    chamado = Chamado.query.filter_by(id=id_chamado).one_or_none()

    if chamado is None:
        return jsonify({"mensagem": f"Chamado com ID {id_chamado} não encontrado."}), 404

    # Status 2: Em Atendimento
    chamado.status_id = 2

    try:
        db.session.commit()
        return jsonify({
            "mensagem": f"Chamado {id_chamado} atualizado para 'Em Atendimento'.",
            "novo_status": chamado.status.nome_status
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar chamado: {e}")
        return jsonify({"mensagem": "Erro interno ao atualizar o chamado."}), 500

# --------------------------------------------------------
# 1. ROTA ADICIONADA: CONCLUIR CHAMADO (status_id = 3)
# --------------------------------------------------------
@admin_chamado_route.route('/concluir/<int:id_chamado>', methods=['PUT'])
def concluir_chamado(id_chamado):
    chamado = Chamado.query.filter_by(id=id_chamado).one_or_none()

    if chamado is None:
        return jsonify({"mensagem": f"Chamado com ID {id_chamado} não encontrado."}), 404

    # Assumindo que o ID 3 é "Concluído"
    chamado.status_id = 3 

    try:
        db.session.commit()
        return jsonify({
            "mensagem": f"Chamado {id_chamado} concluído com sucesso.",
            "novo_status": chamado.status.nome_status
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao concluir chamado: {e}")
        return jsonify({"mensagem": "Erro interno ao concluir o chamado."}), 500


# --------------------------------------------------------
# 2. ROTA ADICIONADA: RECUSAR CHAMADO (status_id = 4, exemplo)
# --------------------------------------------------------
@admin_chamado_route.route('/recusar/<int:id_chamado>', methods=['PUT'])
def recusar_chamado(id_chamado):
    chamado = Chamado.query.filter_by(id=id_chamado).one_or_none()

    if chamado is None:
        return jsonify({"mensagem": f"Chamado com ID {id_chamado} não encontrado."}), 404

    # Assumindo que o ID 4 é "Recusado/Cancelado"
    chamado.status_id = 4 

    try:
        db.session.commit()
        return jsonify({
            "mensagem": f"Chamado {id_chamado} recusado com sucesso.",
            "novo_status": chamado.status.nome_status
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao recusar chamado: {e}")
        return jsonify({"mensagem": "Erro interno ao recusar o chamado."}), 500