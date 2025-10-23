from flask import Blueprint, request, render_template
from models.models import Chamado, TipoChamado
from datetime import datetime
from utils.getUsername import getUsername

cliente_route=Blueprint('Cliente',__name__)

@cliente_route.route('/')
def cliente_page():
    data_inicial_str = request.args.get('data_inicial')
    data_final_str = request.args.get('data_final')
    status_id_str = request.args.get('status_id')
    tipo_id_str = request.args.get('tipo_id') # Valor selecionado para pré-seleção

    username = getUsername()
    # 2. Iniciar a consulta base
    query = Chamado.query.filter_by(user=username)
    
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
        'client_page.html', 
        chamados=chamados,
        tipos=tipos_chamado,        # <-- PASSANDO A LISTA DE TIPOS
        # status_list=status_chamado, # <-- Manter ou remover se não for necessário
        request=request             # <-- Necessário para pré-selecionar o filtro
    )