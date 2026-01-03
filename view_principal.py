#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tela principal com lançamentos e painel de controle
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import threading
from database import Database
from utils import formatar_moeda, validar_valor, calcular_troco, formatar_data, fazer_backup
from tema import (
    COR_PRIMARIA, COR_PRIMARIA_ESCURA, COR_PRIMARIA_CLARA,
    COR_SECUNDARIA, COR_SUCESSO, COR_PERIGO, COR_ALERTA,
    COR_FUNDO, COR_TEXTO_CLARO, COR_TECLADO_NUMERO,
    obter_logo_perfil, NOME_SISTEMA
)
try:
    from PIL import Image, ImageTk
    PIL_DISPONIVEL = True
except ImportError:
    PIL_DISPONIVEL = False


class TecladoNumerico(tk.Frame):
    """Teclado numérico moderno e reutilizável"""
    
    def __init__(self, parent, entry_alvo, bg="white"):
        super().__init__(parent, bg=bg)
        self.entry_alvo = entry_alvo
        self.criar_teclado()
    
    def criar_teclado(self):
        """Cria o teclado numérico com visual moderno"""
        # Título
        tk.Label(
            self, 
            text="⌨️ Teclado", 
            font=("Arial", 9, "bold"), 
            bg=self.cget("bg"), 
            fg="#555"
        ).pack(pady=(0, 5))
        
        teclado_frame = tk.Frame(self, bg=self.cget("bg"))
        teclado_frame.pack()
        
        # Botões do teclado - cores da loja MF
        teclas = [
            [("7", COR_TECLADO_NUMERO), ("8", COR_TECLADO_NUMERO), ("9", COR_TECLADO_NUMERO)],
            [("4", COR_TECLADO_NUMERO), ("5", COR_TECLADO_NUMERO), ("6", COR_TECLADO_NUMERO)],
            [("1", COR_TECLADO_NUMERO), ("2", COR_TECLADO_NUMERO), ("3", COR_TECLADO_NUMERO)],
            [("0", COR_TECLADO_NUMERO), (",", COR_SECUNDARIA), ("⌫", COR_PERIGO)],
        ]
        
        for linha in teclas:
            linha_frame = tk.Frame(teclado_frame, bg=self.cget("bg"))
            linha_frame.pack(pady=2)
            for texto, cor in linha:
                self._criar_botao_moderno(linha_frame, texto, cor)
        
        # Linha de atalhos
        atalhos_frame = tk.Frame(teclado_frame, bg=self.cget("bg"))
        atalhos_frame.pack(pady=(8, 0))
        
        self._criar_botao_moderno(atalhos_frame, ",00", COR_SUCESSO, largura=6)
        self._criar_botao_moderno(atalhos_frame, ",50", COR_SUCESSO, largura=6)
        self._criar_botao_moderno(atalhos_frame, "C", COR_PERIGO, largura=4)
    
    def _criar_botao_moderno(self, parent, texto, cor, largura=4):
        """Cria um botão com visual moderno"""
        btn = tk.Button(
            parent,
            text=texto,
            font=("Arial", 14, "bold"),
            bg=cor,
            fg="white",
            activebackground=self._escurecer_cor(cor),
            activeforeground="white",
            width=largura,
            height=1,
            bd=0,
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda t=texto: self._acao_tecla(t)
        )
        btn.pack(side=tk.LEFT, padx=3, pady=2)
        
        # Efeito hover
        btn.bind("<Enter>", lambda e, b=btn, c=cor: b.config(bg=self._escurecer_cor(c)))
        btn.bind("<Leave>", lambda e, b=btn, c=cor: b.config(bg=c))
        
        return btn
    
    def _escurecer_cor(self, cor_hex):
        """Escurece uma cor hexadecimal"""
        cor = cor_hex.lstrip('#')
        r, g, b = tuple(int(cor[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, int(r * 0.8))
        g = max(0, int(g * 0.8))
        b = max(0, int(b * 0.8))
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def _acao_tecla(self, tecla):
        """Executa a ação da tecla pressionada"""
        if tecla == "⌫":
            atual = self.entry_alvo.get()
            self.entry_alvo.delete(0, tk.END)
            self.entry_alvo.insert(0, atual[:-1])
        elif tecla == "C":
            self.entry_alvo.delete(0, tk.END)
        elif tecla == ",00":
            self.entry_alvo.insert(tk.END, ",00")
        elif tecla == ",50":
            self.entry_alvo.insert(tk.END, ",50")
        else:
            self.entry_alvo.insert(tk.END, tecla)
        
        self.entry_alvo.focus()
        # Disparar evento de KeyRelease para atualizar cálculos
        self.entry_alvo.event_generate('<KeyRelease>')


class PrincipalView(tk.Frame):
    """Tela principal de lançamentos"""
    
    def __init__(self, parent, db: Database, caixa_id: int, fechar_caixa_callback, 
                 historico_callback, config_callback):
        super().__init__(parent)
        self.db = db
        self.caixa_id = caixa_id
        self.fechar_caixa_callback = fechar_caixa_callback
        self.historico_callback = historico_callback
        self.config_callback = config_callback
        
        self.configure(bg=COR_FUNDO)
        self.logo_img = None  # Referência para a imagem
        self.criar_widgets()
        self.atualizar_painel()
    
    def criar_widgets(self):
        """Cria os widgets da interface"""
        # Barra superior com logo e botões - cores da loja MF
        top_frame = tk.Frame(self, bg=COR_PRIMARIA, height=70)
        top_frame.pack(fill=tk.X)
        top_frame.pack_propagate(False)
        
        # Frame esquerdo para logo + título
        left_header = tk.Frame(top_frame, bg=COR_PRIMARIA)
        left_header.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Carregar logo (se PIL disponível)
        if PIL_DISPONIVEL:
            try:
                logo_path = obter_logo_perfil()
                img = Image.open(logo_path)
                img = img.resize((50, 50), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(img)
                logo_label = tk.Label(left_header, image=self.logo_img, bg=COR_PRIMARIA)
                logo_label.pack(side=tk.LEFT, padx=(0, 10))
            except Exception as e:
                pass
        
        tk.Label(
            left_header,
            text="💰 Caixa Aberto",
            font=("Arial", 18, "bold"),
            bg=COR_PRIMARIA,
            fg=COR_TEXTO_CLARO
        ).pack(side=tk.LEFT)
        
        # Botões da barra superior
        btn_frame = tk.Frame(top_frame, bg=COR_PRIMARIA)
        btn_frame.pack(side=tk.RIGHT, padx=20)
        
        tk.Button(
            btn_frame,
            text="� Backup",
            font=("Arial", 10),
            bg=COR_ALERTA,
            fg=COR_TEXTO_CLARO,
            command=self.fazer_backup,
            cursor="hand2",
            relief=tk.FLAT,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="�📊 Histórico",
            font=("Arial", 10),
            bg=COR_PRIMARIA_CLARA,
            fg=COR_TEXTO_CLARO,
            command=self.historico_callback,
            cursor="hand2",
            relief=tk.FLAT,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="⚙️ Config",
            font=("Arial", 10),
            bg=COR_PRIMARIA_CLARA,
            fg=COR_TEXTO_CLARO,
            command=self.config_callback,
            cursor="hand2",
            relief=tk.FLAT,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="🔒 Fechar Caixa",
            font=("Arial", 10, "bold"),
            bg=COR_SECUNDARIA,
            fg=COR_TEXTO_CLARO,
            command=self.fechar_caixa_callback,
            cursor="hand2",
            relief=tk.FLAT,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        # Container principal dividido em duas colunas
        main_container = tk.Frame(self, bg=COR_FUNDO)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Coluna esquerda - Painel e ações rápidas
        left_column = tk.Frame(main_container, bg=COR_FUNDO)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Painel de resumo
        self.criar_painel_resumo(left_column)
        
        # Ações rápidas
        self.criar_acoes_rapidas(left_column)
        
        # Coluna direita - Lançamentos
        right_column = tk.Frame(main_container, bg=COR_FUNDO)
        right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Lista de lançamentos
        self.criar_lista_lancamentos(right_column)
    
    def criar_painel_resumo(self, parent):
        """Cria o painel de resumo do caixa"""
        painel_frame = tk.LabelFrame(
            parent,
            text="Resumo do Caixa",
            font=("Arial", 12, "bold"),
            bg="white",
            padx=20,
            pady=15
        )
        painel_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Saldo atual (destaque)
        self.label_saldo_atual = tk.Label(
            painel_frame,
            text="R$ 0,00",
            font=("Arial", 32, "bold"),
            bg="white",
            fg="#27ae60"
        )
        self.label_saldo_atual.pack(pady=(0, 5))
        
        tk.Label(
            painel_frame,
            text="Saldo Atual",
            font=("Arial", 10),
            bg="white",
            fg="#777"
        ).pack()
        
        ttk.Separator(painel_frame, orient='horizontal').pack(fill=tk.X, pady=15)
        
        # Detalhes
        detalhes_frame = tk.Frame(painel_frame, bg="white")
        detalhes_frame.pack(fill=tk.X)
        
        self.label_troco_inicial = self._criar_item_resumo(
            detalhes_frame, "Troco Inicial:", "R$ 0,00", 0
        )
        self.label_total_entradas = self._criar_item_resumo(
            detalhes_frame, "Entradas:", "R$ 0,00", 1, "#27ae60"
        )
        self.label_total_saidas = self._criar_item_resumo(
            detalhes_frame, "Saídas:", "R$ 0,00", 2, "#e74c3c"
        )
        
        # Botão atualizar
        tk.Button(
            painel_frame,
            text="🔄 Atualizar",
            font=("Arial", 9),
            bg=COR_PRIMARIA,
            fg=COR_TEXTO_CLARO,
            command=self.atualizar_painel,
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=8
        ).pack(pady=(15, 0))
    
    def _criar_item_resumo(self, parent, texto, valor_inicial, row, cor="#333"):
        """Cria um item do resumo"""
        frame = tk.Frame(parent, bg="white")
        frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            frame,
            text=texto,
            font=("Arial", 10),
            bg="white",
            fg="#555",
            anchor=tk.W
        ).pack(side=tk.LEFT)
        
        label_valor = tk.Label(
            frame,
            text=valor_inicial,
            font=("Arial", 10, "bold"),
            bg="white",
            fg=cor,
            anchor=tk.E
        )
        label_valor.pack(side=tk.RIGHT)
        
        return label_valor
    
    def criar_acoes_rapidas(self, parent):
        """Cria os botões de ações rápidas"""
        acoes_frame = tk.LabelFrame(
            parent,
            text="Ações Rápidas",
            font=("Arial", 12, "bold"),
            bg="white",
            padx=15,
            pady=15
        )
        acoes_frame.pack(fill=tk.BOTH, expand=True)
        
        botoes = [
            ("💵 Venda em Dinheiro", self.venda_dinheiro, COR_SUCESSO),
            ("🏧 Venda PIX/Cartão", self.venda_outros, COR_PRIMARIA),
            ("💸 Sangria", self.sangria, COR_SECUNDARIA),
            ("➕ Suprimento", self.suprimento, COR_ALERTA),
            ("📝 Outro Lançamento", self.outro_lancamento, COR_PRIMARIA_CLARA),
        ]
        
        for texto, comando, cor in botoes:
            btn = tk.Button(
                acoes_frame,
                text=texto,
                font=("Arial", 11, "bold"),
                bg=cor,
                fg="white",
                command=comando,
                cursor="hand2",
                relief=tk.FLAT,
                padx=20,
                pady=15
            )
            btn.pack(fill=tk.X, pady=5)
    
    def criar_lista_lancamentos(self, parent):
        """Cria a lista de lançamentos"""
        lista_frame = tk.LabelFrame(
            parent,
            text="Últimos Lançamentos",
            font=("Arial", 12, "bold"),
            bg="white",
            padx=10,
            pady=10
        )
        lista_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview
        colunas = ("Hora", "Tipo", "Categoria", "Valor")
        self.tree = ttk.Treeview(
            lista_frame,
            columns=colunas,
            show="headings",
            height=15
        )
        
        # Configurar colunas
        self.tree.heading("Hora", text="Hora")
        self.tree.heading("Tipo", text="Tipo")
        self.tree.heading("Categoria", text="Categoria")
        self.tree.heading("Valor", text="Valor")
        
        self.tree.column("Hora", width=80, anchor=tk.CENTER)
        self.tree.column("Tipo", width=80, anchor=tk.CENTER)
        self.tree.column("Categoria", width=120, anchor=tk.W)
        self.tree.column("Valor", width=100, anchor=tk.E)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(lista_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Frame para botões de ação
        acoes_lancamento_frame = tk.Frame(lista_frame, bg="white")
        acoes_lancamento_frame.pack(pady=(10, 0))
        
        # Botão editar lançamento
        tk.Button(
            acoes_lancamento_frame,
            text="✏️ Editar Lançamento",
            font=("Arial", 9),
            bg="#f39c12",
            fg="white",
            command=self.editar_lancamento,
            cursor="hand2",
            relief=tk.FLAT,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        # Botão cancelar lançamento
        tk.Button(
            acoes_lancamento_frame,
            text="❌ Cancelar Lançamento",
            font=("Arial", 9),
            bg="#e74c3c",
            fg="white",
            command=self.cancelar_lancamento,
            cursor="hand2",
            relief=tk.FLAT,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        self.atualizar_lancamentos()
    
    def fazer_backup(self):
        """Faz backup do banco de dados"""
        fazer_backup(self.db.db_path)
    
    def atualizar_painel(self):
        """Atualiza os valores do painel"""
        totais = self.db.obter_totais_caixa_aberto(self.caixa_id)
        
        self.label_saldo_atual.config(text=formatar_moeda(totais['saldo_atual']))
        self.label_troco_inicial.config(text=formatar_moeda(totais['troco_inicial']))
        self.label_total_entradas.config(text=formatar_moeda(totais['total_entradas']))
        self.label_total_saidas.config(text=formatar_moeda(totais['total_saidas']))
        
        self.atualizar_lancamentos()
    
    def atualizar_lancamentos(self):
        """Atualiza a lista de lançamentos"""
        # Limpar árvore
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Buscar lançamentos
        lancamentos = self.db.listar_lancamentos(caixa_id=self.caixa_id)
        
        for lanc in lancamentos[:50]:  # Últimos 50
            hora = formatar_data(lanc['data_hora']).split()[1] if lanc.get('data_hora') else ""
            tipo = lanc['tipo']
            categoria = lanc['categoria']
            valor = formatar_moeda(lanc['valor'])
            
            # Inserir com tag para colorir
            tag = "entrada" if tipo == "Entrada" else "saida"
            self.tree.insert("", 0, values=(hora, tipo, categoria, valor), tags=(tag,))
        
        # Configurar cores
        self.tree.tag_configure("entrada", foreground="#27ae60")
        self.tree.tag_configure("saida", foreground="#e74c3c")
    
    def venda_dinheiro(self):
        """Registra uma venda em dinheiro com cálculo de troco"""
        dialog = tk.Toplevel(self)
        dialog.title("Venda em Dinheiro")
        dialog.geometry("580x520")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        frame = tk.Frame(dialog, bg="white", padx=20, pady=15)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            frame,
            text="💵 Venda em Dinheiro",
            font=("Arial", 16, "bold"),
            bg="white"
        ).pack(pady=(0, 15))
        
        # Container principal
        container = tk.Frame(frame, bg="white")
        container.pack(fill=tk.BOTH, expand=True)
        
        # Lado esquerdo - Campos
        left_frame = tk.Frame(container, bg="white")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        # Valor da compra
        tk.Label(left_frame, text="Valor da Compra (R$):", font=("Arial", 10, "bold"), bg="white").pack(anchor=tk.W)
        entry_valor_compra = tk.Entry(left_frame, font=("Arial", 16, "bold"), width=18, justify=tk.RIGHT)
        entry_valor_compra.pack(fill=tk.X, pady=(5, 12))
        entry_valor_compra.focus()
        
        # Valor recebido
        tk.Label(left_frame, text="Valor Recebido (R$):", font=("Arial", 10, "bold"), bg="white").pack(anchor=tk.W)
        entry_valor_recebido = tk.Entry(left_frame, font=("Arial", 16, "bold"), width=18, justify=tk.RIGHT)
        entry_valor_recebido.pack(fill=tk.X, pady=(5, 12))
        
        # Troco
        troco_frame = tk.Frame(left_frame, bg="#ecf0f1", padx=15, pady=10)
        troco_frame.pack(fill=tk.X, pady=10)
        
        label_troco = tk.Label(
            troco_frame,
            text="Troco: R$ 0,00",
            font=("Arial", 18, "bold"),
            bg="#ecf0f1",
            fg="#27ae60"
        )
        label_troco.pack()
        
        def calcular():
            """Calcula o troco"""
            try:
                valido1, valor_compra = validar_valor(entry_valor_compra.get())
                valido2, valor_recebido = validar_valor(entry_valor_recebido.get())
                
                if valido1 and valido2:
                    troco = calcular_troco(valor_recebido, valor_compra)
                    if troco < 0:
                        label_troco.config(text=f"Falta: {formatar_moeda(abs(troco))}", fg="#e74c3c")
                        troco_frame.config(bg="#fdecea")
                    else:
                        label_troco.config(text=f"Troco: {formatar_moeda(troco)}", fg="#27ae60")
                        troco_frame.config(bg="#e8f8f5")
                    label_troco.config(bg=troco_frame.cget("bg"))
                else:
                    label_troco.config(text="Troco: R$ 0,00", fg="#27ae60", bg="#ecf0f1")
                    troco_frame.config(bg="#ecf0f1")
            except:
                pass
        
        entry_valor_compra.bind('<KeyRelease>', lambda e: calcular())
        entry_valor_recebido.bind('<KeyRelease>', lambda e: calcular())
        
        # Observação
        tk.Label(left_frame, text="Observação (opcional):", font=("Arial", 10), bg="white").pack(anchor=tk.W, pady=(10, 5))
        entry_obs = tk.Entry(left_frame, font=("Arial", 10), width=20)
        entry_obs.pack(fill=tk.X)
        
        # Lado direito - Teclado numérico
        right_frame = tk.Frame(container, bg="white")
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Variável para controlar qual campo está ativo
        entry_ativo = [entry_valor_compra]  # Lista para poder modificar dentro das funções
        
        def focar_compra():
            entry_ativo[0] = entry_valor_compra
            entry_valor_compra.focus()
            btn_compra.config(bg="#2c3e50", relief=tk.SUNKEN)
            btn_recebido.config(bg="#7f8c8d", relief=tk.RAISED)
        
        def focar_recebido():
            entry_ativo[0] = entry_valor_recebido
            entry_valor_recebido.focus()
            btn_recebido.config(bg="#2c3e50", relief=tk.SUNKEN)
            btn_compra.config(bg="#7f8c8d", relief=tk.RAISED)
        
        # Botões para alternar campo
        campo_frame = tk.Frame(right_frame, bg="white")
        campo_frame.pack(pady=(0, 8))
        
        btn_compra = tk.Button(
            campo_frame, text="Compra", font=("Arial", 9, "bold"),
            bg="#2c3e50", fg="white", command=focar_compra, cursor="hand2", padx=8, pady=3
        )
        btn_compra.pack(side=tk.LEFT, padx=2)
        
        btn_recebido = tk.Button(
            campo_frame, text="Recebido", font=("Arial", 9, "bold"),
            bg="#7f8c8d", fg="white", command=focar_recebido, cursor="hand2", padx=8, pady=3
        )
        btn_recebido.pack(side=tk.LEFT, padx=2)
        
        # Teclado numérico customizado
        teclado = TecladoNumerico(right_frame, entry_valor_compra)
        teclado.pack()
        
        # Atualizar entry do teclado quando mudar foco
        def atualizar_teclado_compra(e):
            teclado.entry_alvo = entry_valor_compra
            focar_compra()
        
        def atualizar_teclado_recebido(e):
            teclado.entry_alvo = entry_valor_recebido
            focar_recebido()
        
        entry_valor_compra.bind('<FocusIn>', atualizar_teclado_compra)
        entry_valor_recebido.bind('<FocusIn>', atualizar_teclado_recebido)
        
        def salvar():
            valido, valor_compra = validar_valor(entry_valor_compra.get())
            if not valido:
                messagebox.showerror("Erro", "Valor da compra inválido!", parent=dialog)
                return
            
            if valor_compra <= 0:
                messagebox.showerror("Erro", "Valor deve ser maior que zero!", parent=dialog)
                return
            
            # Buscar ID do dinheiro
            formas = self.db.listar_formas_pagamento()
            forma_id = next((f['id'] for f in formas if f['nome'].lower() == 'dinheiro'), None)
            
            self.db.adicionar_lancamento(
                self.caixa_id,
                "Entrada",
                "Venda",
                valor_compra,
                forma_id,
                entry_obs.get().strip()
            )
            
            self.atualizar_painel()
            dialog.destroy()
            messagebox.showinfo("Sucesso", f"Venda registrada: {formatar_moeda(valor_compra)}")
        
        # Botões de ação
        botoes_frame = tk.Frame(frame, bg="white")
        botoes_frame.pack(pady=(15, 0))
        
        tk.Button(
            botoes_frame,
            text="✓ Registrar Venda",
            font=("Arial", 11, "bold"),
            bg="#27ae60",
            fg="white",
            command=salvar,
            cursor="hand2",
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            botoes_frame,
            text="✗ Cancelar",
            font=("Arial", 11),
            bg="#95a5a6",
            fg="white",
            command=dialog.destroy,
            cursor="hand2",
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
    
    def venda_outros(self):
        """Registra uma venda em outras formas de pagamento"""
        self._dialog_lancamento("Entrada", "Venda", "💳 Venda PIX/Cartão", mostrar_forma=True)
    
    def sangria(self):
        """Registra uma sangria com categoria e motivo obrigatório"""
        dialog = tk.Toplevel(self)
        dialog.title("Sangria")
        dialog.geometry("580x520")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        frame = tk.Frame(dialog, bg="white", padx=20, pady=15)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            frame,
            text="💸 Sangria",
            font=("Arial", 16, "bold"),
            bg="white"
        ).pack(pady=(0, 10))
        
        # Categoria com botões
        tk.Label(frame, text="Categoria da Retirada:", font=("Arial", 10, "bold"), bg="white").pack(anchor=tk.W)
        categoria_var = tk.StringVar(value="Retirada")
        
        categorias_frame = tk.Frame(frame, bg="white")
        categorias_frame.pack(fill=tk.X, pady=(5, 15))
        
        categorias = [
            ("💵 Retirada", "Retirada", "#9b59b6"),
            ("🏪 Despesas", "Despesas da Loja", "#e67e22"),
            ("📦 Fornecedor", "Pagamento Fornecedor", "#3498db"),
            ("📝 Outros", "Outros", "#95a5a6"),
        ]
        
        botoes_categoria = []
        
        def selecionar_categoria(valor, btn_selecionado):
            categoria_var.set(valor)
            for btn, cor_original in botoes_categoria:
                if btn == btn_selecionado:
                    btn.config(bg="#2c3e50", relief=tk.SUNKEN)
                else:
                    btn.config(bg=cor_original, relief=tk.RAISED)
        
        for i, (texto, valor, cor) in enumerate(categorias):
            btn = tk.Button(
                categorias_frame,
                text=texto,
                font=("Arial", 10, "bold"),
                bg=cor,
                fg="white",
                cursor="hand2",
                relief=tk.RAISED,
                padx=10,
                pady=10
            )
            btn.config(command=lambda v=valor, b=btn: selecionar_categoria(v, b))
            btn.pack(side=tk.LEFT, padx=3, expand=True, fill=tk.X)
            botoes_categoria.append((btn, cor))
        
        # Selecionar primeiro por padrão
        if botoes_categoria:
            botoes_categoria[0][0].config(bg="#2c3e50", relief=tk.SUNKEN)
        
        # Container principal com valor e teclado
        container = tk.Frame(frame, bg="white")
        container.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Lado esquerdo - Valor e observação
        left_frame = tk.Frame(container, bg="white")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        # Valor
        tk.Label(left_frame, text="Valor (R$):", font=("Arial", 10, "bold"), bg="white").pack(anchor=tk.W)
        entry_valor = tk.Entry(left_frame, font=("Arial", 18, "bold"), width=15, justify=tk.RIGHT)
        entry_valor.pack(fill=tk.X, pady=(5, 15))
        entry_valor.focus()
        
        # Observação (obrigatória)
        tk.Label(left_frame, text="Motivo (obrigatório):", font=("Arial", 10, "bold"), 
                bg="white", fg="#e74c3c").pack(anchor=tk.W)
        entry_obs = tk.Entry(left_frame, font=("Arial", 11), width=20)
        entry_obs.pack(fill=tk.X, pady=(5, 5))
        
        tk.Label(left_frame, text="Descreva o motivo da retirada", 
                font=("Arial", 8), bg="white", fg="#777").pack(anchor=tk.W)
        
        # Lado direito - Teclado numérico
        right_frame = tk.Frame(container, bg="white")
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        teclado = TecladoNumerico(right_frame, entry_valor)
        teclado.pack()
        
        def salvar():
            valido, valor = validar_valor(entry_valor.get())
            if not valido:
                messagebox.showerror("Erro", "Valor inválido!", parent=dialog)
                return
            
            if valor <= 0:
                messagebox.showerror("Erro", "Valor deve ser maior que zero!", parent=dialog)
                return
            
            motivo = entry_obs.get().strip()
            if not motivo:
                messagebox.showerror("Erro", "O motivo da retirada é obrigatório!", parent=dialog)
                entry_obs.focus()
                return
            
            categoria = categoria_var.get()
            
            self.db.adicionar_lancamento(
                self.caixa_id,
                "Saída",
                f"Sangria - {categoria}",
                valor,
                None,
                motivo
            )
            
            self.atualizar_painel()
            dialog.destroy()
            messagebox.showinfo("Sucesso", f"Sangria registrada: {formatar_moeda(valor)}")
        
        # Botões de ação
        botoes_frame = tk.Frame(frame, bg="white")
        botoes_frame.pack(pady=(15, 0))
        
        tk.Button(
            botoes_frame,
            text="✓ Registrar Sangria",
            font=("Arial", 11, "bold"),
            bg="#e74c3c",
            fg="white",
            command=salvar,
            cursor="hand2",
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            botoes_frame,
            text="✗ Cancelar",
            font=("Arial", 11),
            bg="#95a5a6",
            fg="white",
            command=dialog.destroy,
            cursor="hand2",
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        entry_valor.bind('<Return>', lambda e: entry_obs.focus())
        entry_obs.bind('<Return>', lambda e: salvar())
    
    def suprimento(self):
        """Registra um suprimento"""
        self._dialog_lancamento("Entrada", "Suprimento", "➕ Suprimento")
    
    def outro_lancamento(self):
        """Registra outro tipo de lançamento"""
        self._dialog_lancamento_completo()
    
    def _dialog_lancamento(self, tipo, categoria, titulo, mostrar_forma=False):
        """Dialog genérico para lançamentos com teclado numérico"""
        dialog = tk.Toplevel(self)
        dialog.title(titulo)
        dialog.geometry("580x520")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        frame = tk.Frame(dialog, bg="white", padx=20, pady=15)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            frame,
            text=titulo,
            font=("Arial", 16, "bold"),
            bg="white"
        ).pack(pady=(0, 15))
        
        # Container principal
        container = tk.Frame(frame, bg="white")
        container.pack(fill=tk.BOTH, expand=True)
        
        # Lado esquerdo - Campos
        left_frame = tk.Frame(container, bg="white")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        # Valor
        tk.Label(left_frame, text="Valor (R$):", font=("Arial", 10, "bold"), bg="white").pack(anchor=tk.W)
        entry_valor = tk.Entry(left_frame, font=("Arial", 18, "bold"), width=15, justify=tk.RIGHT)
        entry_valor.pack(fill=tk.X, pady=(5, 15))
        entry_valor.focus()
        
        # Forma de pagamento (se necessário)
        forma_var = None
        if mostrar_forma:
            tk.Label(left_frame, text="Forma de Pagamento:", font=("Arial", 10, "bold"), bg="white").pack(anchor=tk.W)
            forma_var = tk.StringVar()
            formas = self.db.listar_formas_pagamento()
            formas_nomes = [f['nome'] for f in formas if f['nome'].lower() != 'dinheiro']
            
            # Botões de forma de pagamento
            formas_frame = tk.Frame(left_frame, bg="white")
            formas_frame.pack(fill=tk.X, pady=(5, 15))
            
            botoes_forma = []
            cores_forma = ["#3498db", "#9b59b6", "#e67e22", "#1abc9c"]
            
            def selecionar_forma(valor, btn_selecionado):
                forma_var.set(valor)
                for btn, cor_original in botoes_forma:
                    if btn == btn_selecionado:
                        btn.config(bg="#2c3e50", relief=tk.SUNKEN)
                    else:
                        btn.config(bg=cor_original, relief=tk.RAISED)
            
            for i, nome in enumerate(formas_nomes[:4]):  # Máximo 4 formas
                cor = cores_forma[i % len(cores_forma)]
                btn = tk.Button(
                    formas_frame,
                    text=nome,
                    font=("Arial", 10, "bold"),
                    bg=cor,
                    fg="white",
                    cursor="hand2",
                    relief=tk.RAISED,
                    padx=8,
                    pady=8
                )
                btn.config(command=lambda v=nome, b=btn: selecionar_forma(v, b))
                btn.pack(side=tk.LEFT, padx=3, expand=True, fill=tk.X)
                botoes_forma.append((btn, cor))
            
            if formas_nomes and botoes_forma:
                forma_var.set(formas_nomes[0])
                botoes_forma[0][0].config(bg="#2c3e50", relief=tk.SUNKEN)
        
        # Observação
        tk.Label(left_frame, text="Observação:", font=("Arial", 10), bg="white").pack(anchor=tk.W)
        entry_obs = tk.Entry(left_frame, font=("Arial", 11), width=20)
        entry_obs.pack(fill=tk.X, pady=(5, 10))
        
        # Lado direito - Teclado numérico
        right_frame = tk.Frame(container, bg="white")
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        teclado = TecladoNumerico(right_frame, entry_valor)
        teclado.pack()
        
        def salvar():
            valido, valor = validar_valor(entry_valor.get())
            if not valido:
                messagebox.showerror("Erro", "Valor inválido!", parent=dialog)
                return
            
            if valor <= 0:
                messagebox.showerror("Erro", "Valor deve ser maior que zero!", parent=dialog)
                return
            
            forma_id = None
            if mostrar_forma and forma_var:
                formas = self.db.listar_formas_pagamento()
                forma_nome = forma_var.get()
                forma_id = next((f['id'] for f in formas if f['nome'] == forma_nome), None)
            
            self.db.adicionar_lancamento(
                self.caixa_id,
                tipo,
                categoria,
                valor,
                forma_id,
                entry_obs.get().strip()
            )
            
            self.atualizar_painel()
            dialog.destroy()
            messagebox.showinfo("Sucesso", f"Lançamento registrado: {formatar_moeda(valor)}")
        
        # Botões de ação
        botoes_frame = tk.Frame(frame, bg="white")
        botoes_frame.pack(pady=(15, 0))
        
        tk.Button(
            botoes_frame,
            text="✓ Registrar",
            font=("Arial", 11, "bold"),
            bg="#3498db",
            fg="white",
            command=salvar,
            cursor="hand2",
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            botoes_frame,
            text="✗ Cancelar",
            font=("Arial", 11),
            bg="#95a5a6",
            fg="white",
            command=dialog.destroy,
            cursor="hand2",
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        entry_valor.bind('<Return>', lambda e: salvar())
    
    def _dialog_lancamento_completo(self):
        """Dialog completo para outros lançamentos"""
        dialog = tk.Toplevel(self)
        dialog.title("Novo Lançamento")
        dialog.geometry("580x520")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        frame = tk.Frame(dialog, bg="white", padx=20, pady=15)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            frame,
            text="📝 Novo Lançamento",
            font=("Arial", 16, "bold"),
            bg="white"
        ).pack(pady=(0, 15))
        
        # Container principal
        container = tk.Frame(frame, bg="white")
        container.pack(fill=tk.BOTH, expand=True)
        
        # Lado esquerdo - Campos
        left_frame = tk.Frame(container, bg="white")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        # Tipo com botões
        tk.Label(left_frame, text="Tipo:", font=("Arial", 10, "bold"), bg="white").pack(anchor=tk.W)
        tipo_var = tk.StringVar(value="Entrada")
        
        tipo_frame = tk.Frame(left_frame, bg="white")
        tipo_frame.pack(fill=tk.X, pady=(5, 12))
        
        btn_entrada = tk.Button(
            tipo_frame, text="📥 Entrada", font=("Arial", 10, "bold"),
            bg="#27ae60", fg="white", cursor="hand2", padx=12, pady=8
        )
        btn_saida = tk.Button(
            tipo_frame, text="📤 Saída", font=("Arial", 10, "bold"),
            bg="#7f8c8d", fg="white", cursor="hand2", padx=12, pady=8
        )
        
        def selecionar_tipo(tipo):
            tipo_var.set(tipo)
            if tipo == "Entrada":
                btn_entrada.config(bg="#27ae60", relief=tk.SUNKEN)
                btn_saida.config(bg="#7f8c8d", relief=tk.RAISED)
            else:
                btn_entrada.config(bg="#7f8c8d", relief=tk.RAISED)
                btn_saida.config(bg="#e74c3c", relief=tk.SUNKEN)
        
        btn_entrada.config(command=lambda: selecionar_tipo("Entrada"), relief=tk.SUNKEN)
        btn_saida.config(command=lambda: selecionar_tipo("Saída"))
        btn_entrada.pack(side=tk.LEFT, padx=3, expand=True, fill=tk.X)
        btn_saida.pack(side=tk.LEFT, padx=3, expand=True, fill=tk.X)
        
        # Categoria com botões
        tk.Label(left_frame, text="Categoria:", font=("Arial", 10, "bold"), bg="white").pack(anchor=tk.W)
        categoria_var = tk.StringVar(value="Venda")
        
        cat_frame = tk.Frame(left_frame, bg="white")
        cat_frame.pack(fill=tk.X, pady=(5, 12))
        
        categorias = [("Venda", "#3498db"), ("Sangria", "#9b59b6"), ("Suprimento", "#e67e22"), ("Despesa", "#e74c3c"), ("Outros", "#95a5a6")]
        botoes_cat = []
        
        def selecionar_cat(cat, btn):
            categoria_var.set(cat)
            for b, cor in botoes_cat:
                if b == btn:
                    b.config(bg="#2c3e50", relief=tk.SUNKEN)
                else:
                    b.config(bg=cor, relief=tk.RAISED)
        
        for cat, cor in categorias:
            btn = tk.Button(cat_frame, text=cat, font=("Arial", 9, "bold"), bg=cor, fg="white", cursor="hand2", padx=5, pady=5)
            btn.config(command=lambda c=cat, b=btn: selecionar_cat(c, b))
            btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
            botoes_cat.append((btn, cor))
        
        botoes_cat[0][0].config(bg="#2c3e50", relief=tk.SUNKEN)
        
        # Valor
        tk.Label(left_frame, text="Valor (R$):", font=("Arial", 10, "bold"), bg="white").pack(anchor=tk.W)
        entry_valor = tk.Entry(left_frame, font=("Arial", 16, "bold"), width=15, justify=tk.RIGHT)
        entry_valor.pack(fill=tk.X, pady=(5, 12))
        entry_valor.focus()
        
        # Forma de pagamento
        tk.Label(left_frame, text="Forma de Pagamento:", font=("Arial", 10, "bold"), bg="white").pack(anchor=tk.W)
        forma_var = tk.StringVar()
        formas = self.db.listar_formas_pagamento()
        formas_nomes = [f['nome'] for f in formas]
        
        formas_frame = tk.Frame(left_frame, bg="white")
        formas_frame.pack(fill=tk.X, pady=(5, 12))
        
        botoes_forma = []
        cores_forma = ["#1abc9c", "#3498db", "#9b59b6", "#e67e22"]
        
        def selecionar_forma(nome, btn):
            forma_var.set(nome)
            for b, cor in botoes_forma:
                if b == btn:
                    b.config(bg="#2c3e50", relief=tk.SUNKEN)
                else:
                    b.config(bg=cor, relief=tk.RAISED)
        
        for i, nome in enumerate(formas_nomes[:4]):
            cor = cores_forma[i % len(cores_forma)]
            btn = tk.Button(formas_frame, text=nome, font=("Arial", 9, "bold"), bg=cor, fg="white", cursor="hand2", padx=5, pady=5)
            btn.config(command=lambda n=nome, b=btn: selecionar_forma(n, b))
            btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
            botoes_forma.append((btn, cor))
        
        if formas_nomes and botoes_forma:
            forma_var.set(formas_nomes[0])
            botoes_forma[0][0].config(bg="#2c3e50", relief=tk.SUNKEN)
        
        # Observação
        tk.Label(left_frame, text="Observação:", font=("Arial", 10), bg="white").pack(anchor=tk.W)
        entry_obs = tk.Entry(left_frame, font=("Arial", 10), width=20)
        entry_obs.pack(fill=tk.X, pady=(5, 10))
        
        # Lado direito - Teclado numérico
        right_frame = tk.Frame(container, bg="white")
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        teclado = TecladoNumerico(right_frame, entry_valor)
        teclado.pack()
        
        def salvar():
            valido, valor = validar_valor(entry_valor.get())
            if not valido:
                messagebox.showerror("Erro", "Valor inválido!", parent=dialog)
                return
            
            if valor <= 0:
                messagebox.showerror("Erro", "Valor deve ser maior que zero!", parent=dialog)
                return
            
            tipo = tipo_var.get()
            categoria = categoria_var.get()
            
            forma_nome = forma_var.get()
            forma_id = next((f['id'] for f in formas if f['nome'] == forma_nome), None)
            
            self.db.adicionar_lancamento(
                self.caixa_id,
                tipo,
                categoria,
                valor,
                forma_id,
                entry_obs.get().strip()
            )
            
            self.atualizar_painel()
            dialog.destroy()
            messagebox.showinfo("Sucesso", f"Lançamento registrado: {formatar_moeda(valor)}")
        
        # Botões de ação
        botoes_frame = tk.Frame(frame, bg="white")
        botoes_frame.pack(pady=(15, 0))
        
        tk.Button(
            botoes_frame,
            text="✓ Registrar",
            font=("Arial", 11, "bold"),
            bg="#3498db",
            fg="white",
            command=salvar,
            cursor="hand2",
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            botoes_frame,
            text="✗ Cancelar",
            font=("Arial", 11),
            bg="#95a5a6",
            fg="white",
            command=dialog.destroy,
            cursor="hand2",
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
    
    def solicitar_senha_adm(self, callback_sucesso):
        """Solicita a senha de administrador antes de executar uma ação"""
        dialog = tk.Toplevel(self)
        dialog.title("Senha de Administrador")
        dialog.geometry("350x180")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        frame = tk.Frame(dialog, bg="white", padx=30, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            frame,
            text="🔒 Senha de Administrador",
            font=("Arial", 12, "bold"),
            bg="white"
        ).pack(pady=(0, 15))
        
        tk.Label(
            frame,
            text="Digite a senha para continuar:",
            font=("Arial", 10),
            bg="white"
        ).pack(anchor=tk.W)
        
        entry_senha = tk.Entry(frame, font=("Arial", 12), show="*", width=20)
        entry_senha.pack(fill=tk.X, pady=(5, 15))
        entry_senha.focus()
        
        def verificar():
            senha = entry_senha.get()
            if self.db.verificar_senha_adm(senha):
                dialog.destroy()
                callback_sucesso()
            else:
                messagebox.showerror("Erro", "Senha incorreta!", parent=dialog)
                entry_senha.delete(0, tk.END)
                entry_senha.focus()
        
        entry_senha.bind('<Return>', lambda e: verificar())
        
        botoes_frame = tk.Frame(frame, bg="white")
        botoes_frame.pack()
        
        tk.Button(
            botoes_frame,
            text="Confirmar",
            font=("Arial", 10, "bold"),
            bg="#27ae60",
            fg="white",
            command=verificar,
            cursor="hand2",
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            botoes_frame,
            text="Cancelar",
            font=("Arial", 10),
            bg="#95a5a6",
            fg="white",
            command=dialog.destroy,
            cursor="hand2",
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
    
    def editar_lancamento(self):
        """Edita um lançamento selecionado"""
        selecao = self.tree.selection()
        if not selecao:
            messagebox.showwarning("Atenção", "Selecione um lançamento para editar!")
            return
        
        # Solicitar senha antes de continuar
        self.solicitar_senha_adm(self._executar_edicao_lancamento)
    
    def _executar_edicao_lancamento(self):
        """Executa a edição do lançamento após validação da senha"""
        selecao = self.tree.selection()
        if not selecao:
            return
        
        # Pegar o índice do item selecionado
        item = selecao[0]
        indice = self.tree.index(item)
        
        # Buscar os lançamentos novamente
        lancamentos = self.db.listar_lancamentos(caixa_id=self.caixa_id)
        
        if indice >= len(lancamentos):
            messagebox.showerror("Erro", "Lançamento não encontrado!")
            return
        
        lancamento = lancamentos[indice]
        
        # Verificar se está cancelado
        if lancamento.get('cancelado'):
            messagebox.showwarning("Atenção", "Não é possível editar um lançamento cancelado!")
            return
        
        # Buscar dados completos do lançamento
        lanc_completo = self.db.obter_lancamento(lancamento['id'])
        if not lanc_completo:
            messagebox.showerror("Erro", "Erro ao carregar dados do lançamento!")
            return
        
        # Verificar se o lançamento é do dia atual
        data_lancamento = lanc_completo.get('data_hora', '')
        if data_lancamento:
            try:
                # Extrair apenas a data (YYYY-MM-DD) do timestamp
                data_lanc = data_lancamento.split()[0] if ' ' in data_lancamento else data_lancamento[:10]
                data_hoje = datetime.now().strftime("%Y-%m-%d")
                
                if data_lanc != data_hoje:
                    messagebox.showwarning(
                        "Atenção", 
                        "Só é permitido editar lançamentos do dia atual!\n\n"
                        f"Este lançamento é do dia {data_lanc}."
                    )
                    return
            except:
                pass  # Se houver erro na validação, permite editar
        
        # Criar dialog de edição
        dialog = tk.Toplevel(self)
        dialog.title("Editar Lançamento")
        dialog.geometry("450x580")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        frame = tk.Frame(dialog, bg="white", padx=30, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            frame,
            text="✏️ Editar Lançamento",
            font=("Arial", 14, "bold"),
            bg="white"
        ).pack(pady=(0, 10))
        
        # Mostrar hora do lançamento original
        hora_lanc = formatar_data(lanc_completo['data_hora']) if lanc_completo.get('data_hora') else "N/A"
        tk.Label(
            frame,
            text=f"📅 Lançado em: {hora_lanc}",
            font=("Arial", 9),
            bg="white",
            fg="#666"
        ).pack(anchor=tk.W)
        
        # Mostrar hora da última edição se existir
        if lanc_completo.get('data_edicao'):
            hora_edicao = formatar_data(lanc_completo['data_edicao'])
            tk.Label(
                frame,
                text=f"✏️ Última edição: {hora_edicao}",
                font=("Arial", 9),
                bg="white",
                fg="#f39c12"
            ).pack(anchor=tk.W)
        
        tk.Frame(frame, height=10, bg="white").pack()
        
        # Tipo
        tk.Label(frame, text="Tipo:", font=("Arial", 10), bg="white").pack(anchor=tk.W)
        tipo_var = tk.StringVar(value=lanc_completo['tipo'])
        ttk.Combobox(frame, textvariable=tipo_var, values=["Entrada", "Saída"], 
                    font=("Arial", 10), state="readonly").pack(fill=tk.X, pady=(5, 15))
        
        # Categoria
        tk.Label(frame, text="Categoria:", font=("Arial", 10), bg="white").pack(anchor=tk.W)
        categoria_var = tk.StringVar(value=lanc_completo['categoria'])
        categorias = ["Venda", "Sangria", "Suprimento", "Despesa", "Outros"]
        ttk.Combobox(frame, textvariable=categoria_var, values=categorias,
                    font=("Arial", 10)).pack(fill=tk.X, pady=(5, 15))
        
        # Valor
        tk.Label(frame, text="Valor (R$):", font=("Arial", 10), bg="white").pack(anchor=tk.W)
        entry_valor = tk.Entry(frame, font=("Arial", 12), width=25)
        entry_valor.insert(0, str(lanc_completo['valor']).replace('.', ','))
        entry_valor.pack(fill=tk.X, pady=(5, 15))
        entry_valor.focus()
        
        # Forma de pagamento
        tk.Label(frame, text="Forma de Pagamento:", font=("Arial", 10), bg="white").pack(anchor=tk.W)
        forma_var = tk.StringVar()
        formas = self.db.listar_formas_pagamento()
        formas_nomes = [f['nome'] for f in formas]
        combo_forma = ttk.Combobox(frame, textvariable=forma_var, values=formas_nomes,
                                   font=("Arial", 10), state="readonly")
        
        # Selecionar forma atual
        forma_atual = lanc_completo.get('forma_pagamento_nome', '')
        if forma_atual and forma_atual in formas_nomes:
            combo_forma.set(forma_atual)
        elif formas_nomes:
            combo_forma.current(0)
        combo_forma.pack(fill=tk.X, pady=(5, 15))
        
        # Observação
        tk.Label(frame, text="Observação:", font=("Arial", 10), bg="white").pack(anchor=tk.W)
        entry_obs = tk.Entry(frame, font=("Arial", 10), width=25)
        entry_obs.insert(0, lanc_completo.get('observacao', '') or '')
        entry_obs.pack(fill=tk.X, pady=(5, 15))
        
        def salvar_edicao():
            valido, valor = validar_valor(entry_valor.get())
            if not valido:
                messagebox.showerror("Erro", "Valor inválido!", parent=dialog)
                return
            
            if valor <= 0:
                messagebox.showerror("Erro", "Valor deve ser maior que zero!", parent=dialog)
                return
            
            tipo = tipo_var.get()
            categoria = categoria_var.get()
            
            forma_nome = forma_var.get()
            forma_id = next((f['id'] for f in formas if f['nome'] == forma_nome), None)
            
            self.db.atualizar_lancamento(
                lanc_completo['id'],
                tipo,
                categoria,
                valor,
                forma_id,
                entry_obs.get().strip()
            )
            
            self.atualizar_painel()
            dialog.destroy()
            messagebox.showinfo("Sucesso", f"Lançamento atualizado: {formatar_moeda(valor)}")
        
        # Botões
        botoes_frame = tk.Frame(frame, bg="white")
        botoes_frame.pack(pady=(10, 0))
        
        tk.Button(
            botoes_frame,
            text="Salvar Alterações",
            font=("Arial", 11, "bold"),
            bg="#27ae60",
            fg="white",
            command=salvar_edicao,
            cursor="hand2",
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            botoes_frame,
            text="Cancelar",
            font=("Arial", 11),
            bg="#95a5a6",
            fg="white",
            command=dialog.destroy,
            cursor="hand2",
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
    
    def cancelar_lancamento(self):
        """Cancela um lançamento selecionado"""
        selecao = self.tree.selection()
        if not selecao:
            messagebox.showwarning("Atenção", "Selecione um lançamento para cancelar!")
            return
        
        resposta = messagebox.askyesno(
            "Confirmar Cancelamento",
            "Tem certeza que deseja cancelar este lançamento?\n\n"
            "Esta ação não pode ser desfeita!"
        )
        
        if resposta:
            # Solicitar senha antes de continuar
            self.solicitar_senha_adm(self._executar_cancelamento_lancamento)
    
    def _executar_cancelamento_lancamento(self):
        """Executa o cancelamento do lançamento após validação da senha"""
        selecao = self.tree.selection()
        if not selecao:
            return
        
        # Pegar o índice do item selecionado
        item = selecao[0]
        indice = self.tree.index(item)
        
        # Buscar os lançamentos novamente
        lancamentos = self.db.listar_lancamentos(caixa_id=self.caixa_id)
        
        if indice < len(lancamentos):
            lancamento = lancamentos[indice]
            self.db.cancelar_lancamento(lancamento['id'])
            self.atualizar_painel()
            messagebox.showinfo("Sucesso", "Lançamento cancelado!")
