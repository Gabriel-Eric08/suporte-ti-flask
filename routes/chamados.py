from flask import Flask, Blueprint, request, jsonify, render_template, abort
from models.models import Chamado, TipoChamado, Setor, Plataforma 
from datetime import datetime
from db_config import db
from sqlalchemy import and_
from utils.posicaoChamado import posicaoChamado

chamados_route = Blueprint('Chamados', __name__)

def calcular_posicao_na_fila(novo_chamado_id):
    """
    Calcula a quantidade de chamados ENVIADOS (status_id=1) 
    que foram criados ANTES do chamado com o ID fornecido.
    A posição é a contagem + 1. Assume que o ID é autoincrementável.
    """
    # Contamos quantos chamados com status_id = 1 têm um ID MENOR que o novo chamado
    contagem_antes = Chamado.query.filter(
        and_(
            Chamado.status_id == 1,
            Chamado.id < novo_chamado_id
        )
    ).count()
    
    # Sua posição na fila é a quantidade de pessoas na sua frente + 1
    return contagem_antes + 1

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
    nome_completo = data.get('nome_completo')
    setor_id = data.get('setor_id')
    tipo_id = data.get('tipo_id')
    
    # Campos opcionais ou condicionais
    # A variável Python ainda pode se chamar 'desc', mas o atributo do modelo é 'tipo_desc'
    desc = data.get('desc') 
    cpf = data.get('cpf')
    plataforma_id = data.get('plataforma_id')
    
    # NOVOS CAMPOS TEXTO 
    cargo = data.get('cargo')
    unidade_sei = data.get('unidade_sei')
    
    user_login = data.get('user')
    
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
        if not cpf or not cargo or not unidade_sei:
            return jsonify({
                "success": False,
                "message": "Chamado para criação de login (tipo 6) necessita dos campos: cpf, cargo e unidade_sei."
            }), 400

    # --- 4. Validação de Integridade de Chaves Estrangeiras ---

    if not Setor.query.get(setor_id):
        return jsonify({"success": False, "message": f"Setor ID {setor_id} inválido."}), 400
    if not TipoChamado.query.get(tipo_id):
        return jsonify({"success": False, "message": f"Tipo de Chamado ID {tipo_id} inválido."}), 400
    
    if plataforma_id and not Plataforma.query.get(plataforma_id):
        return jsonify({"success": False, "message": f"Plataforma ID {plataforma_id} inválida."}), 400
    
    
    # --- 5. Criação e Inserção do Novo Chamado ---
    
    novo_chamado = Chamado(
        # Campos obrigatórios
        nome_completo=nome_completo,
        setor_id=setor_id,
        tipo_id=tipo_id,
        status_id=1, # Configura o status inicial como ENVIADO (1)
        
        # Campos de dados
        user=user_login,
        tipo_desc=desc, # <--- CORRIGIDO: Passando 'desc' para o campo 'tipo_desc' do modelo
        cpf=cpf,
        
        # Chaves Estrangeiras opcionais/condicionais
        plataforma_id=plataforma_id,
        
        # NOVOS CAMPOS TEXTO
        cargo=cargo,
        unidade_sei=unidade_sei,
        
    )
    
    try:
        db.session.add(novo_chamado)
        db.session.commit()
        
        # O ID é gerado após o commit para o objeto 'novo_chamado'
        novo_chamado_id = novo_chamado.id
        
        # 6. CÁLCULO E RETORNO DA POSIÇÃO NA FILA
        posicao = calcular_posicao_na_fila(novo_chamado_id)

        return jsonify({
            "success": True,
            "message": "Chamado registrado com sucesso!",
            "id": novo_chamado_id,
            "posicao_na_fila": posicao # <-- CHAVE EXPORTADA PARA O JS
        }), 201 # 201 Created
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao salvar chamado: {e}")
        # Se ocorrer um erro aqui, é um erro de banco de dados (500)
        return jsonify({
            "success": False,
            "message": "Erro interno ao salvar chamado no banco de dados."
        }), 500
    
# Rota /last (mantida do seu código original)
@chamados_route.route('/last', methods=['GET'])
def posicao_fila():
    """
    Retorna a quantidade total de chamados atualmente com status 'Enviado' (status_id=1).
    """
    try:
        quantidade_enviados = Chamado.query.filter_by(status_id=1).count()
        
        return jsonify({
            "success": True,
            "status_name": "Enviado",
            "status_id": 1,
            "quantidade": quantidade_enviados
        }), 200

    except Exception as e:
        print(f"Erro ao buscar quantidade de chamados: {e}")
        return jsonify({
            "success": False,
            "message": "Erro interno ao consultar o banco de dados."
        }), 500
    
@chamados_route.route('/<int:id_chamado>')
def detalhes_chamado(id_chamado):
    
    # 1. Busca o chamado principal
    chamado = Chamado.query.filter_by(id=id_chamado).first()
    
    # Tratamento de Chamado Não Encontrado
    if chamado is None:
        # Retorna 404
        return abort(404, description=f"Chamado com ID {id_chamado} não encontrado.") 

    # 2. Chama a função auxiliar, que agora retorna (dicionário, status_code)
    # Ignoramos o status_code (pode ser usado para log) e pegamos apenas o dicionário
    dados_posicao, _ = posicaoChamado(id_chamado)
    
    # 3. Extrai a posição do dicionário (AGORA FUNCIONA!)
    posicao = dados_posicao.get("posicao")
    
    # 4. Formata a variável 'posicao' para o template: "" se não tiver posição
    posicao_formatada = str(posicao) if posicao is not None else ""
    
    # 5. Renderiza o template
    return render_template(
        'detalhes_chamado.html', 
        chamado=chamado,
        posicao=posicao_formatada # Variável passada para o Jinja2
    )