#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tela de histórico e relatórios
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from database import Database
from utils import (formatar_moeda, formatar_data, formatar_data_curta, 
                   exportar_para_csv, fazer_backup, exportar_para_pdf,
                   exportar_relatorio_caixa_pdf)
from tema import (
    COR_PRIMARIA, COR_PRIMARIA_CLARA, COR_SUCESSO, COR_SECUNDARIA,
    COR_PERIGO, COR_ALERTA, COR_FUNDO, COR_TEXTO_CLARO
)

class HistoricoView(tk.Frame):
    """Tela de histórico e relatórios"""
    
    def __init__(self, parent, db: Database, voltar_callback):
        super().__init__(parent)
        self.db = db
        self.voltar_callback = voltar_callback
        
        self.configure(bg=COR_FUNDO)
        self.criar_widgets()
        self.carregar_dados()
    
    def criar_widgets(self):
        """Cria os widgets da interface"""
        # Título com cores da loja MF
        titulo_frame = tk.Frame(self, bg=COR_PRIMARIA, height=60)
        titulo_frame.pack(fill=tk.X)
        titulo_frame.pack_propagate(False)
        
        tk.Label(
            titulo_frame,
            text="📊 Histórico e Relatórios",
            font=("Arial", 18, "bold"),
            bg=COR_PRIMARIA,
            fg=COR_TEXTO_CLARO
        ).pack(pady=15)
        
        # Container principal
        container = tk.Frame(self, bg=COR_FUNDO)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame de filtros
        filtros_frame = tk.LabelFrame(
            container,
            text="Filtros",
            font=("Arial", 11, "bold"),
            bg="white",
            padx=15,
            pady=15
        )
        filtros_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Linha 1 - Período
        periodo_frame = tk.Frame(filtros_frame, bg="white")
        periodo_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(periodo_frame, text="Período:", font=("Arial", 10), bg="white").pack(side=tk.LEFT, padx=(0, 10))
        
        # Data início
        tk.Label(periodo_frame, text="De:", font=("Arial", 9), bg="white").pack(side=tk.LEFT, padx=5)
        self.entry_data_inicio = tk.Entry(periodo_frame, font=("Arial", 9), width=12)
        self.entry_data_inicio.pack(side=tk.LEFT, padx=(0, 10))
        
        # Data fim
        tk.Label(periodo_frame, text="Até:", font=("Arial", 9), bg="white").pack(side=tk.LEFT, padx=5)
        self.entry_data_fim = tk.Entry(periodo_frame, font=("Arial", 9), width=12)
        self.entry_data_fim.pack(side=tk.LEFT, padx=(0, 10))
        
        # Preencher com período padrão (últimos 30 dias)
        hoje = datetime.now()
        inicio_padrao = hoje - timedelta(days=30)
        self.entry_data_inicio.insert(0, inicio_padrao.strftime("%d/%m/%Y"))
        self.entry_data_fim.insert(0, hoje.strftime("%d/%m/%Y"))
        
        # Botões de período rápido
        tk.Button(
            periodo_frame,
            text="Hoje",
            font=("Arial", 8),
            bg=COR_PRIMARIA,
            fg=COR_TEXTO_CLARO,
            command=lambda: self.set_periodo(0),
            cursor="hand2",
            padx=10,
            pady=3
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            periodo_frame,
            text="Ontem",
            font=("Arial", 8),
            bg=COR_PRIMARIA,
            fg=COR_TEXTO_CLARO,
            command=lambda: self.set_periodo(-1),
            cursor="hand2",
            padx=10,
            pady=3
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            periodo_frame,
            text="7 dias",
            font=("Arial", 8),
            bg=COR_PRIMARIA,
            fg=COR_TEXTO_CLARO,
            command=lambda: self.set_periodo(7),
            cursor="hand2",
            padx=10,
            pady=3
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            periodo_frame,
            text="30 dias",
            font=("Arial", 8),
            bg=COR_PRIMARIA,
            fg=COR_TEXTO_CLARO,
            command=lambda: self.set_periodo(30),
            cursor="hand2",
            padx=10,
            pady=3
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            periodo_frame,
            text="Tudo",
            font=("Arial", 8),
            bg=COR_SECUNDARIA,
            fg=COR_TEXTO_CLARO,
            command=self.limpar_filtros,
            cursor="hand2",
            padx=10,
            pady=3
        ).pack(side=tk.LEFT, padx=2)
        
        # Linha 2 - Outros filtros
        outros_frame = tk.Frame(filtros_frame, bg="white")
        outros_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(outros_frame, text="Tipo:", font=("Arial", 10), bg="white").pack(side=tk.LEFT, padx=(0, 5))
        self.var_tipo = tk.StringVar(value="Todos")
        ttk.Combobox(
            outros_frame, 
            textvariable=self.var_tipo, 
            values=["Todos", "Entrada", "Saída"],
            font=("Arial", 9),
            state="readonly",
            width=12
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Label(outros_frame, text="Categoria:", font=("Arial", 10), bg="white").pack(side=tk.LEFT, padx=5)
        self.var_categoria = tk.StringVar(value="Todas")
        ttk.Combobox(
            outros_frame,
            textvariable=self.var_categoria,
            values=["Todas", "Venda", "Sangria", "Suprimento", "Despesa", "Outros"],
            font=("Arial", 9),
            state="readonly",
            width=15
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        # Botão filtrar
        tk.Button(
            outros_frame,
            text="🔍 Filtrar",
            font=("Arial", 10, "bold"),
            bg=COR_SUCESSO,
            fg=COR_TEXTO_CLARO,
            command=self.carregar_dados,
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=10)
        
        # Abas
        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba de lançamentos
        self.criar_aba_lancamentos()
        
        # Aba de caixas
        self.criar_aba_caixas()
        
        # Frame de botões inferiores
        botoes_frame = tk.Frame(container, bg="#f0f0f0")
        botoes_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(
            botoes_frame,
            text="📥 Exportar CSV",
            font=("Arial", 10),
            bg="#3498db",
            fg="white",
            command=self.exportar_csv,
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            botoes_frame,
            text="� Exportar PDF",
            font=("Arial", 10),
            bg="#e74c3c",
            fg="white",
            command=self.exportar_pdf,
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            botoes_frame,
            text="�💾 Fazer Backup",
            font=("Arial", 10),
            bg="#f39c12",
            fg="white",
            command=lambda: fazer_backup(self.db.db_path),
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            botoes_frame,
            text="← Voltar",
            font=("Arial", 10),
            bg="#95a5a6",
            fg="white",
            command=self.voltar_callback,
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=10
        ).pack(side=tk.RIGHT, padx=5)
    
    def criar_aba_lancamentos(self):
        """Cria a aba de lançamentos"""
        frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(frame, text="  Lançamentos  ")
        
        # Treeview
        colunas = ("Data/Hora", "Tipo", "Categoria", "Forma Pgto", "Valor", "Observação")
        self.tree_lancamentos = ttk.Treeview(
            frame,
            columns=colunas,
            show="headings",
            height=15
        )
        
        # Configurar colunas
        self.tree_lancamentos.heading("Data/Hora", text="Data/Hora")
        self.tree_lancamentos.heading("Tipo", text="Tipo")
        self.tree_lancamentos.heading("Categoria", text="Categoria")
        self.tree_lancamentos.heading("Forma Pgto", text="Forma Pgto")
        self.tree_lancamentos.heading("Valor", text="Valor")
        self.tree_lancamentos.heading("Observação", text="Observação")
        
        self.tree_lancamentos.column("Data/Hora", width=140)
        self.tree_lancamentos.column("Tipo", width=80, anchor=tk.CENTER)
        self.tree_lancamentos.column("Categoria", width=100)
        self.tree_lancamentos.column("Forma Pgto", width=100)
        self.tree_lancamentos.column("Valor", width=100, anchor=tk.E)
        self.tree_lancamentos.column("Observação", width=200)
        
        # Scrollbars
        scrollbar_y = tk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree_lancamentos.yview)
        scrollbar_x = tk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.tree_lancamentos.xview)
        self.tree_lancamentos.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Grid
        self.tree_lancamentos.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scrollbar_y.grid(row=0, column=1, sticky="ns", pady=10)
        scrollbar_x.grid(row=1, column=0, sticky="ew", padx=10)
        
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Resumo
        resumo_frame = tk.Frame(frame, bg="#ecf0f1", relief=tk.RIDGE, borderwidth=2)
        resumo_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
        
        self.label_resumo_lancamentos = tk.Label(
            resumo_frame,
            text="Total: 0 lançamentos | Entradas: R$ 0,00 | Saídas: R$ 0,00",
            font=("Arial", 10, "bold"),
            bg="#ecf0f1",
            pady=10
        )
        self.label_resumo_lancamentos.pack()
    
    def criar_aba_caixas(self):
        """Cria a aba de caixas"""
        frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(frame, text="  Caixas  ")
        
        # Treeview
        colunas = ("Data Abertura", "Operador", "Troco Inicial", "Entradas", "Saídas", 
                  "Saldo Final", "Status")
        self.tree_caixas = ttk.Treeview(
            frame,
            columns=colunas,
            show="headings",
            height=15
        )
        
        # Configurar colunas
        for col in colunas:
            self.tree_caixas.heading(col, text=col)
        
        self.tree_caixas.column("Data Abertura", width=140)
        self.tree_caixas.column("Operador", width=120)
        self.tree_caixas.column("Troco Inicial", width=100, anchor=tk.E)
        self.tree_caixas.column("Entradas", width=100, anchor=tk.E)
        self.tree_caixas.column("Saídas", width=100, anchor=tk.E)
        self.tree_caixas.column("Saldo Final", width=100, anchor=tk.E)
        self.tree_caixas.column("Status", width=80, anchor=tk.CENTER)
        
        # Scrollbars
        scrollbar_y = tk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree_caixas.yview)
        scrollbar_x = tk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.tree_caixas.xview)
        self.tree_caixas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Grid
        self.tree_caixas.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        scrollbar_y.grid(row=0, column=1, sticky="ns", pady=10)
        scrollbar_x.grid(row=1, column=0, sticky="ew", padx=10)
        
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        # Botão ver detalhes
        tk.Button(
            frame,
            text="📄 Ver Detalhes do Caixa",
            font=("Arial", 10),
            bg="#3498db",
            fg="white",
            command=self.ver_detalhes_caixa,
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=10
        ).grid(row=2, column=0, columnspan=2, pady=(0, 10))
    
    def set_periodo(self, dias: int):
        """Define o período de busca"""
        hoje = datetime.now()
        if dias == 0:
            # Hoje
            inicio = hoje
            fim = hoje
        elif dias == -1:
            # Ontem
            ontem = hoje - timedelta(days=1)
            inicio = ontem
            fim = ontem
        else:
            # Últimos N dias
            inicio = hoje - timedelta(days=dias-1)
            fim = hoje
        
        self.entry_data_inicio.delete(0, tk.END)
        self.entry_data_inicio.insert(0, inicio.strftime("%d/%m/%Y"))
        
        self.entry_data_fim.delete(0, tk.END)
        self.entry_data_fim.insert(0, fim.strftime("%d/%m/%Y"))
        
        # Resetar filtros de tipo e categoria
        self.var_tipo.set("Todos")
        self.var_categoria.set("Todas")
        
        self.carregar_dados()
    
    def limpar_filtros(self):
        """Limpa todos os filtros para mostrar todos os registros"""
        self.entry_data_inicio.delete(0, tk.END)
        self.entry_data_fim.delete(0, tk.END)
        self.var_tipo.set("Todos")
        self.var_categoria.set("Todas")
        self.carregar_dados()
    
    def converter_data_para_iso(self, data_str: str) -> str:
        """Converte data de DD/MM/YYYY para YYYY-MM-DD"""
        if not data_str:
            return None
        try:
            # Tenta converter de DD/MM/YYYY
            if '/' in data_str:
                partes = data_str.split('/')
                if len(partes) == 3:
                    return f"{partes[2]}-{partes[1]}-{partes[0]}"
            # Se já estiver em formato ISO, retorna como está
            return data_str
        except:
            return data_str
    
    def carregar_dados(self):
        """Carrega os dados com os filtros aplicados"""
        try:
            # Obter filtros - tratar datas vazias como None (sem filtro)
            data_inicio_raw = self.entry_data_inicio.get().strip() or None
            data_fim_raw = self.entry_data_fim.get().strip() or None
            
            # Converter para formato ISO (YYYY-MM-DD) para o banco
            data_inicio = self.converter_data_para_iso(data_inicio_raw)
            data_fim = self.converter_data_para_iso(data_fim_raw)
            
            tipo = self.var_tipo.get() if self.var_tipo.get() != "Todos" else None
            categoria = self.var_categoria.get() if self.var_categoria.get() != "Todas" else None
            
            # Carregar lançamentos
            self.carregar_lancamentos(data_inicio, data_fim, tipo, categoria)
            
            # Carregar caixas
            self.carregar_caixas(data_inicio, data_fim)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados: {str(e)}")
    
    def carregar_lancamentos(self, data_inicio, data_fim, tipo, categoria):
        """Carrega a lista de lançamentos"""
        # Limpar árvore
        for item in self.tree_lancamentos.get_children():
            self.tree_lancamentos.delete(item)
        
        try:
            # Buscar lançamentos
            lancamentos = self.db.listar_lancamentos(
                data_inicio=data_inicio,
                data_fim=data_fim,
                tipo=tipo,
                categoria=categoria
            )
            
            total_entradas = 0
            total_saidas = 0
            
            if not lancamentos:
                # Mostrar mensagem quando não há lançamentos
                periodo_info = ""
                if data_inicio and data_fim:
                    periodo_info = f" no período de {data_inicio} a {data_fim}"
                elif data_inicio:
                    periodo_info = f" a partir de {data_inicio}"
                elif data_fim:
                    periodo_info = f" até {data_fim}"
                
                self.label_resumo_lancamentos.config(
                    text=f"Nenhum lançamento encontrado{periodo_info}. Tente expandir o período ou clique em 'Tudo'."
                )
                return
            
            for lanc in lancamentos:
                data_hora = formatar_data(lanc['data_hora']) if lanc.get('data_hora') else ""
                tipo_lanc = lanc['tipo']
                cat = lanc['categoria']
                forma = lanc.get('forma_pagamento_nome', '') or ''
                valor = lanc['valor'] or 0
                obs = lanc.get('observacao', '') or ''
                
                # Calcular totais
                if tipo_lanc == "Entrada":
                    total_entradas += valor
                else:
                    total_saidas += valor
                
                # Inserir
                tag = "entrada" if tipo_lanc == "Entrada" else "saida"
                self.tree_lancamentos.insert(
                    "", tk.END,
                    values=(data_hora, tipo_lanc, cat, forma, formatar_moeda(valor), obs),
                    tags=(tag,)
                )
            
            # Configurar cores
            self.tree_lancamentos.tag_configure("entrada", foreground="#27ae60")
            self.tree_lancamentos.tag_configure("saida", foreground="#e74c3c")
            
            # Atualizar resumo
            self.label_resumo_lancamentos.config(
                text=f"Total: {len(lancamentos)} lançamentos | "
                     f"Entradas: {formatar_moeda(total_entradas)} | "
                     f"Saídas: {formatar_moeda(total_saidas)}"
            )
        except Exception as e:
            self.label_resumo_lancamentos.config(
                text=f"Erro ao carregar lançamentos: {str(e)}"
            )
    
    def carregar_caixas(self, data_inicio, data_fim):
        """Carrega a lista de caixas"""
        # Limpar árvore
        for item in self.tree_caixas.get_children():
            self.tree_caixas.delete(item)
        
        try:
            # Buscar caixas
            caixas = self.db.listar_caixas(data_inicio, data_fim)
            
            if not caixas:
                # Inserir linha informativa quando não há caixas
                self.tree_caixas.insert(
                    "", tk.END,
                    values=("Nenhum caixa encontrado", "-", "-", "-", "-", "-", "-"),
                    tags=("vazio",)
                )
                self.tree_caixas.tag_configure("vazio", foreground="#999")
                return
            
            for caixa in caixas:
                data_abertura = formatar_data(caixa['data_abertura']) if caixa.get('data_abertura') else ""
                operador = caixa.get('operador', '') or 'N/A'
                troco_inicial = formatar_moeda(caixa.get('troco_inicial', 0) or 0)
                entradas = formatar_moeda(caixa.get('total_entradas', 0) or 0)
                saidas = formatar_moeda(caixa.get('total_saidas', 0) or 0)
                saldo = formatar_moeda(caixa.get('saldo_final', 0) or 0)
                status = "Aberto" if caixa.get('status') == 'aberto' else "Fechado"
                
                # Inserir
                tag = "aberto" if caixa.get('status') == 'aberto' else "fechado"
                self.tree_caixas.insert(
                    "", tk.END,
                    values=(data_abertura, operador, troco_inicial, entradas, saidas, saldo, status),
                    tags=(tag,)
                )
            
            # Configurar cores
            self.tree_caixas.tag_configure("aberto", foreground="#27ae60", font=("Arial", 9, "bold"))
            self.tree_caixas.tag_configure("fechado", foreground="#555")
        except Exception as e:
            self.tree_caixas.insert(
                "", tk.END,
                values=(f"Erro: {str(e)}", "-", "-", "-", "-", "-", "-"),
                tags=("erro",)
            )
            self.tree_caixas.tag_configure("erro", foreground="#e74c3c")
    
    def ver_detalhes_caixa(self):
        """Mostra os detalhes de um caixa selecionado"""
        selecao = self.tree_caixas.selection()
        if not selecao:
            messagebox.showwarning("Atenção", "Selecione um caixa para ver os detalhes!")
            return
        
        # Pegar o índice
        item = selecao[0]
        indice = self.tree_caixas.index(item)
        
        # Buscar caixas novamente
        data_inicio = self.entry_data_inicio.get().strip()
        data_fim = self.entry_data_fim.get().strip()
        caixas = self.db.listar_caixas(data_inicio, data_fim)
        
        if indice < len(caixas):
            caixa = caixas[indice]
            self.mostrar_detalhes_caixa(caixa['id'])
    
    def mostrar_detalhes_caixa(self, caixa_id: int):
        """Mostra uma janela com os detalhes do caixa"""
        from utils import gerar_relatorio_texto, salvar_relatorio_texto
        
        # Buscar relatório completo
        dados = self.db.obter_relatorio_fechamento(caixa_id)
        relatorio = gerar_relatorio_texto(dados)
        
        # Criar janela
        dialog = tk.Toplevel(self)
        dialog.title("Detalhes do Caixa")
        dialog.geometry("800x600")
        dialog.transient(self)
        
        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        frame = tk.Frame(dialog, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Texto do relatório
        text_widget = tk.Text(
            frame,
            font=("Courier", 10),
            wrap=tk.WORD,
            bg="#f9f9f9"
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(text_widget, command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        text_widget.insert("1.0", relatorio)
        text_widget.config(state=tk.DISABLED)
        
        # Botões
        botoes_frame = tk.Frame(frame)
        botoes_frame.pack(pady=(10, 0))
        
        tk.Button(
            botoes_frame,
            text="💾 Salvar TXT",
            font=("Arial", 10),
            bg="#27ae60",
            fg="white",
            command=lambda: salvar_relatorio_texto(relatorio),
            cursor="hand2",
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            botoes_frame,
            text="📄 Salvar PDF",
            font=("Arial", 10),
            bg="#e74c3c",
            fg="white",
            command=lambda: exportar_relatorio_caixa_pdf(dados),
            cursor="hand2",
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            botoes_frame,
            text="Fechar",
            font=("Arial", 10),
            bg="#95a5a6",
            fg="white",
            command=dialog.destroy,
            cursor="hand2",
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
    
    def exportar_csv(self):
        """Exporta os dados atuais para CSV"""
        aba_atual = self.notebook.index(self.notebook.select())
        
        if aba_atual == 0:  # Lançamentos
            # Buscar lançamentos
            data_inicio = self.entry_data_inicio.get().strip()
            data_fim = self.entry_data_fim.get().strip()
            tipo = self.var_tipo.get() if self.var_tipo.get() != "Todos" else None
            categoria = self.var_categoria.get() if self.var_categoria.get() != "Todas" else None
            
            lancamentos = self.db.listar_lancamentos(
                data_inicio=data_inicio,
                data_fim=data_fim,
                tipo=tipo,
                categoria=categoria
            )
            
            if not lancamentos:
                messagebox.showwarning("Atenção", "Não há lançamentos para exportar!")
                return
            
            # Formatar dados
            dados_exportar = []
            for lanc in lancamentos:
                dados_exportar.append({
                    'Data/Hora': formatar_data(lanc['data_hora']),
                    'Tipo': lanc['tipo'],
                    'Categoria': lanc['categoria'],
                    'Forma Pagamento': lanc.get('forma_pagamento_nome', ''),
                    'Valor': lanc['valor'],
                    'Observacao': lanc.get('observacao', '')
                })
            
            colunas = ['Data/Hora', 'Tipo', 'Categoria', 'Forma Pagamento', 'Valor', 'Observacao']
            exportar_para_csv(dados_exportar, colunas)
            
        else:  # Caixas
            data_inicio = self.entry_data_inicio.get().strip()
            data_fim = self.entry_data_fim.get().strip()
            caixas = self.db.listar_caixas(data_inicio, data_fim)
            
            if not caixas:
                messagebox.showwarning("Atenção", "Não há caixas para exportar!")
                return
            
            # Formatar dados
            dados_exportar = []
            for caixa in caixas:
                dados_exportar.append({
                    'Data Abertura': formatar_data(caixa['data_abertura']),
                    'Data Fechamento': formatar_data(caixa.get('data_fechamento', '')),
                    'Operador': caixa.get('operador', ''),
                    'Troco Inicial': caixa['troco_inicial'],
                    'Total Entradas': caixa.get('total_entradas', 0),
                    'Total Saidas': caixa.get('total_saidas', 0),
                    'Saldo Final': caixa.get('saldo_final', 0),
                    'Valor Contado': caixa.get('valor_contado', ''),
                    'Diferenca': caixa.get('diferenca', ''),
                    'Status': caixa['status']
                })
            
            colunas = ['Data Abertura', 'Data Fechamento', 'Operador', 'Troco Inicial',
                      'Total Entradas', 'Total Saidas', 'Saldo Final', 'Valor Contado',
                      'Diferenca', 'Status']
            exportar_para_csv(dados_exportar, colunas)
    
    def exportar_pdf(self):
        """Exporta os dados atuais para PDF"""
        aba_atual = self.notebook.index(self.notebook.select())
        
        if aba_atual == 0:  # Lançamentos
            # Buscar lançamentos
            data_inicio = self.entry_data_inicio.get().strip()
            data_fim = self.entry_data_fim.get().strip()
            tipo = self.var_tipo.get() if self.var_tipo.get() != "Todos" else None
            categoria = self.var_categoria.get() if self.var_categoria.get() != "Todas" else None
            
            lancamentos = self.db.listar_lancamentos(
                data_inicio=data_inicio,
                data_fim=data_fim,
                tipo=tipo,
                categoria=categoria
            )
            
            if not lancamentos:
                messagebox.showwarning("Atenção", "Não há lançamentos para exportar!")
                return
            
            # Calcular totais para o resumo
            total_entradas = sum(l['valor'] for l in lancamentos if l['tipo'] == 'Entrada')
            total_saidas = sum(l['valor'] for l in lancamentos if l['tipo'] == 'Saída')
            
            # Formatar dados
            dados_exportar = []
            for lanc in lancamentos:
                dados_exportar.append({
                    'Data/Hora': formatar_data(lanc['data_hora']),
                    'Tipo': lanc['tipo'],
                    'Categoria': lanc['categoria'],
                    'Forma Pgto': lanc.get('forma_pagamento_nome', '') or '',
                    'Valor': formatar_moeda(lanc['valor']),
                    'Obs': (lanc.get('observacao', '') or '')[:20]
                })
            
            colunas = ['Data/Hora', 'Tipo', 'Categoria', 'Forma Pgto', 'Valor', 'Obs']
            
            # Preparar título e resumo
            titulo = "Relatório de Lançamentos"
            if data_inicio and data_fim:
                titulo += f" ({data_inicio} a {data_fim})"
            
            resumo = {
                'Total': f'{len(lancamentos)} lançamentos',
                'Entradas': formatar_moeda(total_entradas),
                'Saídas': formatar_moeda(total_saidas)
            }
            
            exportar_para_pdf(dados_exportar, colunas, titulo, resumo=resumo)
            
        else:  # Caixas
            data_inicio = self.entry_data_inicio.get().strip()
            data_fim = self.entry_data_fim.get().strip()
            caixas = self.db.listar_caixas(data_inicio, data_fim)
            
            if not caixas:
                messagebox.showwarning("Atenção", "Não há caixas para exportar!")
                return
            
            # Formatar dados
            dados_exportar = []
            for caixa in caixas:
                dados_exportar.append({
                    'Data Abertura': formatar_data(caixa['data_abertura']),
                    'Operador': caixa.get('operador', '') or 'N/A',
                    'Troco Inicial': formatar_moeda(caixa.get('troco_inicial', 0) or 0),
                    'Entradas': formatar_moeda(caixa.get('total_entradas', 0) or 0),
                    'Saídas': formatar_moeda(caixa.get('total_saidas', 0) or 0),
                    'Saldo Final': formatar_moeda(caixa.get('saldo_final', 0) or 0),
                    'Status': 'Aberto' if caixa.get('status') == 'aberto' else 'Fechado'
                })
            
            colunas = ['Data Abertura', 'Operador', 'Troco Inicial', 'Entradas', 
                      'Saídas', 'Saldo Final', 'Status']
            
            titulo = "Relatório de Caixas"
            if data_inicio and data_fim:
                titulo += f" ({data_inicio} a {data_fim})"
            
            resumo = {'Total': f'{len(caixas)} caixas'}
            
            exportar_para_pdf(dados_exportar, colunas, titulo, resumo=resumo)
