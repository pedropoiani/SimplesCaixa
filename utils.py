#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo com funções utilitárias
"""

import os
import shutil
import csv
from datetime import datetime
from typing import List, Dict
from tkinter import filedialog, messagebox

# Importar tema
from tema import (
    COR_PRIMARIA, COR_SECUNDARIA, COR_SUCESSO,
    obter_logo_informativa, obter_logo_perfil, NOME_SISTEMA
)

# Tentar importar reportlab para PDF
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_DISPONIVEL = True
except ImportError:
    REPORTLAB_DISPONIVEL = False

def fazer_backup(db_path: str) -> bool:
    """Faz backup do banco de dados"""
    try:
        home_dir = os.path.expanduser("~")
        backup_dir = os.path.join(home_dir, ".pdvmf", "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"pdvmf_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        shutil.copy2(db_path, backup_path)
        
        messagebox.showinfo("Backup", 
                           f"Backup realizado com sucesso!\n\nLocal: {backup_path}")
        return True
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao fazer backup:\n{str(e)}")
        return False

def fazer_backup_silencioso(db_path: str) -> bool:
    """Faz backup do banco de dados sem exibir mensagem (para uso automático)"""
    try:
        home_dir = os.path.expanduser("~")
        backup_dir = os.path.join(home_dir, ".pdvmf", "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"pdvmf_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        shutil.copy2(db_path, backup_path)
        
        # Limpar backups antigos (manter apenas os últimos 30)
        backups = sorted([f for f in os.listdir(backup_dir) if f.endswith('.db')])
        if len(backups) > 30:
            for old_backup in backups[:-30]:
                try:
                    os.remove(os.path.join(backup_dir, old_backup))
                except:
                    pass
        
        return True
    except Exception as e:
        return False

def restaurar_backup() -> str:
    """Restaura um backup do banco de dados"""
    try:
        home_dir = os.path.expanduser("~")
        backup_dir = os.path.join(home_dir, ".pdvmf", "backups")
        
        filename = filedialog.askopenfilename(
            title="Selecione o backup para restaurar",
            initialdir=backup_dir,
            filetypes=[("Database files", "*.db"), ("All files", "*.*")]
        )
        
        if not filename:
            return None
        
        resposta = messagebox.askyesno(
            "Confirmar Restauração",
            "Tem certeza que deseja restaurar este backup?\n\n"
            "O banco de dados atual será substituído e o aplicativo será reiniciado."
        )
        
        if resposta:
            return filename
        
        return None
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao restaurar backup:\n{str(e)}")
        return None

def exportar_para_csv(dados: List[Dict], colunas: List[str], nome_arquivo: str = None) -> bool:
    """Exporta dados para arquivo CSV"""
    try:
        if nome_arquivo is None:
            home_dir = os.path.expanduser("~")
            downloads_dir = os.path.join(home_dir, "Downloads")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = filedialog.asksaveasfilename(
                title="Salvar CSV",
                initialdir=downloads_dir,
                initialfile=f"relatorio_pdv_{timestamp}.csv",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
        
        if not nome_arquivo:
            return False
        
        with open(nome_arquivo, 'w', newline='', encoding='utf-8') as arquivo:
            writer = csv.DictWriter(arquivo, fieldnames=colunas, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(dados)
        
        messagebox.showinfo("Exportação", 
                           f"Dados exportados com sucesso!\n\nLocal: {nome_arquivo}")
        return True
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao exportar para CSV:\n{str(e)}")
        return False

def exportar_para_pdf(dados: List[Dict], colunas: List[str], titulo: str = "Relatório", 
                      nome_arquivo: str = None, resumo: Dict = None) -> bool:
    """Exporta dados para arquivo PDF"""
    if not REPORTLAB_DISPONIVEL:
        messagebox.showerror("Erro", 
            "Biblioteca 'reportlab' não está instalada.\n\n"
            "Para instalar, execute no terminal:\n"
            "pip install reportlab")
        return False
    
    try:
        if nome_arquivo is None:
            home_dir = os.path.expanduser("~")
            downloads_dir = os.path.join(home_dir, "Downloads")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = filedialog.asksaveasfilename(
                title="Salvar PDF",
                initialdir=downloads_dir,
                initialfile=f"relatorio_pdv_{timestamp}.pdf",
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )
        
        if not nome_arquivo:
            return False
        
        # Criar documento PDF
        doc = SimpleDocTemplate(
            nome_arquivo, 
            pagesize=A4,
            rightMargin=15*mm,
            leftMargin=15*mm,
            topMargin=15*mm,
            bottomMargin=15*mm
        )
        
        elementos = []
        styles = getSampleStyleSheet()
        
        # Adicionar logo no cabeçalho
        try:
            logo_path = obter_logo_informativa()
            if os.path.exists(logo_path):
                logo = Image(logo_path, width=40*mm, height=40*mm)
                logo.hAlign = 'CENTER'
                elementos.append(logo)
                elementos.append(Spacer(1, 5*mm))
        except:
            pass
        
        # Estilo do título com cor da loja MF
        estilo_titulo = ParagraphStyle(
            'TituloRelatorio',
            parent=styles['Heading1'],
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=10*mm,
            textColor=colors.HexColor(COR_PRIMARIA)
        )
        
        # Estilo do subtítulo
        estilo_subtitulo = ParagraphStyle(
            'Subtitulo',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.grey,
            spaceAfter=5*mm
        )
        
        # Título
        elementos.append(Paragraph(titulo, estilo_titulo))
        
        # Data/hora do relatório
        data_relatorio = datetime.now().strftime("%d/%m/%Y às %H:%M")
        elementos.append(Paragraph(f"Gerado em: {data_relatorio}", estilo_subtitulo))
        
        # Resumo (se fornecido)
        if resumo:
            estilo_resumo = ParagraphStyle(
                'Resumo',
                parent=styles['Normal'],
                fontSize=11,
                alignment=TA_CENTER,
                spaceAfter=8*mm,
                textColor=colors.HexColor(COR_PRIMARIA)
            )
            texto_resumo = " | ".join([f"{k}: {v}" for k, v in resumo.items()])
            elementos.append(Paragraph(texto_resumo, estilo_resumo))
        
        elementos.append(Spacer(1, 5*mm))
        
        # Preparar dados da tabela
        dados_tabela = [colunas]  # Cabeçalho
        
        for item in dados:
            linha = []
            for col in colunas:
                valor = item.get(col, '')
                # Truncar textos muito longos
                if isinstance(valor, str) and len(valor) > 30:
                    valor = valor[:27] + "..."
                linha.append(str(valor) if valor else '')
            dados_tabela.append(linha)
        
        # Calcular larguras das colunas proporcionalmente
        largura_disponivel = A4[0] - 30*mm
        num_colunas = len(colunas)
        largura_coluna = largura_disponivel / num_colunas
        larguras = [largura_coluna] * num_colunas
        
        # Criar tabela
        tabela = Table(dados_tabela, colWidths=larguras, repeatRows=1)
        
        # Estilo da tabela com cores da loja MF
        estilo_tabela = TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COR_PRIMARIA)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            
            # Corpo
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
            ('TOPPADDING', (0, 1), (-1, -1), 5),
            
            # Bordas
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            
            # Cores alternadas nas linhas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ])
        
        tabela.setStyle(estilo_tabela)
        elementos.append(tabela)
        
        # Rodapé
        elementos.append(Spacer(1, 10*mm))
        estilo_rodape = ParagraphStyle(
            'Rodape',
            parent=styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.HexColor(COR_PRIMARIA)
        )
        elementos.append(Paragraph(f"{NOME_SISTEMA} - Sistema de Ponto de Venda", estilo_rodape))
        
        # Gerar PDF
        doc.build(elementos)
        
        messagebox.showinfo("Exportação", 
                           f"PDF exportado com sucesso!\n\nLocal: {nome_arquivo}")
        return True
        
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao exportar para PDF:\n{str(e)}")
        return False

def exportar_relatorio_caixa_pdf(dados_fechamento: Dict, nome_arquivo: str = None) -> bool:
    """Exporta relatório de fechamento de caixa para PDF"""
    if not REPORTLAB_DISPONIVEL:
        messagebox.showerror("Erro", 
            "Biblioteca 'reportlab' não está instalada.\n\n"
            "Para instalar, execute no terminal:\n"
            "pip install reportlab")
        return False
    
    try:
        caixa = dados_fechamento['caixa']
        
        if nome_arquivo is None:
            home_dir = os.path.expanduser("~")
            downloads_dir = os.path.join(home_dir, "Downloads")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = filedialog.asksaveasfilename(
                title="Salvar Relatório PDF",
                initialdir=downloads_dir,
                initialfile=f"fechamento_caixa_{timestamp}.pdf",
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
            )
        
        if not nome_arquivo:
            return False
        
        # Criar documento PDF
        doc = SimpleDocTemplate(
            nome_arquivo, 
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        elementos = []
        styles = getSampleStyleSheet()
        
        # Adicionar logo no cabeçalho
        try:
            logo_path = obter_logo_informativa()
            if os.path.exists(logo_path):
                logo = Image(logo_path, width=35*mm, height=35*mm)
                logo.hAlign = 'CENTER'
                elementos.append(logo)
                elementos.append(Spacer(1, 3*mm))
        except:
            pass
        
        # Estilos personalizados com cores da loja MF
        estilo_titulo = ParagraphStyle(
            'TituloRelatorio',
            parent=styles['Heading1'],
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=5*mm,
            textColor=colors.HexColor(COR_PRIMARIA)
        )
        
        estilo_secao = ParagraphStyle(
            'Secao',
            parent=styles['Heading2'],
            fontSize=12,
            alignment=TA_LEFT,
            spaceBefore=8*mm,
            spaceAfter=3*mm,
            textColor=colors.HexColor(COR_PRIMARIA)
        )
        
        estilo_normal = ParagraphStyle(
            'NormalCustom',
            parent=styles['Normal'],
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=2*mm
        )
        
        # Título
        elementos.append(Paragraph("RELATÓRIO DE FECHAMENTO DE CAIXA", estilo_titulo))
        
        # Info do caixa
        elementos.append(Paragraph("INFORMAÇÕES GERAIS", estilo_secao))
        
        info_data = [
            ["Operador:", caixa.get('operador', 'N/A')],
            ["Data Abertura:", formatar_data(caixa['data_abertura'])],
        ]
        if caixa.get('data_fechamento'):
            info_data.append(["Data Fechamento:", formatar_data(caixa['data_fechamento'])])
        info_data.append(["Status:", "Aberto" if caixa.get('status') == 'aberto' else "Fechado"])
        
        tabela_info = Table(info_data, colWidths=[50*mm, 100*mm])
        tabela_info.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
        ]))
        elementos.append(tabela_info)
        
        # Resumo Financeiro
        elementos.append(Paragraph("RESUMO FINANCEIRO", estilo_secao))
        
        financeiro_data = [
            ["Troco Inicial:", formatar_moeda(caixa['troco_inicial'])],
            ["Total Entradas:", formatar_moeda(caixa.get('total_entradas', 0))],
            ["Total Saídas:", formatar_moeda(caixa.get('total_saidas', 0))],
            ["Saldo Final:", formatar_moeda(caixa.get('saldo_final', 0))],
        ]
        
        if caixa.get('valor_contado') is not None:
            financeiro_data.append(["Valor Contado:", formatar_moeda(caixa['valor_contado'])])
            diferenca = caixa.get('diferenca', 0)
            sinal = "+" if diferenca > 0 else ""
            financeiro_data.append(["Diferença:", f"{sinal}{formatar_moeda(diferenca)}"])
        
        tabela_financeiro = Table(financeiro_data, colWidths=[50*mm, 50*mm])
        tabela_financeiro.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor(COR_SUCESSO + '33')),  # Saldo final
        ]))
        elementos.append(tabela_financeiro)
        
        # Por forma de pagamento
        if dados_fechamento.get('por_forma_pagamento'):
            elementos.append(Paragraph("POR FORMA DE PAGAMENTO", estilo_secao))
            
            forma_data = [["Forma de Pagamento", "Total"]]
            for forma in dados_fechamento['por_forma_pagamento']:
                forma_data.append([forma['nome'], formatar_moeda(forma['total'])])
            
            tabela_forma = Table(forma_data, colWidths=[80*mm, 50*mm])
            tabela_forma.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COR_PRIMARIA)),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
            ]))
            elementos.append(tabela_forma)
        
        # Por categoria
        if dados_fechamento.get('por_categoria'):
            elementos.append(Paragraph("POR CATEGORIA", estilo_secao))
            
            cat_data = [["Tipo", "Categoria", "Total"]]
            for cat in dados_fechamento['por_categoria']:
                cat_data.append([cat['tipo'], cat['categoria'], formatar_moeda(cat['total'])])
            
            tabela_cat = Table(cat_data, colWidths=[40*mm, 70*mm, 50*mm])
            tabela_cat.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COR_SUCESSO)),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
            ]))
            elementos.append(tabela_cat)
        
        # Observações
        if caixa.get('observacoes'):
            elementos.append(Paragraph("OBSERVAÇÕES", estilo_secao))
            elementos.append(Paragraph(caixa['observacoes'], estilo_normal))
        
        # Rodapé
        elementos.append(Spacer(1, 15*mm))
        estilo_rodape = ParagraphStyle(
            'Rodape',
            parent=styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.HexColor(COR_PRIMARIA)
        )
        data_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
        elementos.append(Paragraph(f"Relatório gerado em {data_geracao} - {NOME_SISTEMA}", estilo_rodape))
        
        # Gerar PDF
        doc.build(elementos)
        
        messagebox.showinfo("Exportação", 
                           f"Relatório PDF exportado com sucesso!\n\nLocal: {nome_arquivo}")
        return True
        
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao exportar relatório PDF:\n{str(e)}")
        return False

def formatar_moeda(valor: float) -> str:
    """Formata um valor como moeda brasileira"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def formatar_data(data_str: str) -> str:
    """Formata uma data do formato ISO para formato brasileiro"""
    try:
        if not data_str:
            return ""
        
        # Tenta parsear diferentes formatos
        if "T" in data_str:
            dt = datetime.fromisoformat(data_str.replace("Z", "+00:00"))
        else:
            dt = datetime.strptime(data_str, "%Y-%m-%d %H:%M:%S")
        
        return dt.strftime("%d/%m/%Y %H:%M:%S")
    except:
        return data_str

def formatar_data_curta(data_str: str) -> str:
    """Formata uma data do formato ISO para formato brasileiro curto"""
    try:
        if not data_str:
            return ""
        
        if "T" in data_str:
            dt = datetime.fromisoformat(data_str.replace("Z", "+00:00"))
        else:
            dt = datetime.strptime(data_str, "%Y-%m-%d %H:%M:%S")
        
        return dt.strftime("%d/%m/%Y")
    except:
        return data_str

def converter_data_br_para_sql(data_br: str) -> str:
    """Converte data do formato brasileiro (DD/MM/YYYY) para SQL (YYYY-MM-DD)"""
    try:
        if not data_br or not data_br.strip():
            return None
        
        # Remove espaços
        data_br = data_br.strip()
        
        # Tenta parsear formato brasileiro
        dt = datetime.strptime(data_br, "%d/%m/%Y")
        return dt.strftime("%Y-%m-%d")
    except:
        # Se falhar, retorna None
        return None

def validar_valor(valor_str: str) -> tuple:
    """Valida um valor monetário digitado"""
    try:
        # Remove espaços e substitui vírgula por ponto
        valor_str = valor_str.strip().replace(",", ".")
        
        # Remove "R$" se presente
        valor_str = valor_str.replace("R$", "").strip()
        
        valor = float(valor_str)
        
        if valor < 0:
            return False, "O valor não pode ser negativo"
        
        return True, valor
    except ValueError:
        return False, "Valor inválido"

def calcular_troco(valor_recebido: float, valor_compra: float) -> float:
    """Calcula o troco"""
    return valor_recebido - valor_compra

def obter_data_atual() -> str:
    """Retorna a data atual no formato brasileiro"""
    return datetime.now().strftime("%d/%m/%Y")

def obter_hora_atual() -> str:
    """Retorna a hora atual"""
    return datetime.now().strftime("%H:%M:%S")

def obter_data_hora_atual() -> str:
    """Retorna data e hora atual"""
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

def gerar_relatorio_texto(dados_fechamento: Dict) -> str:
    """Gera um relatório em formato texto do fechamento"""
    caixa = dados_fechamento['caixa']
    
    relatorio = "=" * 60 + "\n"
    relatorio += "RELATÓRIO DE FECHAMENTO DE CAIXA\n"
    relatorio += "=" * 60 + "\n\n"
    
    relatorio += f"Operador: {caixa.get('operador', 'N/A')}\n"
    relatorio += f"Data Abertura: {formatar_data(caixa['data_abertura'])}\n"
    
    if caixa.get('data_fechamento'):
        relatorio += f"Data Fechamento: {formatar_data(caixa['data_fechamento'])}\n"
    
    relatorio += "\n" + "-" * 60 + "\n"
    relatorio += "RESUMO FINANCEIRO\n"
    relatorio += "-" * 60 + "\n\n"
    
    relatorio += f"Troco Inicial:      {formatar_moeda(caixa['troco_inicial'])}\n"
    relatorio += f"Total Entradas:     {formatar_moeda(caixa.get('total_entradas', 0))}\n"
    relatorio += f"Total Saídas:       {formatar_moeda(caixa.get('total_saidas', 0))}\n"
    relatorio += f"Saldo Final:        {formatar_moeda(caixa.get('saldo_final', 0))}\n"
    
    if caixa.get('valor_contado') is not None:
        relatorio += f"\nValor Contado:      {formatar_moeda(caixa['valor_contado'])}\n"
        diferenca = caixa.get('diferenca', 0)
        sinal = "+" if diferenca > 0 else ""
        relatorio += f"Diferença:          {sinal}{formatar_moeda(diferenca)}\n"
    
    # Totais por forma de pagamento
    if dados_fechamento.get('por_forma_pagamento'):
        relatorio += "\n" + "-" * 60 + "\n"
        relatorio += "POR FORMA DE PAGAMENTO\n"
        relatorio += "-" * 60 + "\n\n"
        
        for forma in dados_fechamento['por_forma_pagamento']:
            relatorio += f"{forma['nome']:20s} {formatar_moeda(forma['total']):>20s}\n"
    
    # Totais por categoria
    if dados_fechamento.get('por_categoria'):
        relatorio += "\n" + "-" * 60 + "\n"
        relatorio += "POR CATEGORIA\n"
        relatorio += "-" * 60 + "\n\n"
        
        for cat in dados_fechamento['por_categoria']:
            relatorio += f"{cat['tipo']:10s} - {cat['categoria']:20s} {formatar_moeda(cat['total']):>15s}\n"
    
    if caixa.get('observacoes'):
        relatorio += "\n" + "-" * 60 + "\n"
        relatorio += "OBSERVAÇÕES\n"
        relatorio += "-" * 60 + "\n\n"
        relatorio += caixa['observacoes'] + "\n"
    
    relatorio += "\n" + "=" * 60 + "\n"
    
    return relatorio

def salvar_relatorio_texto(conteudo: str, nome_arquivo: str = None) -> bool:
    """Salva um relatório em arquivo de texto"""
    try:
        if nome_arquivo is None:
            home_dir = os.path.expanduser("~")
            downloads_dir = os.path.join(home_dir, "Downloads")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = filedialog.asksaveasfilename(
                title="Salvar Relatório",
                initialdir=downloads_dir,
                initialfile=f"relatorio_fechamento_{timestamp}.txt",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
        
        if not nome_arquivo:
            return False
        
        with open(nome_arquivo, 'w', encoding='utf-8') as arquivo:
            arquivo.write(conteudo)
        
        messagebox.showinfo("Relatório", 
                           f"Relatório salvo com sucesso!\n\nLocal: {nome_arquivo}")
        return True
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar relatório:\n{str(e)}")
        return False
