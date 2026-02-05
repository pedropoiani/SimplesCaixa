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
    formas_pagamento = db.Column(db.Text, nullable=False, default='Dinheiro,PIX,PIX Online,Cartão Débito,Cartão Crédito,Link de Cartão')
    
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
        
        total_entradas = sum(l.valor for l in lancamentos if l.tipo == 'entrada' and not l.estorno)
        total_saidas = sum(l.valor for l in lancamentos if l.tipo == 'saida' and not l.estorno)
        saldo_atual = self.troco_inicial + total_entradas - total_saidas
        
        return {
            'troco_inicial': self.troco_inicial,
            'total_entradas': total_entradas,
            'total_saidas': total_saidas,
            'saldo_atual': saldo_atual
        }
    
    def calcular_saldo_dinheiro(self):
        """Calcula o saldo esperado em dinheiro no caixa"""
        lancamentos = Lancamento.query.filter_by(caixa_id=self.id).all()
        
        # Vendas em dinheiro (excluindo estornados)
        vendas_dinheiro = sum(
            l.valor for l in lancamentos 
            if l.categoria == 'venda' and l.tipo == 'entrada' and l.forma_pagamento == 'Dinheiro'
            and not l.estorno
        )
        
        # Sangrias (sempre diminuem o dinheiro no caixa, excluindo estornados)
        sangrias = sum(
            l.valor for l in lancamentos 
            if l.categoria == 'sangria' and l.tipo == 'saida'
            and not l.estorno
        )
        
        # Suprimentos (sempre aumentam o dinheiro no caixa, excluindo estornados)
        suprimentos = sum(
            l.valor for l in lancamentos 
            if l.categoria == 'suprimento' and l.tipo == 'entrada'
            and not l.estorno
        )
        
        # Outras despesas em dinheiro (excluindo estornados)
        despesas_dinheiro = sum(
            l.valor for l in lancamentos 
            if l.categoria not in ['venda', 'sangria', 'suprimento'] 
            and l.tipo == 'saida' 
            and (l.forma_pagamento == 'Dinheiro' or not l.forma_pagamento)
            and not l.estorno
        )
        
        saldo_dinheiro = self.troco_inicial + vendas_dinheiro + suprimentos - sangrias - despesas_dinheiro
        
        return saldo_dinheiro
    
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
            'saldo_dinheiro': self.calcular_saldo_dinheiro(),
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
    estorno = db.relationship('Estorno', back_populates='lancamento', uselist=False, cascade='all, delete-orphan')
    
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
            'descricao': self.descricao,
            'estornado': bool(self.estorno),
            'motivo_estorno': self.estorno.motivo if self.estorno else None
        }


class Estorno(db.Model):
    __tablename__ = 'estorno'
    id = db.Column(db.Integer, primary_key=True)
    lancamento_id = db.Column(db.Integer, db.ForeignKey('lancamento.id'), nullable=False, unique=True)
    motivo = db.Column(db.Text, nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False, default=datetime.now)
    lancamento = db.relationship('Lancamento', back_populates='estorno')

    def to_dict(self):
        return {
            'id': self.id,
            'lancamento_id': self.lancamento_id,
            'motivo': self.motivo,
            'data_hora': self.data_hora.isoformat() if self.data_hora else None
        }

