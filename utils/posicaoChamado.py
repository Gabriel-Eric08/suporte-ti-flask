from flask import jsonify
from models.models import Chamado
from sqlalchemy import asc # Importe para garantir a ordenação ascendente

def posicaoChamado(id_chamado):
    """
    Calcula a posição de um chamado na fila (apenas se o status for "Em Aberto").

    A posição é determinada ordenando todos os chamados com status_id=1
    pela data e hora de abertura (campo 'datetime') em ordem ascendente (o mais antigo primeiro).
    """

    # 1. Busca o chamado específico
    chamado = Chamado.query.filter_by(id=id_chamado).first()

    if not chamado:
        return jsonify({"success": False, "message": "Chamado não encontrado."}), 404

    # 2. Verifica o status do chamado
    # Assumimos que 'status_id=1' significa "Em Aberto"
    if chamado.status_id != 1:
        return jsonify({
            "success": True,
            "message": "O chamado não possui posição na fila, pois já foi atendido ou cancelado!",
            "posicao": None
        })

    # 3. Busca todos os chamados em aberto e ordena pelo campo 'datetime' (data de abertura)
    # O chamado com o 'datetime' mais antigo (menor) tem a posição 1.
    chamados_em_aberto = Chamado.query.filter_by(status_id=1).order_by(Chamado.datetime.asc()).all()

    # 4. Encontra a posição do chamado específico na lista (Índice + 1)
    posicao = None
    for index, ch in enumerate(chamados_em_aberto):
        if ch.id == id_chamado:
            # Posição na fila é o índice (base 0) + 1
            posicao = index + 1
            break
            
    # Este caso só ocorreria em falhas de concorrência extremas, mas é bom para robustez
    if posicao is None:
         return jsonify({
            "success": False,
            "message": "Erro ao determinar a posição na fila (Chamado em aberto, mas inconsistente na lista de abertos).",
            "posicao": None
        }), 500
        
    return jsonify({
        "success": True,
        "message": f"Seu chamado está na posição {posicao} da fila.",
        "posicao": posicao
    })