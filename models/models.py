from db_config import db
from sqlalchemy.orm import relationship
from datetime import datetime

# ------------------------------------------------
# TABELAS DE REFERÊNCIA (LOOKUP TABLES)
# ------------------------------------------------

class Setor(db.Model):
    __tablename__ = 'setores'
    setor_id = db.Column(db.Integer, primary_key=True)
    nome_setor = db.Column(db.String(100), unique=True, nullable=False)

    # Relacionamento de volta com Usuarios
    usuarios = db.relationship('Usuario', backref='setor', lazy=True)
    
    def __repr__(self):
        return f"Setor('{self.nome_setor}')"

class TipoChamado(db.Model):
    __tablename__ = 'tipos_chamado'
    tipo_id = db.Column(db.Integer, primary_key=True)
    nome_tipo = db.Column(db.String(50), unique=True, nullable=False)
    
    def __repr__(self):
        return f"TipoChamado('{self.nome_tipo}')"

class Plataforma(db.Model):
    __tablename__ = 'plataformas'
    plataforma_id = db.Column(db.Integer, primary_key=True)
    nome_plataforma = db.Column(db.String(50), unique=True, nullable=False)
    
    def __repr__(self):
        return f"Plataforma('{self.nome_plataforma}')"

class Cargo(db.Model):
    __tablename__ = 'cargos'
    cargo_id = db.Column(db.Integer, primary_key=True)
    nome_cargo = db.Column(db.String(100), unique=True, nullable=False)

    # Relacionamento de volta com Usuarios
    usuarios = db.relationship('Usuario', backref='cargo', lazy=True)
    
    def __repr__(self):
        return f"Cargo('{self.nome_cargo}')"

class UnidadeSei(db.Model):
    __tablename__ = 'unidades_sei'
    unidade_sei_id = db.Column(db.Integer, primary_key=True)
    codigo_unidade = db.Column(db.String(50), unique=True, nullable=False)
    nome_unidade = db.Column(db.String(255), nullable=False)
    
    def __repr__(self):
        return f"UnidadeSei('{self.codigo_unidade}')"

# ------------------------------------------------
# TABELAS PRINCIPAIS
# ------------------------------------------------

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False) # Armazena o hash da senha
    nome = db.Column(db.String(255), nullable=False)
    
    # Chaves Estrangeiras
    setor_id = db.Column(db.Integer, db.ForeignKey('setores.setor_id'), nullable=False)
    cargo_id = db.Column(db.Integer, db.ForeignKey('cargos.cargo_id'), nullable=False)
    
    def __repr__(self):
        return f"Usuario('{self.login}', '{self.nome}')"

class Chamado(db.Model):
    __tablename__ = 'chamados'
    id = db.Column(db.Integer, primary_key=True)
    
    # Colunas de Dados
    # datetime: Obrigatório e com valor padrão
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # user, tipo_desc, cpf: Permite NULL (Não obrigatórios)
    user = db.Column(db.String(255), nullable=True)     
    tipo_desc = db.Column(db.Text, nullable=True)
    nome_completo = db.Column(db.String(255), nullable=False) # MANTIDO como OBRIGATÓRIO
    cpf = db.Column(db.String(14), nullable=True)
    
    # Chaves Estrangeiras
    # setor_id e tipo_id: MANTIDOS como OBRIGATÓRIOS
    setor_id = db.Column(db.Integer, db.ForeignKey('setores.setor_id'), nullable=False)
    tipo_id = db.Column(db.Integer, db.ForeignKey('tipos_chamado.tipo_id'), nullable=False)
    
    # plataforma_id: CORRIGIDO para permitir NULL (Não obrigatório)
    plataforma_id = db.Column(db.Integer, db.ForeignKey('plataformas.plataforma_id'), nullable=True)
    
    # cargo_id e unidade_sei_id: Permite NULL (Não obrigatórios)
    cargo_id = db.Column(db.Integer, db.ForeignKey('cargos.cargo_id'), nullable=True) 
    unidade_sei_id = db.Column(db.Integer, db.ForeignKey('unidades_sei.unidade_sei_id'), nullable=True)
    status_id = db.Column(db.Integer, db.ForeignKey('status_chamado.status_id'), nullable=False, default=1)
    # Relacionamentos
    # (É necessário garantir que os modelos 'TipoChamado', 'Plataforma', etc.
    #  estejam definidos em 'models.py' ou no mesmo arquivo para que isso funcione.)
    # tipo_chamado = db.relationship('TipoChamado', backref='chamados_rel', lazy=True)
    # ... outros relacionamentos ...

    def __repr__(self):
        status_desc = self.status.nome_status if self.status else 'Status Desconhecido'
        return f"Chamado('{self.id}', '{self.nome_completo}', 'Status: {status_desc}')"
    
class StatusChamado(db.Model):
    __tablename__ = 'status_chamado'
    status_id = db.Column(db.Integer, primary_key=True)
    nome_status = db.Column(db.String(50), nullable=False)
    
    # RELACIONAMENTO SQLAlchemy (NÃO é uma coluna no banco de dados)
    # Cria a propriedade 'chamado.status' no modelo Chamado
    chamados_status = db.relationship('Chamado', backref='status', lazy=True) 

    def __repr__(self):
        return f"StatusChamado('{self.status_id}', '{self.nome_status}')"