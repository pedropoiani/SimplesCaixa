#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tela de configurações do sistema
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from database import Database
from github_sync import get_github_sync, sincronizar_agora
from tema import (
    COR_PRIMARIA, COR_PRIMARIA_CLARA, COR_SUCESSO, COR_SECUNDARIA,
    COR_PERIGO, COR_FUNDO, COR_TEXTO_CLARO
)

class ConfiguracaoView(tk.Frame):
    """Tela de configurações da loja"""
    
    def __init__(self, parent, db: Database, voltar_callback):
        super().__init__(parent)
        self.db = db
        self.voltar_callback = voltar_callback
        
        self.configure(bg=COR_FUNDO)
        self.criar_widgets()
        self.carregar_configuracoes()
    
    def criar_widgets(self):
        """Cria os widgets da interface"""
        # Título com cores da loja MF
        titulo_frame = tk.Frame(self, bg=COR_PRIMARIA, height=60)
        titulo_frame.pack(fill=tk.X)
        titulo_frame.pack_propagate(False)
        
        tk.Label(
            titulo_frame,
            text="⚙️ Configurações",
            font=("Arial", 18, "bold"),
            bg=COR_PRIMARIA,
            fg=COR_TEXTO_CLARO
        ).pack(pady=15)
        
        # Container principal
        container = tk.Frame(self, bg=COR_FUNDO)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Frame de configurações da loja
        loja_frame = tk.LabelFrame(
            container,
            text="Dados da Loja",
            font=("Arial", 12, "bold"),
            bg="white",
            padx=20,
            pady=20
        )
        loja_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Nome da loja
        tk.Label(
            loja_frame,
            text="Nome da Loja:",
            font=("Arial", 10),
            bg="white"
        ).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.entry_nome_loja = tk.Entry(
            loja_frame,
            font=("Arial", 10),
            width=40
        )
        self.entry_nome_loja.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Responsável
        tk.Label(
            loja_frame,
            text="Responsável:",
            font=("Arial", 10),
            bg="white"
        ).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.entry_responsavel = tk.Entry(
            loja_frame,
            font=("Arial", 10),
            width=40
        )
        self.entry_responsavel.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Botão salvar configurações
        btn_salvar_config = tk.Button(
            loja_frame,
            text="💾 Salvar Configurações",
            font=("Arial", 10, "bold"),
            bg=COR_SUCESSO,
            fg=COR_TEXTO_CLARO,
            command=self.salvar_configuracoes,
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=10
        )
        btn_salvar_config.grid(row=2, column=0, columnspan=2, pady=(15, 0))
        
        # Frame de formas de pagamento
        pagamento_frame = tk.LabelFrame(
            container,
            text="Formas de Pagamento",
            font=("Arial", 12, "bold"),
            bg="white",
            padx=20,
            pady=20
        )
        pagamento_frame.pack(fill=tk.BOTH, expand=True)
        
        # Lista de formas de pagamento
        lista_frame = tk.Frame(pagamento_frame, bg="white")
        lista_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(lista_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox
        self.listbox_formas = tk.Listbox(
            lista_frame,
            font=("Arial", 10),
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE,
            height=6
        )
        self.listbox_formas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox_formas.yview)
        
        # Botões de ação
        botoes_frame = tk.Frame(pagamento_frame, bg="white")
        botoes_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(
            botoes_frame,
            text="➕ Adicionar",
            font=("Arial", 9),
            bg=COR_PRIMARIA,
            fg=COR_TEXTO_CLARO,
            command=self.adicionar_forma_pagamento,
            cursor="hand2",
            relief=tk.FLAT,
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(
            botoes_frame,
            text="✓ Ativar",
            font=("Arial", 9),
            bg=COR_SUCESSO,
            fg=COR_TEXTO_CLARO,
            command=lambda: self.toggle_forma_pagamento(True),
            cursor="hand2",
            relief=tk.FLAT,
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            botoes_frame,
            text="✗ Desativar",
            font=("Arial", 9),
            bg=COR_SECUNDARIA,
            fg=COR_TEXTO_CLARO,
            command=lambda: self.toggle_forma_pagamento(False),
            cursor="hand2",
            relief=tk.FLAT,
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        # Frame de segurança (senha ADM)
        seguranca_frame = tk.LabelFrame(
            container,
            text="🔒 Segurança",
            font=("Arial", 12, "bold"),
            bg="white",
            padx=20,
            pady=20
        )
        seguranca_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Label(
            seguranca_frame,
            text="A senha de administrador é necessária para editar ou cancelar lançamentos.",
            font=("Arial", 9),
            bg="white",
            fg="#666"
        ).pack(anchor=tk.W, pady=(0, 10))
        
        tk.Button(
            seguranca_frame,
            text="🔑 Alterar Senha de Administrador",
            font=("Arial", 10, "bold"),
            bg=COR_SECUNDARIA,
            fg=COR_TEXTO_CLARO,
            command=self.alterar_senha_adm,
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=10
        ).pack()
        
        # Frame do GitHub Pages (Sincronização Mobile)
        github_frame = tk.LabelFrame(
            container,
            text="📱 Acesso Mobile (GitHub Pages)",
            font=("Arial", 12, "bold"),
            bg="white",
            padx=20,
            pady=20
        )
        github_frame.pack(fill=tk.X, pady=(20, 0))
        
        tk.Label(
            github_frame,
            text="Visualize as movimentações no celular através do GitHub Pages.",
            font=("Arial", 9),
            bg="white",
            fg="#666"
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Status da sincronização
        self.github_sync = get_github_sync()
        status_text = "✅ Configurado" if self.github_sync.esta_configurado() else "❌ Não configurado"
        self.label_github_status = tk.Label(
            github_frame,
            text=f"Status: {status_text}",
            font=("Arial", 10),
            bg="white"
        )
        self.label_github_status.pack(anchor=tk.W, pady=(0, 10))
        
        botoes_github = tk.Frame(github_frame, bg="white")
        botoes_github.pack()
        
        tk.Button(
            botoes_github,
            text="⚙️ Configurar GitHub",
            font=("Arial", 10, "bold"),
            bg=COR_PRIMARIA,
            fg=COR_TEXTO_CLARO,
            command=self.configurar_github,
            cursor="hand2",
            relief=tk.FLAT,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            botoes_github,
            text="🔄 Sincronizar Agora",
            font=("Arial", 10),
            bg=COR_SUCESSO,
            fg=COR_TEXTO_CLARO,
            command=self.sincronizar_github_agora,
            cursor="hand2",
            relief=tk.FLAT,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT)
        
        # Botão voltar
        btn_voltar = tk.Button(
            container,
            text="← Voltar",
            font=("Arial", 10),
            bg=COR_PRIMARIA_CLARA,
            fg=COR_TEXTO_CLARO,
            command=self.voltar_callback,
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=10
        )
        btn_voltar.pack(pady=(20, 0))
        
        self.carregar_formas_pagamento()
    
    def carregar_configuracoes(self):
        """Carrega as configurações salvas"""
        config = self.db.obter_configuracao()
        if config:
            self.entry_nome_loja.insert(0, config.get('nome_loja', ''))
            self.entry_responsavel.insert(0, config.get('responsavel', ''))
    
    def salvar_configuracoes(self):
        """Salva as configurações da loja"""
        nome_loja = self.entry_nome_loja.get().strip()
        
        if not nome_loja:
            messagebox.showwarning("Atenção", "O nome da loja é obrigatório!")
            return
        
        responsavel = self.entry_responsavel.get().strip()
        
        self.db.salvar_configuracao(nome_loja, responsavel)
        messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
    
    def carregar_formas_pagamento(self):
        """Carrega a lista de formas de pagamento"""
        self.listbox_formas.delete(0, tk.END)
        formas = self.db.listar_formas_pagamento(apenas_ativas=False)
        
        for forma in formas:
            status = "✓" if forma['ativo'] else "✗"
            texto = f"{status} {forma['nome']}"
            self.listbox_formas.insert(tk.END, texto)
            
            # Armazena o ID como atributo do item
            self.listbox_formas.itemconfig(tk.END, fg="green" if forma['ativo'] else "red")
    
    def adicionar_forma_pagamento(self):
        """Adiciona uma nova forma de pagamento"""
        dialog = tk.Toplevel(self)
        dialog.title("Nova Forma de Pagamento")
        dialog.geometry("400x150")
        dialog.transient(self)
        dialog.grab_set()
        
        # Centralizar
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        frame = tk.Frame(dialog, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            frame,
            text="Nome da forma de pagamento:",
            font=("Arial", 10)
        ).pack(anchor=tk.W)
        
        entry_nome = tk.Entry(frame, font=("Arial", 10), width=30)
        entry_nome.pack(fill=tk.X, pady=(5, 15))
        entry_nome.focus()
        
        def salvar():
            nome = entry_nome.get().strip()
            if not nome:
                messagebox.showwarning("Atenção", "Digite um nome!", parent=dialog)
                return
            
            try:
                self.db.adicionar_forma_pagamento(nome)
                self.carregar_formas_pagamento()
                dialog.destroy()
                messagebox.showinfo("Sucesso", "Forma de pagamento adicionada!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao adicionar:\n{str(e)}", parent=dialog)
        
        botoes_frame = tk.Frame(frame)
        botoes_frame.pack()
        
        tk.Button(
            botoes_frame,
            text="Salvar",
            font=("Arial", 10),
            bg="#27ae60",
            fg="white",
            command=salvar,
            cursor="hand2",
            padx=20,
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
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        entry_nome.bind('<Return>', lambda e: salvar())
    
    def toggle_forma_pagamento(self, ativar: bool):
        """Ativa ou desativa uma forma de pagamento"""
        selecao = self.listbox_formas.curselection()
        if not selecao:
            messagebox.showwarning("Atenção", "Selecione uma forma de pagamento!")
            return
        
        indice = selecao[0]
        formas = self.db.listar_formas_pagamento(apenas_ativas=False)
        
        if indice < len(formas):
            forma = formas[indice]
            self.db.ativar_desativar_forma_pagamento(forma['id'], ativar)
            self.carregar_formas_pagamento()
            
            status = "ativada" if ativar else "desativada"
            messagebox.showinfo("Sucesso", f"Forma de pagamento {status}!")
    
    def alterar_senha_adm(self):
        """Abre o dialog para alterar a senha de administrador"""
        dialog = tk.Toplevel(self)
        dialog.title("Alterar Senha de Administrador")
        dialog.geometry("400x320")
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
            text="🔑 Alterar Senha de Administrador",
            font=("Arial", 12, "bold"),
            bg="white"
        ).pack(pady=(0, 20))
        
        # Senha atual
        tk.Label(frame, text="Senha Atual:", font=("Arial", 10), bg="white").pack(anchor=tk.W)
        entry_senha_atual = tk.Entry(frame, font=("Arial", 11), show="*", width=25)
        entry_senha_atual.pack(fill=tk.X, pady=(5, 15))
        entry_senha_atual.focus()
        
        # Nova senha
        tk.Label(frame, text="Nova Senha:", font=("Arial", 10), bg="white").pack(anchor=tk.W)
        entry_nova_senha = tk.Entry(frame, font=("Arial", 11), show="*", width=25)
        entry_nova_senha.pack(fill=tk.X, pady=(5, 15))
        
        # Confirmar nova senha
        tk.Label(frame, text="Confirmar Nova Senha:", font=("Arial", 10), bg="white").pack(anchor=tk.W)
        entry_confirmar = tk.Entry(frame, font=("Arial", 11), show="*", width=25)
        entry_confirmar.pack(fill=tk.X, pady=(5, 20))
        
        def salvar():
            senha_atual = entry_senha_atual.get()
            nova_senha = entry_nova_senha.get()
            confirmar = entry_confirmar.get()
            
            # Validar senha atual
            if not self.db.verificar_senha_adm(senha_atual):
                messagebox.showerror("Erro", "Senha atual incorreta!", parent=dialog)
                entry_senha_atual.delete(0, tk.END)
                entry_senha_atual.focus()
                return
            
            # Validar nova senha
            if len(nova_senha) < 4:
                messagebox.showerror("Erro", "A nova senha deve ter pelo menos 4 caracteres!", parent=dialog)
                return
            
            if nova_senha != confirmar:
                messagebox.showerror("Erro", "As senhas não coincidem!", parent=dialog)
                entry_confirmar.delete(0, tk.END)
                entry_confirmar.focus()
                return
            
            # Salvar nova senha
            self.db.alterar_senha_adm(nova_senha)
            dialog.destroy()
            messagebox.showinfo("Sucesso", "Senha de administrador alterada com sucesso!")
        
        botoes_frame = tk.Frame(frame, bg="white")
        botoes_frame.pack()
        
        tk.Button(
            botoes_frame,
            text="Salvar",
            font=("Arial", 10, "bold"),
            bg="#27ae60",
            fg="white",
            command=salvar,
            cursor="hand2",
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            botoes_frame,
            text="Cancelar",
            font=("Arial", 10),
            bg="#95a5a6",
            fg="white",
            command=dialog.destroy,
            cursor="hand2",
            padx=20,
            pady=8
        ).pack(side=tk.LEFT, padx=5)

    def configurar_github(self):
        """Abre o dialog para configurar o GitHub Pages"""
        dialog = tk.Toplevel(self)
        dialog.title("Configurar GitHub Pages")
        dialog.geometry("500x420")
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
            text="📱 Configurar Acesso Mobile",
            font=("Arial", 14, "bold"),
            bg="white"
        ).pack(pady=(0, 20))
        
        # Instruções
        tk.Label(
            frame,
            text="Configure para visualizar movimentações no celular via GitHub Pages.",
            font=("Arial", 9),
            bg="white",
            fg="#666",
            wraplength=400
        ).pack(pady=(0, 15))
        
        # Repositório
        tk.Label(frame, text="Repositório (usuario/repo):", font=("Arial", 10), bg="white").pack(anchor=tk.W)
        entry_repo = tk.Entry(frame, font=("Arial", 11), width=40)
        entry_repo.pack(fill=tk.X, pady=(5, 15))
        entry_repo.insert(0, self.github_sync.config.get('repo', ''))
        
        # Token
        tk.Label(frame, text="Token de Acesso Pessoal:", font=("Arial", 10), bg="white").pack(anchor=tk.W)
        entry_token = tk.Entry(frame, font=("Arial", 11), width=40, show="*")
        entry_token.pack(fill=tk.X, pady=(5, 5))
        if self.github_sync.config.get('token'):
            entry_token.insert(0, self.github_sync.config.get('token'))
        
        tk.Label(
            frame,
            text="Gere em: GitHub → Settings → Developer Settings → Personal Access Tokens",
            font=("Arial", 8),
            bg="white",
            fg="#888"
        ).pack(anchor=tk.W, pady=(0, 15))
        
        # Checkbox ativo
        ativo_var = tk.BooleanVar(value=self.github_sync.config.get('ativo', False))
        tk.Checkbutton(
            frame,
            text="Sincronização automática ativa",
            variable=ativo_var,
            font=("Arial", 10),
            bg="white"
        ).pack(anchor=tk.W, pady=(0, 15))
        
        # Status do teste
        self.label_teste_status = tk.Label(
            frame,
            text="",
            font=("Arial", 10),
            bg="white"
        )
        self.label_teste_status.pack(pady=(0, 10))
        
        def testar():
            repo = entry_repo.get().strip()
            token = entry_token.get().strip()
            
            if not repo or not token:
                self.label_teste_status.config(text="⚠️ Preencha todos os campos", fg="#e74c3c")
                return
            
            self.label_teste_status.config(text="🔄 Testando conexão...", fg="#3498db")
            dialog.update()
            
            # Salvar temporariamente para testar
            self.github_sync.salvar_config(token, repo, ativo_var.get())
            sucesso, mensagem = self.github_sync.testar_conexao()
            
            if sucesso:
                self.label_teste_status.config(text=f"✅ {mensagem}", fg="#27ae60")
            else:
                self.label_teste_status.config(text=f"❌ {mensagem}", fg="#e74c3c")
        
        def salvar():
            repo = entry_repo.get().strip()
            token = entry_token.get().strip()
            
            if ativo_var.get() and (not repo or not token):
                messagebox.showerror("Erro", "Preencha o repositório e o token!", parent=dialog)
                return
            
            self.github_sync.salvar_config(token, repo, ativo_var.get())
            
            # Atualizar status na tela principal
            status_text = "✅ Configurado" if self.github_sync.esta_configurado() else "❌ Não configurado"
            self.label_github_status.config(text=f"Status: {status_text}")
            
            dialog.destroy()
            messagebox.showinfo("Sucesso", "Configurações do GitHub salvas!")
        
        botoes_frame = tk.Frame(frame, bg="white")
        botoes_frame.pack(pady=(10, 0))
        
        tk.Button(
            botoes_frame,
            text="🔍 Testar Conexão",
            font=("Arial", 10),
            bg="#3498db",
            fg="white",
            command=testar,
            cursor="hand2",
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            botoes_frame,
            text="💾 Salvar",
            font=("Arial", 10, "bold"),
            bg="#27ae60",
            fg="white",
            command=salvar,
            cursor="hand2",
            padx=15,
            pady=8
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
            pady=8
        ).pack(side=tk.LEFT, padx=5)
    
    def sincronizar_github_agora(self):
        """Força sincronização imediata com GitHub"""
        if not self.github_sync.esta_configurado():
            messagebox.showwarning("Atenção", "Configure o GitHub primeiro!")
            return
        
        # Sincronizar em segundo plano com nova conexão do banco
        db_path = self.db.db_path
        
        def sync():
            try:
                from database import Database
                db_thread = Database(db_path)
                sucesso = sincronizar_agora(db_thread)
                db_thread.close()
                if sucesso:
                    messagebox.showinfo("Sucesso", "Movimentações sincronizadas com sucesso!\n\nAcesse no celular:\nhttps://SEU_USUARIO.github.io/SEU_REPO/")
                else:
                    messagebox.showerror("Erro", "Falha ao sincronizar. Verifique as configurações.")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao sincronizar:\n{str(e)}")
        
        messagebox.showinfo("Aguarde", "Sincronizando...")
        threading.Thread(target=sync, daemon=True).start()