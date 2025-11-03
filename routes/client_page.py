from flask import Blueprint, request, render_template, abort
# Importar o modelo Usuario é crucial para buscar o ID
from models.models import Chamado, TipoChamado, Usuario 
from datetime import datetime
from utils.getUsername import getUsername # Assume que retorna o login (username)
from utils.changePasswordRequired import password_change_required

cliente_route=Blueprint('Cliente',__name__)

@cliente_route.route('/')
@password_change_required
def cliente_page():
    data_inicial_str = request.args.get('data_inicial')
    data_final_str = request.args.get('data_final')
    status_id_str = request.args.get('status_id')
    tipo_id_str = request.args.get('tipo_id') 

    username = getUsername()
    
    # 1. NOVO: Buscar o ID do usuário pelo username (login)
    usuario_logado = Usuario.query.filter_by(login=username).first()
    
    # Se o usuário não for encontrado (ou não estiver logado, dependendo da sua autenticação)
    if not usuario_logado:
        # Você pode retornar um 403 (Forbidden) ou 401 (Unauthorized)
        # Neste caso, vamos retornar um 403 e encerrar.
        return abort(403, description="Usuário não logado ou não encontrado na base de dados.")
        
    user_id = usuario_logado.id

    # 2. Iniciar a consulta base, AGORA FILTRANDO POR user_id
    query = Chamado.query.filter_by(user_id=user_id) # <--- CORREÇÃO AQUI
    
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
    # Consultar os TIPOS DE CHAMADO
    # *************************************************************
    tipos_chamado = TipoChamado.query.order_by(TipoChamado.nome_tipo).all()
    
    # 5. Renderizar o template
    return render_template(
        'client_page.html.j2', 
        chamados=chamados,
        tipos=tipos_chamado,
        request=request
    )