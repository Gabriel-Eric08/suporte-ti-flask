from db_config import db
from sqlalchemy.orm import relationship
from datetime import datetime, timezone 
import pytz # Importa pytz para fusos horários

# Define o fuso horário de Brasília
FUSO_BRASILIA = pytz.timezone('America/Sao_Paulo')

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
    
class StatusChamado(db.Model):
    __tablename__ = 'status_chamado'
    status_id = db.Column(db.Integer, primary_key=True)
    nome_status = db.Column(db.String(50), nullable=False)
    
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
    
    # 1. Data de Abertura (Original)
    # CORRIGIDO: Usa o fuso horário de Brasília (FUSO_BRASILIA) no default
    datetime = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(FUSO_BRASILIA))
    
    # 2. NOVAS COLUNAS DE TEMPO DE ACOMPANHAMENTO
    datetime_atendido = db.Column(db.DateTime, nullable=True) # Quando o status_id muda para 2
    datetime_concluido = db.Column(db.DateTime, nullable=True) # Quando o status_id muda para 3
    
    # Informações do Solicitante
    user = db.Column(db.String(255))
    nome_completo = db.Column(db.String(255), nullable=False)
    cpf = db.Column(db.String(14))
    tipo_desc = db.Column(db.Text, nullable=True) 

    # --- CHAVES ESTRANGEIRAS ---
    setor_id = db.Column(db.Integer, db.ForeignKey('setores.setor_id'), nullable=False)
    tipo_id = db.Column(db.Integer, db.ForeignKey('tipos_chamado.tipo_id'), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('status_chamado.status_id'), nullable=False, default=1)
    plataforma_id = db.Column(db.Integer, db.ForeignKey('plataformas.plataforma_id'), nullable=True)

    # 3. CHAVE ESTRANGEIRA DO TÉCNICO RESPONSÁVEL
    tecnico_responsavel_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    
    # --- CAMPOS DE TEXTO ---
    cargo = db.Column(db.Text, nullable=True) 
    unidade_sei = db.Column(db.Text, nullable=True) 
    
    # Definição dos Relacionamentos
    setor = db.relationship('Setor', backref='chamados_setor_rel', lazy=True)
    tipo = db.relationship('TipoChamado', backref='chamados_tipo_rel', lazy=True)
    status = db.relationship('StatusChamado', backref='chamados_status_rel', lazy=True)
    plataforma = db.relationship('Plataforma', backref='chamados_plataforma_rel', lazy=True)
    
    # RELACIONAMENTO PARA O TÉCNICO RESPONSÁVEL
    tecnico_responsavel = db.relationship('Usuario', foreign_keys=[tecnico_responsavel_id], backref='chamados_atendidos', lazy=True)
    
    def __repr__(self):
        return f"Chamado(ID: {self.id}, Solicitante: {self.nome_completo}, Status: {self.status.nome_status if self.status else 'N/A'})"