from flask import Blueprint, request, render_template, jsonify, redirect, url_for
from models.models import Chamado, TipoChamado, Usuario, StatusChamado 
from db_config import db 
from datetime import datetime
# REMOVIDO: timezone, para usar pytz
import pytz # <-- NOVO: Importa pytz para fusos horários
from utils.getUsername import getUsername

admin_chamado_route = Blueprint('Admin_chamados', __name__)

# Define o fuso horário de Brasília de forma global para o módulo
FUSO_BRASILIA = pytz.timezone('America/Sao_Paulo')

def verificar_admin_ou_funcionario():
    """
    Verifica se o usuário logado tem cargo_id 2 (Funcionário) ou 3 (Admin).
    Retorna o objeto Usuario se autorizado, ou None caso contrário.
    """
    login_usuario = getUsername()
    if not login_usuario:
        return None # Não logado

    # Busca o usuário pelo login armazenado no cookie
    usuario = Usuario.query.filter_by(login=login_usuario).first()
    
    # Verifica se o usuário existe e se o cargo_id é 2 ou 3
    if usuario and usuario.cargo_id in [2, 3]:
        return usuario
    
    return None


@admin_chamado_route.route('/')
def admin_page():
    # --- 0. VERIFICAÇÃO DE ACESSO ---
    usuario_autorizado = verificar_admin_ou_funcionario()
    
    if usuario_autorizado is None:
        return render_template('admin_acesso_negado.html'), 403 
    # -------------------------------
    
    # 1. Obter parâmetros de consulta do URL
    data_inicial_str = request.args.get('data_inicial')
    data_final_str = request.args.get('data_final')
    status_id_str = request.args.get('status_id')
    tipo_id_str = request.args.get('tipo_id')

    # 2. Iniciar a consulta base
    query = Chamado.query
    
    # 3. Aplicar filtros dinamicamente
    # Filtro de Data Inicial 
    if data_inicial_str:
        try:
            data_inicial = datetime.strptime(data_inicial_str, '%Y-%m-%d')
            # CORREÇÃO: Torna a data "aware" no fuso de Brasília, no início do dia
            data_inicial_aware = FUSO_BRASILIA.localize(data_inicial.replace(hour=0, minute=0, second=0))
            query = query.filter(Chamado.datetime >= data_inicial_aware)
        except ValueError:
            pass

    # Filtro de Data Final 
    if data_final_str:
        try:
            data_final_base = datetime.strptime(data_final_str, '%Y-%m-%d')
            # Garante que pega até o final do dia
            data_final_limite = data_final_base.replace(hour=23, minute=59, second=59) 
            # CORREÇÃO: Torna a data "aware" no fuso de Brasília, no final do dia
            data_final_aware = FUSO_BRASILIA.localize(data_final_limite)
            query = query.filter(Chamado.datetime <= data_final_aware)
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

    # 4. Finalizar a ordenação e executar a consulta
    chamados = query.order_by(Chamado.datetime.desc()).all()
    
    # 5. Consultar Tipos de Chamado para o filtro
    tipos_chamado = TipoChamado.query.order_by(TipoChamado.nome_tipo).all()

    # 6. Renderizar o template original para usuários autorizados
    return render_template(
        'admin_page.html', 
        chamados=chamados,
        tipos=tipos_chamado,
        request=request
    )

@admin_chamado_route.route('/<int:id_chamado>/atender', methods=['PUT'])
def atender_chamado(id_chamado):
    # --- VERIFICAÇÃO DE ACESSO E TÉCNICO ---
    tecnico = verificar_admin_ou_funcionario()
    if tecnico is None:
        return jsonify({"mensagem": "Acesso negado. Necessário ser Administrador ou Funcionário."}), 403
    # -------------------------------------

    chamado = Chamado.query.filter_by(id=id_chamado).one_or_none()

    if chamado is None:
        return jsonify({"mensagem": f"Chamado com ID {id_chamado} não encontrado."}), 404
    
    # Apenas mude se o status atual for 'Enviado' (Status ID 1)
    if chamado.status_id == 1:
        # Status 2: Em Atendimento
        chamado.status_id = 2
        # --- REGISTRA A DATA/HORA E O TÉCNICO RESPONSÁVEL ---
        # CORRIGIDO: Usa o horário atual de Brasília
        chamado.datetime_atendido = datetime.now(FUSO_BRASILIA) 
        chamado.tecnico_responsavel_id = tecnico.id 
    else:
        return jsonify({"mensagem": f"Chamado {id_chamado} já está em atendimento ou concluído."}), 400

    try:
        db.session.commit()
        return jsonify({
            "mensagem": f"Chamado {id_chamado} atualizado para 'Em Atendimento'.",
            "novo_status": chamado.status.nome_status if chamado.status else 'Em Atendimento'
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar chamado: {e}")
        return jsonify({"mensagem": "Erro interno ao atualizar o chamado."}), 500

# --------------------------------------------------------
# ROTA: CONCLUIR CHAMADO
# --------------------------------------------------------
@admin_chamado_route.route('/<int:id_chamado>/concluir', methods=['PUT'])
def concluir_chamado(id_chamado):
    # --- VERIFICAÇÃO DE ACESSO E TÉCNICO ---
    tecnico = verificar_admin_ou_funcionario()
    if tecnico is None:
        return jsonify({"mensagem": "Acesso negado. Necessário ser Administrador ou Funcionário."}), 403
    # -------------------------------------

    chamado = Chamado.query.filter_by(id=id_chamado).one_or_none()

    if chamado is None:
        return jsonify({"mensagem": f"Chamado com ID {id_chamado} não encontrado."}), 404

    # Apenas mude se o status atual for 'Enviado' (1) ou 'Em Atendimento' (2).
    if chamado.status_id in [1, 2]:
        # Assumindo que o ID 3 é "Concluído"
        chamado.status_id = 3
        # --- REGISTRA A DATA/HORA DE CONCLUSÃO ---
        # CORRIGIDO: Usa o horário atual de Brasília
        chamado.datetime_concluido = datetime.now(FUSO_BRASILIA)
        
        # Garante que o responsável está registrado
        if chamado.tecnico_responsavel_id is None:
            chamado.tecnico_responsavel_id = tecnico.id 
    else:
        return jsonify({"mensagem": f"Chamado {id_chamado} já está concluído ou recusado."}), 400


    try:
        db.session.commit()
        return jsonify({
            "mensagem": f"Chamado {id_chamado} concluído com sucesso.",
            "novo_status": chamado.status.nome_status if chamado.status else 'Concluído'
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao concluir chamado: {e}")
        return jsonify({"mensagem": "Erro interno ao concluir o chamado."}), 500


# --------------------------------------------------------
# ROTA: RECUSAR CHAMADO
# --------------------------------------------------------
@admin_chamado_route.route('/<int:id_chamado>/recusar', methods=['PUT'])
def recusar_chamado(id_chamado):
    chamado = Chamado.query.filter_by(id=id_chamado).one_or_none()

    if chamado is None:
        return jsonify({"mensagem": f"Chamado com ID {id_chamado} não encontrado."}), 404

    # Apenas recusamos se não estiver já concluído ou recusado.
    # Assumindo que 3 é "Concluído" e 4 é "Recusado/Cancelado"
    if chamado.status_id not in [3, 4]: 
        # Assumindo que o ID 4 é "Recusado/Cancelado"
        chamado.status_id = 4 
    else:
        return jsonify({"mensagem": f"Chamado {id_chamado} já está concluído ou recusado."}), 400


    try:
        db.session.commit()
        # Se 'chamado.status' não existir (por exemplo, se o relacionamento não carregar), 
        # cai no fallback 'Recusado/Cancelado'.
        return jsonify({
            "mensagem": f"Chamado {id_chamado} recusado com sucesso.",
            "novo_status": chamado.status.nome_status if chamado.status else 'Recusado/Cancelado'
        }), 200

    except Exception as e:
        db.session.rollback()
        print(f"Erro ao recusar chamado: {e}")
        return jsonify({"mensagem": "Erro interno ao recusar o chamado."}), 500