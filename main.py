#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema PDV-MF - Ponto de Venda com Controle de Caixa
Aplicação principal
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

from database import Database
from view_configuracao import ConfiguracaoView
from view_caixa import AberturaView, FechamentoView
from view_principal import PrincipalView
from view_historico import HistoricoView
from tema import obter_logo_perfil, NOME_SISTEMA, SUBTITULO_SISTEMA, COR_FUNDO
try:
    from PIL import Image, ImageTk
    PIL_DISPONIVEL = True
except ImportError:
    PIL_DISPONIVEL = False

class PDVApp(tk.Tk):
    """Classe principal da aplicação"""
    
    def __init__(self):
        super().__init__()
        
        # Configurações da janela
        self.title(f"{NOME_SISTEMA} - {SUBTITULO_SISTEMA}")
        self.geometry("1200x700")
        self.minsize(1000, 600)
        
        # Centralizar janela
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        
        # Configurar ícone da janela com logo da loja MF
        if PIL_DISPONIVEL:
            try:
                logo_path = obter_logo_perfil()
                if os.path.exists(logo_path):
                    img = Image.open(logo_path)
                    img = img.resize((64, 64), Image.Resampling.LANCZOS)
                    icon = ImageTk.PhotoImage(img)
                    self.iconphoto(True, icon)
                    self._icon_img = icon  # Manter referência
            except Exception as e:
                pass
        
        # Inicializar banco de dados
        self.db = Database()
        
        # Variável para armazenar o caixa atual
        self.caixa_atual_id = None
        
        # Container para as views
        self.container = tk.Frame(self, bg=COR_FUNDO)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # Frame atual
        self.frame_atual = None
        
        # Verificar se há caixa aberto
        self.verificar_caixa_aberto()
        
        # Handler de fechamento da janela
        self.protocol("WM_DELETE_WINDOW", self.fechar_aplicacao)
    
    def verificar_caixa_aberto(self):
        """Verifica se há um caixa aberto"""
        caixa = self.db.obter_caixa_aberto()
        
        if caixa:
            self.caixa_atual_id = caixa['id']
            self.mostrar_principal()
        else:
            # Verificar se já tem configuração
            config = self.db.obter_configuracao()
            if not config:
                # Primeira execução - mostrar configuração
                resposta = messagebox.askyesno(
                    "Bem-vindo!",
                    "Parece ser a primeira vez que você usa o sistema.\n\n"
                    "Deseja configurar os dados da loja agora?"
                )
                if resposta:
                    self.mostrar_configuracao()
                else:
                    self.mostrar_abertura()
            else:
                self.mostrar_abertura()
    
    def limpar_frame(self):
        """Limpa o frame atual"""
        if self.frame_atual:
            self.frame_atual.destroy()
            self.frame_atual = None
    
    def mostrar_abertura(self):
        """Mostra a tela de abertura de caixa"""
        self.limpar_frame()
        self.frame_atual = AberturaView(
            self.container,
            self.db,
            self.fechar_aplicacao,
            self.caixa_aberto,
            self.mostrar_historico
        )
        self.frame_atual.pack(fill=tk.BOTH, expand=True)
    
    def mostrar_principal(self):
        """Mostra a tela principal com o caixa aberto"""
        self.limpar_frame()
        self.frame_atual = PrincipalView(
            self.container,
            self.db,
            self.caixa_atual_id,
            self.mostrar_fechamento,
            self.mostrar_historico,
            self.mostrar_configuracao
        )
        self.frame_atual.pack(fill=tk.BOTH, expand=True)
    
    def mostrar_fechamento(self):
        """Mostra a tela de fechamento de caixa"""
        self.limpar_frame()
        self.frame_atual = FechamentoView(
            self.container,
            self.db,
            self.caixa_atual_id,
            self.caixa_fechado
        )
        self.frame_atual.pack(fill=tk.BOTH, expand=True)
    
    def mostrar_configuracao(self):
        """Mostra a tela de configurações"""
        self.limpar_frame()
        self.frame_atual = ConfiguracaoView(
            self.container,
            self.db,
            self.voltar_principal_ou_abertura
        )
        self.frame_atual.pack(fill=tk.BOTH, expand=True)
    
    def mostrar_historico(self):
        """Mostra a tela de histórico"""
        self.limpar_frame()
        self.frame_atual = HistoricoView(
            self.container,
            self.db,
            self.voltar_principal_ou_abertura
        )
        self.frame_atual.pack(fill=tk.BOTH, expand=True)
    
    def caixa_aberto(self, caixa_id: int):
        """Callback quando o caixa é aberto"""
        self.caixa_atual_id = caixa_id
        self.mostrar_principal()
    
    def caixa_fechado(self):
        """Callback quando o caixa é fechado"""
        self.caixa_atual_id = None
        self.mostrar_abertura()
    
    def voltar_principal_ou_abertura(self):
        """Volta para a tela principal ou abertura"""
        if self.caixa_atual_id:
            self.mostrar_principal()
        else:
            self.mostrar_abertura()
    
    def fechar_aplicacao(self):
        """Fecha a aplicação"""
        # Verificar se há caixa aberto
        if self.caixa_atual_id:
            resposta = messagebox.askyesno(
                "Atenção",
                "Há um caixa aberto!\n\n"
                "Tem certeza que deseja sair sem fechar o caixa?\n"
                "(Você poderá continuar quando abrir o sistema novamente)"
            )
            if not resposta:
                return
        
        # Fechar banco de dados
        self.db.close()
        
        # Fechar aplicação
        self.quit()
        self.destroy()

def main():
    """Função principal"""
    try:
        app = PDVApp()
        app.mainloop()
    except Exception as e:
        messagebox.showerror("Erro Fatal", f"Erro ao iniciar a aplicação:\n\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
