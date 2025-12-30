#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de gerenciamento do banco de dados SQLite
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class Database:
    """Classe para gerenciar o banco de dados SQLite"""
    
    def __init__(self, db_path: str = None):
        """Inicializa a conexão com o banco de dados"""
        if db_path is None:
            # Cria o banco na pasta do usuário
            home_dir = os.path.expanduser("~")
            app_dir = os.path.join(home_dir, ".pdvmf")
            os.makedirs(app_dir, exist_ok=True)
            db_path = os.path.join(app_dir, "pdvmf.db")
        
        self.db_path = db_path
        self.conn = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Conecta ao banco de dados"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
    
    def close(self):
        """Fecha a conexão com o banco"""
        if self.conn:
            self.conn.close()
    
    def create_tables(self):
        """Cria as tabelas necessárias no banco"""
        cursor = self.conn.cursor()
        
        # Tabela de configurações
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuracoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_loja TEXT NOT NULL,
                responsavel TEXT,
                senha_adm TEXT DEFAULT '741856',
                created_at TIMESTAMP DEFAULT (datetime('now', 'localtime')),
                updated_at TIMESTAMP DEFAULT (datetime('now', 'localtime'))
            )
        """)
        
        # Adicionar coluna senha_adm se não existir (para bancos antigos)
        try:
            cursor.execute("ALTER TABLE configuracoes ADD COLUMN senha_adm TEXT DEFAULT '741856'")
            self.conn.commit()
        except:
            pass  # Coluna já existe
        
        # Tabela de formas de pagamento
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS formas_pagamento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL UNIQUE,
                ativo INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT (datetime('now', 'localtime'))
            )
        """)
        
        # Tabela de caixa (abertura)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS caixa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operador TEXT,
                troco_inicial REAL NOT NULL DEFAULT 0,
                data_abertura TIMESTAMP DEFAULT (datetime('now', 'localtime')),
                data_fechamento TIMESTAMP,
                status TEXT DEFAULT 'aberto',
                total_entradas REAL DEFAULT 0,
                total_saidas REAL DEFAULT 0,
                saldo_final REAL DEFAULT 0,
                valor_contado REAL,
                diferenca REAL,
                observacoes TEXT
            )
        """)
        
        # Tabela de lançamentos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lancamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                caixa_id INTEGER NOT NULL,
                tipo TEXT NOT NULL,
                categoria TEXT NOT NULL,
                forma_pagamento_id INTEGER,
                valor REAL NOT NULL,
                observacao TEXT,
                data_hora TIMESTAMP DEFAULT (datetime('now', 'localtime')),
                data_edicao TIMESTAMP,
                operador TEXT,
                cancelado INTEGER DEFAULT 0,
                FOREIGN KEY (caixa_id) REFERENCES caixa(id),
                FOREIGN KEY (forma_pagamento_id) REFERENCES formas_pagamento(id)
            )
        """)
        
        # Adicionar coluna data_edicao se não existir (para bancos antigos)
        try:
            cursor.execute("ALTER TABLE lancamentos ADD COLUMN data_edicao TIMESTAMP")
            self.conn.commit()
        except:
            pass  # Coluna já existe
        
        # Tabela de fechamentos (histórico)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fechamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                caixa_id INTEGER NOT NULL,
                troco_inicial REAL,
                total_entradas REAL,
                total_saidas REAL,
                saldo_esperado REAL,
                valor_contado REAL,
                diferenca REAL,
                data_fechamento TIMESTAMP DEFAULT (datetime('now', 'localtime')),
                operador TEXT,
                observacoes TEXT,
                FOREIGN KEY (caixa_id) REFERENCES caixa(id)
            )
        """)
        
        # Tabela de logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                acao TEXT NOT NULL,
                detalhes TEXT,
                operador TEXT,
                data_hora TIMESTAMP DEFAULT (datetime('now', 'localtime'))
            )
        """)
        
        self.conn.commit()
        
        # Inserir formas de pagamento padrão
        self._inserir_formas_pagamento_padrao()
    
    def _inserir_formas_pagamento_padrao(self):
        """Insere as formas de pagamento padrão se não existirem"""
        cursor = self.conn.cursor()
        formas_padrao = ["Dinheiro", "PIX", "Cartão Débito", "Cartão Crédito"]
        
        for forma in formas_padrao:
            cursor.execute("""
                INSERT OR IGNORE INTO formas_pagamento (nome) VALUES (?)
            """, (forma,))
        
        self.conn.commit()
    
    # ========== CONFIGURAÇÕES ==========
    
    def salvar_configuracao(self, nome_loja: str, responsavel: str = "") -> int:
        """Salva ou atualiza configurações da loja"""
        cursor = self.conn.cursor()
        
        # Verifica se já existe configuração
        cursor.execute("SELECT id FROM configuracoes LIMIT 1")
        config = cursor.fetchone()
        
        if config:
            cursor.execute("""
                UPDATE configuracoes 
                SET nome_loja = ?, responsavel = ?, updated_at = datetime('now', 'localtime')
                WHERE id = ?
            """, (nome_loja, responsavel, config['id']))
            config_id = config['id']
        else:
            cursor.execute("""
                INSERT INTO configuracoes (nome_loja, responsavel)
                VALUES (?, ?)
            """, (nome_loja, responsavel))
            config_id = cursor.lastrowid
        
        self.conn.commit()
        return config_id
    
    def obter_configuracao(self) -> Optional[Dict]:
        """Obtém as configurações da loja"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM configuracoes ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        return dict(result) if result else None
    
    def verificar_senha_adm(self, senha: str) -> bool:
        """Verifica se a senha de administrador está correta"""
        config = self.obter_configuracao()
        if config:
            senha_atual = config.get('senha_adm', '741856')
            return senha == senha_atual
        # Se não há configuração, usa senha padrão
        return senha == '741856'
    
    def alterar_senha_adm(self, nova_senha: str) -> bool:
        """Altera a senha de administrador"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM configuracoes LIMIT 1")
        config = cursor.fetchone()
        
        if config:
            cursor.execute("""
                UPDATE configuracoes 
                SET senha_adm = ?, updated_at = datetime('now', 'localtime')
                WHERE id = ?
            """, (nova_senha, config['id']))
        else:
            cursor.execute("""
                INSERT INTO configuracoes (nome_loja, senha_adm)
                VALUES ('Minha Loja', ?)
            """, (nova_senha,))
        
        self.conn.commit()
        return True
    
    # ========== FORMAS DE PAGAMENTO ==========
    
    def listar_formas_pagamento(self, apenas_ativas: bool = True) -> List[Dict]:
        """Lista todas as formas de pagamento"""
        cursor = self.conn.cursor()
        if apenas_ativas:
            cursor.execute("SELECT * FROM formas_pagamento WHERE ativo = 1 ORDER BY nome")
        else:
            cursor.execute("SELECT * FROM formas_pagamento ORDER BY nome")
        return [dict(row) for row in cursor.fetchall()]
    
    def adicionar_forma_pagamento(self, nome: str) -> int:
        """Adiciona uma nova forma de pagamento"""
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO formas_pagamento (nome) VALUES (?)", (nome,))
        self.conn.commit()
        return cursor.lastrowid
    
    def ativar_desativar_forma_pagamento(self, forma_id: int, ativo: bool):
        """Ativa ou desativa uma forma de pagamento"""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE formas_pagamento SET ativo = ? WHERE id = ?", 
                      (1 if ativo else 0, forma_id))
        self.conn.commit()
    
    # ========== CAIXA ==========
    
    def abrir_caixa(self, troco_inicial: float, operador: str = "") -> int:
        """Abre um novo caixa"""
        cursor = self.conn.cursor()
        data_abertura = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO caixa (troco_inicial, operador, status, data_abertura)
            VALUES (?, ?, 'aberto', ?)
        """, (troco_inicial, operador, data_abertura))
        caixa_id = cursor.lastrowid
        self.conn.commit()
        
        # Registrar log
        self.registrar_log("Abertura de Caixa", 
                          f"Troco inicial: R$ {troco_inicial:.2f}", operador)
        
        return caixa_id
    
    def obter_caixa_aberto(self) -> Optional[Dict]:
        """Obtém o caixa atualmente aberto"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM caixa 
            WHERE status = 'aberto' 
            ORDER BY data_abertura DESC 
            LIMIT 1
        """)
        result = cursor.fetchone()
        return dict(result) if result else None
    
    def fechar_caixa(self, caixa_id: int, valor_contado: float = None, 
                     observacoes: str = "", operador: str = "") -> Dict:
        """Fecha o caixa e calcula totais"""
        cursor = self.conn.cursor()
        
        # Buscar informações do caixa
        cursor.execute("SELECT * FROM caixa WHERE id = ?", (caixa_id,))
        caixa = dict(cursor.fetchone())
        
        # Calcular totais
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN tipo = 'Entrada' AND cancelado = 0 THEN valor ELSE 0 END) as total_entradas,
                SUM(CASE WHEN tipo = 'Saída' AND cancelado = 0 THEN valor ELSE 0 END) as total_saidas
            FROM lancamentos
            WHERE caixa_id = ?
        """, (caixa_id,))
        totais = dict(cursor.fetchone())
        
        total_entradas = totais['total_entradas'] or 0
        total_saidas = totais['total_saidas'] or 0
        saldo_final = caixa['troco_inicial'] + total_entradas - total_saidas
        
        diferenca = None
        if valor_contado is not None:
            diferenca = valor_contado - saldo_final
        
        # Atualizar caixa
        cursor.execute("""
            UPDATE caixa 
            SET status = 'fechado',
                data_fechamento = datetime('now', 'localtime'),
                total_entradas = ?,
                total_saidas = ?,
                saldo_final = ?,
                valor_contado = ?,
                diferenca = ?,
                observacoes = ?
            WHERE id = ?
        """, (total_entradas, total_saidas, saldo_final, valor_contado, 
              diferenca, observacoes, caixa_id))
        
        # Registrar fechamento no histórico
        cursor.execute("""
            INSERT INTO fechamentos 
            (caixa_id, troco_inicial, total_entradas, total_saidas, 
             saldo_esperado, valor_contado, diferenca, operador, observacoes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (caixa_id, caixa['troco_inicial'], total_entradas, total_saidas,
              saldo_final, valor_contado, diferenca, operador, observacoes))
        
        self.conn.commit()
        
        # Registrar log
        self.registrar_log("Fechamento de Caixa", 
                          f"Saldo final: R$ {saldo_final:.2f}", operador)
        
        return {
            'troco_inicial': caixa['troco_inicial'],
            'total_entradas': total_entradas,
            'total_saidas': total_saidas,
            'saldo_final': saldo_final,
            'valor_contado': valor_contado,
            'diferenca': diferenca
        }
    
    # ========== LANÇAMENTOS ==========
    
    def adicionar_lancamento(self, caixa_id: int, tipo: str, categoria: str,
                            valor: float, forma_pagamento_id: int = None,
                            observacao: str = "", operador: str = "") -> int:
        """Adiciona um novo lançamento"""
        cursor = self.conn.cursor()
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO lancamentos 
            (caixa_id, tipo, categoria, valor, forma_pagamento_id, observacao, operador, data_hora)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (caixa_id, tipo, categoria, valor, forma_pagamento_id, observacao, operador, data_hora))
        lancamento_id = cursor.lastrowid
        self.conn.commit()
        
        # Registrar log
        self.registrar_log(f"Lançamento - {tipo}", 
                          f"{categoria}: R$ {valor:.2f}", operador)
        
        return lancamento_id
    
    def listar_lancamentos(self, caixa_id: int = None, 
                          data_inicio: str = None, data_fim: str = None,
                          tipo: str = None, categoria: str = None,
                          limite: int = None) -> List[Dict]:
        """Lista lançamentos com filtros opcionais"""
        cursor = self.conn.cursor()
        
        query = """
            SELECT l.*, fp.nome as forma_pagamento_nome, c.data_abertura
            FROM lancamentos l
            LEFT JOIN formas_pagamento fp ON l.forma_pagamento_id = fp.id
            LEFT JOIN caixa c ON l.caixa_id = c.id
            WHERE l.cancelado = 0
        """
        params = []
        
        if caixa_id:
            query += " AND l.caixa_id = ?"
            params.append(caixa_id)
        
        if data_inicio and data_inicio.strip():
            query += " AND DATE(l.data_hora) >= DATE(?)"
            params.append(data_inicio.strip())
        
        if data_fim and data_fim.strip():
            query += " AND DATE(l.data_hora) <= DATE(?)"
            params.append(data_fim.strip())
        
        if tipo and tipo.strip():
            query += " AND l.tipo = ?"
            params.append(tipo.strip())
        
        if categoria and categoria.strip():
            query += " AND l.categoria = ?"
            params.append(categoria.strip())
        
        query += " ORDER BY l.data_hora DESC"
        
        if limite:
            query += f" LIMIT {int(limite)}"
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def cancelar_lancamento(self, lancamento_id: int, operador: str = ""):
        """Cancela um lançamento"""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE lancamentos SET cancelado = 1 WHERE id = ?", 
                      (lancamento_id,))
        self.conn.commit()
        
        self.registrar_log("Cancelamento de Lançamento", 
                          f"Lançamento ID: {lancamento_id}", operador)
    
    def atualizar_lancamento(self, lancamento_id: int, tipo: str, categoria: str, 
                             valor: float, forma_pagamento_id: int = None, 
                             observacao: str = "", operador: str = ""):
        """Atualiza um lançamento existente"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE lancamentos 
            SET tipo = ?, categoria = ?, valor = ?, forma_pagamento_id = ?, observacao = ?,
                data_edicao = datetime('now', 'localtime')
            WHERE id = ?
        """, (tipo, categoria, valor, forma_pagamento_id, observacao, lancamento_id))
        self.conn.commit()
        
        self.registrar_log("Edição de Lançamento", 
                          f"Lançamento ID: {lancamento_id} - Valor: {valor}", operador)
    
    def obter_lancamento(self, lancamento_id: int) -> Dict:
        """Obtém um lançamento pelo ID"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT l.*, fp.nome as forma_pagamento_nome
            FROM lancamentos l
            LEFT JOIN formas_pagamento fp ON l.forma_pagamento_id = fp.id
            WHERE l.id = ?
        """, (lancamento_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def obter_totais_caixa_aberto(self, caixa_id: int) -> Dict:
        """Obtém os totais do caixa aberto em tempo real"""
        cursor = self.conn.cursor()
        
        # Buscar troco inicial
        cursor.execute("SELECT troco_inicial FROM caixa WHERE id = ?", (caixa_id,))
        troco_inicial = cursor.fetchone()['troco_inicial']
        
        # Calcular totais
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN tipo = 'Entrada' AND cancelado = 0 THEN valor ELSE 0 END) as total_entradas,
                SUM(CASE WHEN tipo = 'Saída' AND cancelado = 0 THEN valor ELSE 0 END) as total_saidas
            FROM lancamentos
            WHERE caixa_id = ?
        """, (caixa_id,))
        totais = dict(cursor.fetchone())
        
        total_entradas = totais['total_entradas'] or 0
        total_saidas = totais['total_saidas'] or 0
        saldo_atual = troco_inicial + total_entradas - total_saidas
        
        # Totais por forma de pagamento
        cursor.execute("""
            SELECT fp.nome, SUM(l.valor) as total
            FROM lancamentos l
            JOIN formas_pagamento fp ON l.forma_pagamento_id = fp.id
            WHERE l.caixa_id = ? AND l.tipo = 'Entrada' AND l.cancelado = 0
            GROUP BY fp.nome
        """, (caixa_id,))
        por_forma_pagamento = {row['nome']: row['total'] for row in cursor.fetchall()}
        
        return {
            'troco_inicial': troco_inicial,
            'total_entradas': total_entradas,
            'total_saidas': total_saidas,
            'saldo_atual': saldo_atual,
            'por_forma_pagamento': por_forma_pagamento
        }
    
    # ========== HISTÓRICO E RELATÓRIOS ==========
    
    def listar_caixas(self, data_inicio: str = None, data_fim: str = None, 
                      limite: int = None) -> List[Dict]:
        """Lista todos os caixas (abertos e fechados)"""
        cursor = self.conn.cursor()
        
        query = "SELECT * FROM caixa WHERE 1=1"
        params = []
        
        if data_inicio and data_inicio.strip():
            query += " AND DATE(data_abertura) >= DATE(?)"
            params.append(data_inicio.strip())
        
        if data_fim and data_fim.strip():
            query += " AND DATE(data_abertura) <= DATE(?)"
            params.append(data_fim.strip())
        
        query += " ORDER BY data_abertura DESC"
        
        if limite:
            query += f" LIMIT {int(limite)}"
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def obter_relatorio_fechamento(self, caixa_id: int) -> Dict:
        """Obtém relatório completo de um fechamento"""
        cursor = self.conn.cursor()
        
        # Dados do caixa
        cursor.execute("SELECT * FROM caixa WHERE id = ?", (caixa_id,))
        caixa = dict(cursor.fetchone())
        
        # Lançamentos
        lancamentos = self.listar_lancamentos(caixa_id=caixa_id)
        
        # Totais por categoria
        cursor.execute("""
            SELECT categoria, tipo, SUM(valor) as total
            FROM lancamentos
            WHERE caixa_id = ? AND cancelado = 0
            GROUP BY categoria, tipo
        """, (caixa_id,))
        por_categoria = [dict(row) for row in cursor.fetchall()]
        
        # Totais por forma de pagamento
        cursor.execute("""
            SELECT fp.nome, SUM(l.valor) as total
            FROM lancamentos l
            JOIN formas_pagamento fp ON l.forma_pagamento_id = fp.id
            WHERE l.caixa_id = ? AND l.tipo = 'Entrada' AND l.cancelado = 0
            GROUP BY fp.nome
        """, (caixa_id,))
        por_forma = [dict(row) for row in cursor.fetchall()]
        
        return {
            'caixa': caixa,
            'lancamentos': lancamentos,
            'por_categoria': por_categoria,
            'por_forma_pagamento': por_forma
        }
    
    # ========== LOGS ==========
    
    def registrar_log(self, acao: str, detalhes: str = "", operador: str = ""):
        """Registra uma ação no log"""
        cursor = self.conn.cursor()
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT INTO logs (acao, detalhes, operador, data_hora)
            VALUES (?, ?, ?, ?)
        """, (acao, detalhes, operador, data_hora))
        self.conn.commit()
    
    def listar_logs(self, limite: int = 100) -> List[Dict]:
        """Lista os logs mais recentes"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM logs 
            ORDER BY data_hora DESC 
            LIMIT ?
        """, (limite,))
        return [dict(row) for row in cursor.fetchall()]
