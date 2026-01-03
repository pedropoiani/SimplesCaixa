#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telas de abertura e fechamento de caixa
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import Database
from utils import formatar_moeda, validar_valor, formatar_data, exportar_relatorio_caixa_pdf, fazer_backup_silencioso
from tema import (
    COR_PRIMARIA, COR_PRIMARIA_CLARA, COR_SUCESSO, COR_SUCESSO_ESCURA,
    COR_SECUNDARIA, COR_PERIGO, COR_FUNDO, COR_TEXTO_CLARO,
    COR_TECLADO_NUMERO, obter_logo_perfil
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

class AberturaView(tk.Frame):
    """Tela de abertura de caixa"""
    
    def __init__(self, parent, db: Database, voltar_callback, abrir_callback, historico_callback=None):
        super().__init__(parent)
        self.db = db
        self.voltar_callback = voltar_callback
        self.abrir_callback = abrir_callback
        self.historico_callback = historico_callback
        
        self.configure(bg=COR_FUNDO)
        self.logo_img = None
        self.criar_widgets()
    
    def criar_widgets(self):
        """Cria os widgets da interface"""
        # Título com cores da loja MF
        titulo_frame = tk.Frame(self, bg=COR_SUCESSO, height=70)
        titulo_frame.pack(fill=tk.X)
        titulo_frame.pack_propagate(False)
        
        # Container para logo e título
        header_content = tk.Frame(titulo_frame, bg=COR_SUCESSO)
        header_content.pack(pady=10)
        
        # Carregar logo (se PIL disponível)
        if PIL_DISPONIVEL:
            try:
                logo_path = obter_logo_perfil()
                img = Image.open(logo_path)
                img = img.resize((50, 50), Image.Resampling.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(img)
                logo_label = tk.Label(header_content, image=self.logo_img, bg=COR_SUCESSO)
                logo_label.pack(side=tk.LEFT, padx=(0, 10))
            except:
                pass
        
        tk.Label(
            header_content,
            text="🔓 Abertura de Caixa",
            font=("Arial", 18, "bold"),
            bg=COR_SUCESSO,
            fg=COR_TEXTO_CLARO
        ).pack(side=tk.LEFT)
        
        # Container principal
        container = tk.Frame(self, bg="white")
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Informações
        info_text = (
            "Informe os dados para abertura do caixa.\n"
            "O troco inicial é o dinheiro que você coloca no caixa para dar troco."
        )
        tk.Label(
            container,
            text=info_text,
            font=("Arial", 10),
            bg="white",
            fg="#555",
            justify=tk.LEFT
        ).pack(pady=(0, 15))
        
        # Container com campos e teclado
        main_frame = tk.Frame(container, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Lado esquerdo - Campos
        left_frame = tk.Frame(main_frame, bg="white")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        
        # Operador
        tk.Label(
            left_frame,
            text="Operador:",
            font=("Arial", 11, "bold"),
            bg="white"
        ).pack(anchor=tk.W)
        
        self.entry_operador = tk.Entry(
            left_frame,
            font=("Arial", 12),
            width=25
        )
        self.entry_operador.pack(fill=tk.X, pady=(5, 15))
        
        # Troco inicial
        tk.Label(
            left_frame,
            text="Troco Inicial (R$):",
            font=("Arial", 11, "bold"),
            bg="white"
        ).pack(anchor=tk.W)
        
        self.entry_troco = tk.Entry(
            left_frame,
            font=("Arial", 18, "bold"),
            width=15,
            justify=tk.RIGHT
        )
        self.entry_troco.pack(fill=tk.X, pady=(5, 15))
        self.entry_troco.insert(0, "0,00")
        self.entry_troco.focus()
        
        # Lado direito - Teclado numérico
        right_frame = tk.Frame(main_frame, bg="white")
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        teclado = TecladoNumerico(right_frame, self.entry_troco)
        teclado.pack()
        
        # Botões
        botoes_frame = tk.Frame(container, bg="white")
        botoes_frame.pack(pady=(20, 0))
        
        tk.Button(
            botoes_frame,
            text="✓ Abrir Caixa",
            font=("Arial", 12, "bold"),
            bg=COR_SUCESSO,
            fg=COR_TEXTO_CLARO,
            command=self.abrir_caixa,
            cursor="hand2",
            relief=tk.FLAT,
            padx=30,
            pady=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            botoes_frame,
            text="✗ Cancelar",
            font=("Arial", 12),
            bg="#95a5a6",
            fg="white",
            command=self.voltar_callback,
            cursor="hand2",
            relief=tk.FLAT,
            padx=30,
            pady=15
        ).pack(side=tk.LEFT, padx=5)
        
        # Botão Ver Relatórios (se callback disponível)
        if self.historico_callback:
            tk.Button(
                botoes_frame,
                text="📊 Ver Relatórios",
                font=("Arial", 12),
                bg=COR_PRIMARIA,
                fg=COR_TEXTO_CLARO,
                command=self.historico_callback,
                cursor="hand2",
                relief=tk.FLAT,
                padx=30,
                pady=15
            ).pack(side=tk.LEFT, padx=5)
        
        self.entry_troco.bind('<Return>', lambda e: self.abrir_caixa())
    
    def abrir_caixa(self):
        """Abre o caixa"""
        # Validar troco inicial
        valido, resultado = validar_valor(self.entry_troco.get())
        if not valido:
            messagebox.showerror("Erro", f"Troco inicial inválido:\n{resultado}")
            return
        
        troco_inicial = resultado
        operador = self.entry_operador.get().strip() or "Não informado"
        
        # Confirmar abertura
        resposta = messagebox.askyesno(
            "Confirmar Abertura",
            f"Abrir caixa com:\n\n"
            f"Operador: {operador}\n"
            f"Troco Inicial: {formatar_moeda(troco_inicial)}\n\n"
            f"Confirma?"
        )
        
        if resposta:
            caixa_id = self.db.abrir_caixa(troco_inicial, operador)
            messagebox.showinfo("Sucesso", "Caixa aberto com sucesso!")
            self.abrir_callback(caixa_id)


class FechamentoView(tk.Frame):
    """Tela de fechamento de caixa"""
    
    def __init__(self, parent, db: Database, caixa_id: int, fechar_callback):
        super().__init__(parent)
        self.db = db
        self.caixa_id = caixa_id
        self.fechar_callback = fechar_callback
        
        self.configure(bg=COR_FUNDO)
        self.criar_widgets()
        self.atualizar_resumo()
    
    def criar_widgets(self):
        """Cria os widgets da interface"""
        # Título com cor da loja MF
        titulo_frame = tk.Frame(self, bg=COR_SECUNDARIA, height=60)
        titulo_frame.pack(fill=tk.X)
        titulo_frame.pack_propagate(False)
        
        tk.Label(
            titulo_frame,
            text="🔒 Fechamento de Caixa",
            font=("Arial", 18, "bold"),
            bg=COR_SECUNDARIA,
            fg=COR_TEXTO_CLARO
        ).pack(pady=15)
        
        # Container principal com scroll
        canvas = tk.Canvas(self, bg=COR_FUNDO, highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COR_FUNDO)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=20)
        
        # Frame de resumo
        resumo_frame = tk.LabelFrame(
            scrollable_frame,
            text="Resumo do Caixa",
            font=("Arial", 12, "bold"),
            bg="white",
            padx=20,
            pady=20
        )
        resumo_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Labels de resumo
        self.label_troco = self._criar_label_resumo(resumo_frame, "Troco Inicial:", 0)
        self.label_entradas = self._criar_label_resumo(resumo_frame, "Total Entradas:", 1)
        self.label_dinheiro = self._criar_label_resumo(resumo_frame, "• Dinheiro:", 2, indent=True)
        self.label_cartao = self._criar_label_resumo(resumo_frame, "• Cartão:", 3, indent=True)
        self.label_pix = self._criar_label_resumo(resumo_frame, "• PIX:", 4, indent=True)
        self.label_saidas = self._criar_label_resumo(resumo_frame, "Total Saídas:", 5)
        
        ttk.Separator(resumo_frame, orient='horizontal').grid(
            row=6, column=0, columnspan=2, sticky=tk.EW, pady=10
        )
        
        self.label_saldo_dinheiro = tk.Label(
            resumo_frame,
            text="💰 Dinheiro no Caixa: R$ 0,00",
            font=("Arial", 14, "bold"),
            bg="white",
            fg="#27ae60"
        )
        self.label_saldo_dinheiro.grid(row=7, column=0, columnspan=2, pady=5)
        
        self.label_outros = tk.Label(
            resumo_frame,
            text="(Cartão + PIX: R$ 0,00)",
            font=("Arial", 10),
            bg="white",
            fg="#555"
        )
        self.label_outros.grid(row=8, column=0, columnspan=2, pady=(0, 10))
        
        # Frame de contagem com teclado
        contagem_frame = tk.LabelFrame(
            scrollable_frame,
            text="Conferência",
            font=("Arial", 12, "bold"),
            bg="white",
            padx=20,
            pady=20
        )
        contagem_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Container para campos e teclado
        conferencia_container = tk.Frame(contagem_frame, bg="white")
        conferencia_container.pack(fill=tk.X)
        
        # Lado esquerdo - Campos
        left_conf = tk.Frame(conferencia_container, bg="white")
        left_conf.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        tk.Label(
            left_conf,
            text="Dinheiro Contado (R$):",
            font=("Arial", 11, "bold"),
            bg="white"
        ).pack(anchor=tk.W)
        
        tk.Label(
            left_conf,
            text="(Conte apenas o dinheiro físico no caixa)",
            font=("Arial", 9),
            bg="white",
            fg="#777"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.entry_valor_contado = tk.Entry(
            left_conf,
            font=("Arial", 16, "bold"),
            width=18,
            justify=tk.RIGHT
        )
        self.entry_valor_contado.pack(fill=tk.X, pady=(5, 10))
        self.entry_valor_contado.bind('<KeyRelease>', lambda e: self.calcular_diferenca())
        
        # Label de diferença
        self.label_diferenca = tk.Label(
            left_conf,
            text="",
            font=("Arial", 12, "bold"),
            bg="white"
        )
        self.label_diferenca.pack(pady=5)
        
        # Observações
        tk.Label(
            left_conf,
            text="Observações:",
            font=("Arial", 11),
            bg="white"
        ).pack(anchor=tk.W, pady=(10, 5))
        
        self.text_observacoes = tk.Text(
            left_conf,
            font=("Arial", 10),
            width=30,
            height=3
        )
        self.text_observacoes.pack(fill=tk.X)
        
        # Lado direito - Teclado numérico
        right_conf = tk.Frame(conferencia_container, bg="white")
        right_conf.pack(side=tk.RIGHT, fill=tk.Y)
        
        teclado = TecladoNumerico(right_conf, self.entry_valor_contado)
        teclado.pack()
        
        # Botões
        botoes_frame = tk.Frame(scrollable_frame, bg=COR_FUNDO)
        botoes_frame.pack(pady=(20, 0))
        
        tk.Button(
            botoes_frame,
            text="✓ Fechar Caixa",
            font=("Arial", 12, "bold"),
            bg=COR_SECUNDARIA,
            fg=COR_TEXTO_CLARO,
            command=self.fechar_caixa,
            cursor="hand2",
            relief=tk.FLAT,
            padx=30,
            pady=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            botoes_frame,
            text="✗ Cancelar",
            font=("Arial", 12),
            bg="#95a5a6",
            fg="white",
            command=self.fechar_callback,
            cursor="hand2",
            relief=tk.FLAT,
            padx=30,
            pady=15
        ).pack(side=tk.LEFT, padx=5)
    
    def _criar_label_resumo(self, parent, texto, row, indent=False):
        """Cria um par de labels para o resumo"""
        label_texto = tk.Label(
            parent,
            text=texto,
            font=("Arial", 11),
            bg="white",
            anchor=tk.W
        )
        if indent:
            label_texto.grid(row=row, column=0, sticky=tk.W, pady=2, padx=(20, 0))
        else:
            label_texto.grid(row=row, column=0, sticky=tk.W, pady=5)
        
        label_valor = tk.Label(
            parent,
            text="R$ 0,00",
            font=("Arial", 11, "bold"),
            bg="white",
            anchor=tk.E
        )
        label_valor.grid(row=row, column=1, sticky=tk.E, pady=5, padx=(20, 0))
        
        return label_valor
    
    def atualizar_resumo(self):
        """Atualiza o resumo do caixa"""
        totais = self.db.obter_totais_caixa_aberto(self.caixa_id)
        por_forma = totais['por_forma_pagamento']
        
        # Valores por forma de pagamento
        dinheiro = por_forma.get('Dinheiro', 0)
        cartao = por_forma.get('Cartão', 0)
        pix = por_forma.get('PIX', 0)
        outros = totais['total_entradas'] - dinheiro - cartao - pix
        
        # Atualizar labels
        self.label_troco.config(text=formatar_moeda(totais['troco_inicial']))
        self.label_entradas.config(text=formatar_moeda(totais['total_entradas']))
        self.label_dinheiro.config(text=formatar_moeda(dinheiro))
        self.label_cartao.config(text=formatar_moeda(cartao))
        self.label_pix.config(text=formatar_moeda(pix))
        self.label_saidas.config(text=formatar_moeda(totais['total_saidas']))
        
        # Calcular saldo esperado em DINHEIRO (troco inicial + dinheiro recebido - saídas)
        self.saldo_esperado_dinheiro = totais['troco_inicial'] + dinheiro - totais['total_saidas']
        self.valor_cartao_pix = cartao + pix + outros
        
        self.label_saldo_dinheiro.config(
            text=f"💰 Dinheiro no Caixa: {formatar_moeda(self.saldo_esperado_dinheiro)}"
        )
        self.label_outros.config(
            text=f"(Cartão + PIX: {formatar_moeda(self.valor_cartao_pix)})"
        )
    
    def calcular_diferenca(self):
        """Calcula a diferença entre o dinheiro contado e o esperado"""
        valor_str = self.entry_valor_contado.get().strip()
        
        if not valor_str:
            self.label_diferenca.config(text="", fg="black")
            return
        
        valido, resultado = validar_valor(valor_str)
        if not valido:
            self.label_diferenca.config(text="Valor inválido", fg="red")
            return
        
        valor_contado = resultado
        diferenca = valor_contado - self.saldo_esperado_dinheiro
        
        if abs(diferenca) < 0.01:
            texto = "✓ Dinheiro confere!"
            cor = "#27ae60"
        elif diferenca > 0:
            texto = f"Sobra: {formatar_moeda(diferenca)}"
            cor = "#f39c12"
        else:
            texto = f"Falta: {formatar_moeda(abs(diferenca))}"
            cor = "#e74c3c"
        
        self.label_diferenca.config(text=texto, fg=cor)
    
    def fechar_caixa(self):
        """Fecha o caixa"""
        # Obter valor contado (se informado)
        valor_contado = None
        valor_str = self.entry_valor_contado.get().strip()
        
        if valor_str:
            valido, resultado = validar_valor(valor_str)
            if not valido:
                messagebox.showerror("Erro", f"Valor contado inválido:\n{resultado}")
                return
            valor_contado = resultado
        
        observacoes = self.text_observacoes.get("1.0", tk.END).strip()
        
        # Confirmar fechamento
        mensagem = "Confirma o fechamento do caixa?\n\n"
        mensagem += f"💰 Dinheiro Esperado no Caixa: {formatar_moeda(self.saldo_esperado_dinheiro)}\n"
        mensagem += f"💳 Cartão + PIX: {formatar_moeda(self.valor_cartao_pix)}\n\n"
        
        if valor_contado is not None:
            mensagem += f"Dinheiro Contado: {formatar_moeda(valor_contado)}\n"
            diferenca = valor_contado - self.saldo_esperado_dinheiro
            if abs(diferenca) > 0.01:
                if diferenca > 0:
                    mensagem += f"Sobra: {formatar_moeda(diferenca)}\n"
                else:
                    mensagem += f"Falta: {formatar_moeda(abs(diferenca))}\n"
        
        mensagem += "\n⚠️ Esta ação não pode ser desfeita!"
        
        resposta = messagebox.askyesno("Confirmar Fechamento", mensagem)
        
        if resposta:
            # Fechar caixa
            resultado = self.db.fechar_caixa(
                self.caixa_id,
                valor_contado,
                observacoes
            )
            
            # Fazer backup automático ao fechar caixa
            fazer_backup_silencioso(self.db.db_path)
            
            # Perguntar se quer salvar relatório em PDF
            salvar = messagebox.askyesno(
                "Relatório",
                "Caixa fechado com sucesso!\n\nBackup realizado automaticamente.\n\nDeseja salvar o relatório de fechamento em PDF?"
            )
            
            if salvar:
                dados = self.db.obter_relatorio_fechamento(self.caixa_id)
                exportar_relatorio_caixa_pdf(dados)
            self.fechar_callback()
