from db_config import db
from sqlalchemy.orm import relationship
from datetime import datetime, timezone # Importe timezone

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

# ------------------------------------------------
# CORREÇÃO CRÍTICA 1: Renomeada de 'UnidadeSei' para 'UnidadeSEI' para 
# coincidir com a referência na classe Chamado (unidade_sei = db.relationship('UnidadeSEI', ...)).
# Se a intenção era 'UnidadeSei', mude a referência na classe Chamado.
# Assumi que a referência em Chamado ('UnidadeSEI') está correta.
# ------------------------------------------------
class UnidadeSEI(db.Model):
    __tablename__ = 'unidades_sei'
    unidade_sei_id = db.Column(db.Integer, primary_key=True)
    codigo_unidade = db.Column(db.String(50), unique=True, nullable=False)
    nome_unidade = db.Column(db.String(255), nullable=False)
    
    def __repr__(self):
        return f"UnidadeSEI('{self.codigo_unidade}')"

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
    
# ------------------------------------------------
# Classe StatusChamado MUDANÇA 2: Definida ANTES de Chamado para evitar
# problemas de inicialização se você não quiser usar strings.
# REMOÇÃO DO CHAMADOS_STATUS (O relacionamento é definido em Chamado)
# ------------------------------------------------

class StatusChamado(db.Model):
    __tablename__ = 'status_chamado'
    status_id = db.Column(db.Integer, primary_key=True)
    nome_status = db.Column(db.String(50), nullable=False)
    
    # RELACIONAMENTO SQLAlchemy
    # O backref 'chamados_status_rel' será criado na classe StatusChamado
    # pela definição na classe Chamado. 
    # MANTENHA ESTA CLASSE SEM DEFINIÇÕES DE RELACIONAMENTO EXPLÍCITAS PARA EVITAR CONFLITOS.
    
    def __repr__(self):
        return f"StatusChamado('{self.status_id}', '{self.nome_status}')"

# ------------------------------------------------
# Classe Chamado
# ------------------------------------------------

class Chamado(db.Model):
    # Nome da tabela no banco de dados
    __tablename__ = 'chamados'

    # Colunas Principais
    id = db.Column(db.Integer, primary_key=True)
    
    # CORREÇÃO 3: Usando now(timezone.utc) (prática recomendada)
    datetime = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    # Informações do Solicitante
    user = db.Column(db.String(255))
    nome_completo = db.Column(db.String(255), nullable=False)
    cpf = db.Column(db.String(14))
    tipo_desc = db.Column(db.Text, nullable=True) 

    # Chaves Estrangeiras (Relacionamentos)
    setor_id = db.Column(db.Integer, db.ForeignKey('setores.setor_id'), nullable=False)
    tipo_id = db.Column(db.Integer, db.ForeignKey('tipos_chamado.tipo_id'), nullable=False)
    plataforma_id = db.Column(db.Integer, db.ForeignKey('plataformas.plataforma_id'), nullable=True)
    cargo_id = db.Column(db.Integer, db.ForeignKey('cargos.cargo_id'), nullable=True)
    unidade_sei_id = db.Column(db.Integer, db.ForeignKey('unidades_sei.unidade_sei_id'), nullable=True)
    status_id = db.Column(db.Integer, db.ForeignKey('status_chamado.status_id'), nullable=False, default=1)

    # Definição dos Relacionamentos (CORRIGIDO E UNIFICADO)
    
    # O backref deve ser único: 'chamados_setor_rel' vs 'setor' (Propriedade)
    setor = db.relationship('Setor', backref='chamados_setor_rel', lazy=True)
    
    # O backref deve ser único: 'chamados_tipo_rel' vs 'tipo' (Propriedade)
    tipo = db.relationship('TipoChamado', backref='chamados_tipo_rel', lazy=True)
    
    # O backref deve ser único: 'chamados_status_rel' vs 'status' (Propriedade)
    status = db.relationship('StatusChamado', backref='chamados_status_rel', lazy=True)
    
    # Certifique-se de que a classe 'Plataforma' existe e foi carregada
    plataforma = db.relationship('Plataforma', backref='chamados_plataforma_rel', lazy=True)
    
    # Certifique-se de que a classe 'Cargo' existe e foi carregada
    cargo = db.relationship('Cargo', backref='chamados_cargo_rel', lazy=True)
    
    # Usa a classe 'UnidadeSEI' (corrigida na definição acima)
    unidade_sei = db.relationship('UnidadeSEI', backref='chamados_unidade_sei_rel', lazy=True)

    def __repr__(self):
        # Acesso às informações relacionadas para exibição
        return f"Chamado(ID: {self.id}, Solicitante: {self.nome_completo}, Setor: {self.setor.nome_setor if self.setor else 'N/A'}, Status: {self.status.nome_status if self.status else 'N/A'})"