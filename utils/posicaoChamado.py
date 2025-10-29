from flask import jsonify
from models.models import Chamado
from sqlalchemy import asc # Importe para garantir a ordenação ascendente

def posicaoChamado(id_chamado): # Novo nome para indicar que retorna um dict
    # 1. Busca o chamado específico
    chamado = Chamado.query.filter_by(id=id_chamado).first()

    if not chamado:
        # Retorna o dicionário de erro e o status HTTP 404
        return {"success": False, "message": "Chamado não encontrado."}, 404

    # 2. Verifica o status (Assumimos 'status_id=1' significa "Em Aberto")
    if chamado.status_id != 1:
        # Retorna o dicionário de sucesso (posição nula) e o status HTTP 200
        return {
            "success": True,
            "message": "O chamado não possui posição na fila, pois já foi atendido ou cancelado!",
            "posicao": None
        }, 200

    # 3. Executa a lógica de ordenação e busca da posição (Ideia 1)
    chamados_em_aberto = Chamado.query.filter_by(status_id=1).order_by(Chamado.datetime.asc()).all()
    posicao = None
    for index, ch in enumerate(chamados_em_aberto):
        if ch.id == id_chamado:
            posicao = index + 1
            break
            
    # 4. Retorna o dicionário de resultado e o status HTTP 200
    return {
        "success": True,
        "message": f"Seu chamado está na posição {posicao} da fila.",
        "posicao": posicao
    }, 200