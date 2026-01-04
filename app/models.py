"""
Modelos do banco de dados para o sistema PDV
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

db = SQLAlchemy()

class Configuracao(db.Model):
    __tablename__ = 'configuracao'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_loja = db.Column(db.String(200), nullable=False, default='Minha Loja')
    responsavel = db.Column(db.String(200), nullable=False, default='Responsável')
    formas_pagamento = db.Column(db.Text, nullable=False, default='Dinheiro,PIX,Cartão Débito,Cartão Crédito')
    
    @staticmethod
    def get_config():
        config = Configuracao.query.first()
        if not config:
            config = Configuracao()
            db.session.add(config)
            db.session.commit()
        return config

class Caixa(db.Model):
    __tablename__ = 'caixa'
    
    id = db.Column(db.Integer, primary_key=True)
    data_abertura = db.Column(db.DateTime, nullable=False, default=datetime.now)
    data_fechamento = db.Column(db.DateTime)
    operador = db.Column(db.String(200))
    troco_inicial = db.Column(db.Float, nullable=False, default=0.0)
    valor_contado = db.Column(db.Float)
    diferenca = db.Column(db.Float)
    observacao = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='aberto')  # aberto, fechado
    
    lancamentos = db.relationship('Lancamento', backref='caixa', lazy=True, cascade='all, delete-orphan')
    
    def calcular_totais(self):
        """Calcula os totais de entradas e saídas do caixa"""
        lancamentos = Lancamento.query.filter_by(caixa_id=self.id).all()
        
        total_entradas = sum(l.valor for l in lancamentos if l.tipo == 'entrada')
        total_saidas = sum(l.valor for l in lancamentos if l.tipo == 'saida')
        saldo_atual = self.troco_inicial + total_entradas - total_saidas
        
        return {
            'troco_inicial': self.troco_inicial,
            'total_entradas': total_entradas,
            'total_saidas': total_saidas,
            'saldo_atual': saldo_atual
        }
    
    def to_dict(self):
        totais = self.calcular_totais()
        return {
            'id': self.id,
            'data_abertura': self.data_abertura.isoformat() if self.data_abertura else None,
            'data_fechamento': self.data_fechamento.isoformat() if self.data_fechamento else None,
            'operador': self.operador,
            'troco_inicial': self.troco_inicial,
            'valor_contado': self.valor_contado,
            'diferenca': self.diferenca,
            'observacao': self.observacao,
            'status': self.status,
            **totais
        }

class Lancamento(db.Model):
    __tablename__ = 'lancamento'
    
    id = db.Column(db.Integer, primary_key=True)
    caixa_id = db.Column(db.Integer, db.ForeignKey('caixa.id'), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False, default=datetime.now)
    tipo = db.Column(db.String(20), nullable=False)  # entrada, saida
    categoria = db.Column(db.String(50), nullable=False)  # venda, sangria, suprimento, despesa, outros
    forma_pagamento = db.Column(db.String(50))
    valor = db.Column(db.Float, nullable=False)
    valor_recebido = db.Column(db.Float)  # Para vendas em dinheiro
    troco = db.Column(db.Float)  # Troco calculado
    descricao = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'caixa_id': self.caixa_id,
            'data_hora': self.data_hora.isoformat() if self.data_hora else None,
            'tipo': self.tipo,
            'categoria': self.categoria,
            'forma_pagamento': self.forma_pagamento,
            'valor': self.valor,
            'valor_recebido': self.valor_recebido,
            'troco': self.troco,
            'descricao': self.descricao
        }


class PushSubscription(db.Model):
    """Subscrições de Push Notifications"""
    __tablename__ = 'push_subscription'
    
    id = db.Column(db.Integer, primary_key=True)
    endpoint = db.Column(db.Text, nullable=False, unique=True)
    p256dh = db.Column(db.Text, nullable=False)
    auth = db.Column(db.Text, nullable=False)
    nome_dispositivo = db.Column(db.String(200))
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.now)
    
    # Configurações de notificação
    notificar_sangria = db.Column(db.Boolean, default=True)
    notificar_abertura = db.Column(db.Boolean, default=True)
    notificar_fechamento = db.Column(db.Boolean, default=True)
    notificar_resumo_diario = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome_dispositivo': self.nome_dispositivo,
            'ativo': self.ativo,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'notificar_sangria': self.notificar_sangria,
            'notificar_abertura': self.notificar_abertura,
            'notificar_fechamento': self.notificar_fechamento,
            'notificar_resumo_diario': self.notificar_resumo_diario
        }
