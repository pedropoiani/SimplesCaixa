"""
Módulo de Geração de Relatórios em PDF
"""
from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT


def formatar_moeda(valor):
    """Formata valor para moeda brasileira"""
    return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')


def formatar_data(data_str):
    """Formata data ISO para formato brasileiro"""
    if not data_str:
        return '-'
    try:
        dt = datetime.fromisoformat(data_str.replace('Z', '+00:00'))
        return dt.strftime('%d/%m/%Y %H:%M')
    except:
        return data_str


def gerar_relatorio_caixa_pdf(caixa_data, lancamentos, nome_loja='Minha Loja'):
    """
    Gera PDF com relatório completo de um caixa específico
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    styles = getSampleStyleSheet()
    
    # Estilos customizados
    titulo_style = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=20,
        textColor=colors.HexColor('#1a5fb4')
    )
    
    subtitulo_style = ParagraphStyle(
        'Subtitulo',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=10,
        textColor=colors.HexColor('#333333')
    )
    
    info_style = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.grey
    )
    
    elements = []
    
    # Cabeçalho
    elements.append(Paragraph(f"📋 {nome_loja}", titulo_style))
    elements.append(Paragraph("RELATÓRIO DE CAIXA", subtitulo_style))
    elements.append(Paragraph(
        f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
        info_style
    ))
    elements.append(Spacer(1, 20))
    
    # Informações do Caixa
    elements.append(Paragraph("📊 Informações do Caixa", subtitulo_style))
    
    info_caixa = [
        ['Campo', 'Valor'],
        ['ID do Caixa', str(caixa_data.get('id', '-'))],
        ['Operador', caixa_data.get('operador', '-') or '-'],
        ['Data Abertura', formatar_data(caixa_data.get('data_abertura'))],
        ['Data Fechamento', formatar_data(caixa_data.get('data_fechamento'))],
        ['Status', caixa_data.get('status', '-').upper()],
        ['Troco Inicial', formatar_moeda(caixa_data.get('troco_inicial', 0))],
    ]
    
    tabela_info = Table(info_caixa, colWidths=[200, 250])
    tabela_info.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5fb4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
    ]))
    elements.append(tabela_info)
    elements.append(Spacer(1, 20))
    
    # Resumo Financeiro
    elements.append(Paragraph("💰 Resumo Financeiro", subtitulo_style))
    
    total_entradas = caixa_data.get('total_entradas', 0)
    total_saidas = caixa_data.get('total_saidas', 0)
    saldo = caixa_data.get('saldo_atual', 0)
    diferenca = caixa_data.get('diferenca')
    
    resumo_data = [
        ['Descrição', 'Valor'],
        ['Total de Entradas', formatar_moeda(total_entradas)],
        ['Total de Saídas', formatar_moeda(total_saidas)],
        ['Saldo Final', formatar_moeda(saldo)],
    ]
    
    if caixa_data.get('valor_contado') is not None:
        resumo_data.append(['Valor Contado', formatar_moeda(caixa_data.get('valor_contado', 0))])
    
    if diferenca is not None:
        status_diferenca = "✅ Conferido" if abs(diferenca) < 0.01 else (
            f"⬆️ Sobra: {formatar_moeda(diferenca)}" if diferenca > 0 
            else f"⬇️ Falta: {formatar_moeda(abs(diferenca))}"
        )
        resumo_data.append(['Diferença', status_diferenca])
    
    tabela_resumo = Table(resumo_data, colWidths=[200, 250])
    tabela_resumo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#26a269')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e8f5e9')]),
    ]))
    elements.append(tabela_resumo)
    elements.append(Spacer(1, 20))
    
    # Lista de Lançamentos
    if lancamentos:
        elements.append(Paragraph("📝 Lançamentos", subtitulo_style))
        
        lanc_data = [['Hora', 'Tipo', 'Categoria', 'Descrição', 'Valor']]
        
        for lanc in lancamentos:
            hora = ''
            try:
                dt = datetime.fromisoformat(lanc.get('data_hora', '').replace('Z', '+00:00'))
                hora = dt.strftime('%H:%M')
            except:
                hora = '-'
            
            tipo_emoji = '⬆️' if lanc.get('tipo') == 'entrada' else '⬇️'
            valor = lanc.get('valor', 0)
            valor_str = formatar_moeda(valor)
            if lanc.get('tipo') == 'saida':
                valor_str = f"-{valor_str}"
            
            descricao = lanc.get('descricao') or lanc.get('forma_pagamento') or '-'
            if len(descricao) > 30:
                descricao = descricao[:27] + '...'
            
            lanc_data.append([
                hora,
                f"{tipo_emoji} {lanc.get('tipo', '-')}",
                lanc.get('categoria', '-'),
                descricao,
                valor_str
            ])
        
        tabela_lanc = Table(lanc_data, colWidths=[50, 70, 80, 150, 100])
        tabela_lanc.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#5c6bc0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (4, 1), (4, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(tabela_lanc)
    
    # Rodapé
    elements.append(Spacer(1, 30))
    elements.append(Paragraph(
        f"Sistema PDV - {nome_loja} - {datetime.now().year}",
        info_style
    ))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def gerar_relatorio_periodo_pdf(dados_relatorio, nome_loja='Minha Loja'):
    """
    Gera PDF com relatório de um período
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    styles = getSampleStyleSheet()
    
    titulo_style = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=20,
        textColor=colors.HexColor('#1a5fb4')
    )
    
    subtitulo_style = ParagraphStyle(
        'Subtitulo',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=10,
        textColor=colors.HexColor('#333333')
    )
    
    info_style = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.grey
    )
    
    elements = []
    
    # Cabeçalho
    elements.append(Paragraph(f"📊 {nome_loja}", titulo_style))
    elements.append(Paragraph("RELATÓRIO POR PERÍODO", subtitulo_style))
    
    periodo = dados_relatorio.get('periodo', {})
    elements.append(Paragraph(
        f"Período: {formatar_data(periodo.get('inicio'))} a {formatar_data(periodo.get('fim'))}",
        info_style
    ))
    elements.append(Paragraph(
        f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
        info_style
    ))
    elements.append(Spacer(1, 20))
    
    # Resumo Geral
    elements.append(Paragraph("💰 Resumo Geral", subtitulo_style))
    
    totais = dados_relatorio.get('totais', {})
    resumo_data = [
        ['Descrição', 'Valor'],
        ['Total de Entradas', formatar_moeda(totais.get('entradas', 0))],
        ['Total de Saídas', formatar_moeda(totais.get('saidas', 0))],
        ['Saldo do Período', formatar_moeda(totais.get('saldo', 0))],
    ]
    
    tabela_resumo = Table(resumo_data, colWidths=[200, 250])
    tabela_resumo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#26a269')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e8f5e9')]),
    ]))
    elements.append(tabela_resumo)
    elements.append(Spacer(1, 20))
    
    # Por Categoria
    categorias = dados_relatorio.get('categorias', [])
    if categorias:
        elements.append(Paragraph("📋 Por Categoria", subtitulo_style))
        
        cat_data = [['Categoria', 'Tipo', 'Total']]
        for cat in categorias:
            tipo_emoji = '⬆️' if cat.get('tipo') == 'entrada' else '⬇️'
            cat_data.append([
                cat.get('categoria', '-').capitalize(),
                f"{tipo_emoji} {cat.get('tipo', '-')}",
                formatar_moeda(cat.get('total', 0))
            ])
        
        tabela_cat = Table(cat_data, colWidths=[150, 150, 150])
        tabela_cat.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#5c6bc0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ]))
        elements.append(tabela_cat)
        elements.append(Spacer(1, 20))
    
    # Por Forma de Pagamento
    pagamentos = dados_relatorio.get('pagamentos', [])
    if pagamentos:
        elements.append(Paragraph("💳 Vendas por Forma de Pagamento", subtitulo_style))
        
        pag_data = [['Forma de Pagamento', 'Total']]
        for pag in pagamentos:
            pag_data.append([
                pag.get('forma', '-'),
                formatar_moeda(pag.get('total', 0))
            ])
        
        tabela_pag = Table(pag_data, colWidths=[250, 200])
        tabela_pag.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff7043')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#fff3e0')]),
        ]))
        elements.append(tabela_pag)
    
    # Rodapé
    elements.append(Spacer(1, 30))
    elements.append(Paragraph(
        f"Sistema PDV - {nome_loja} - {datetime.now().year}",
        info_style
    ))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer


def gerar_resumo_diario_pdf(data_resumo, nome_loja='Minha Loja'):
    """
    Gera PDF com resumo diário
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    styles = getSampleStyleSheet()
    
    titulo_style = ParagraphStyle(
        'Titulo',
        parent=styles['Heading1'],
        fontSize=20,
        alignment=TA_CENTER,
        spaceAfter=20,
        textColor=colors.HexColor('#1a5fb4')
    )
    
    subtitulo_style = ParagraphStyle(
        'Subtitulo',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=10,
        textColor=colors.HexColor('#333333')
    )
    
    destaque_style = ParagraphStyle(
        'Destaque',
        parent=styles['Normal'],
        fontSize=24,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#26a269'),
        fontName='Helvetica-Bold'
    )
    
    info_style = ParagraphStyle(
        'Info',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=colors.grey
    )
    
    elements = []
    
    # Cabeçalho
    data_str = data_resumo.get('data', datetime.now().strftime('%Y-%m-%d'))
    try:
        data_formatada = datetime.strptime(data_str, '%Y-%m-%d').strftime('%d/%m/%Y')
    except:
        data_formatada = data_str
    
    elements.append(Paragraph(f"📊 {nome_loja}", titulo_style))
    elements.append(Paragraph(f"RESUMO DO DIA - {data_formatada}", subtitulo_style))
    elements.append(Spacer(1, 20))
    
    # Total de Vendas em Destaque
    total_vendas = data_resumo.get('total_vendas', 0)
    elements.append(Paragraph("💰 TOTAL DE VENDAS", subtitulo_style))
    elements.append(Paragraph(formatar_moeda(total_vendas), destaque_style))
    elements.append(Spacer(1, 20))
    
    # Vendas por forma de pagamento
    vendas = data_resumo.get('vendas', {})
    if vendas:
        elements.append(Paragraph("💳 Por Forma de Pagamento", subtitulo_style))
        
        vendas_data = [['Forma', 'Valor']]
        for forma, valor in vendas.items():
            if valor > 0:
                vendas_data.append([forma.replace('_', ' ').title(), formatar_moeda(valor)])
        
        if len(vendas_data) > 1:
            tabela_vendas = Table(vendas_data, colWidths=[200, 200])
            tabela_vendas.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#26a269')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('TOPPADDING', (0, 0), (-1, 0), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e8f5e9')]),
            ]))
            elements.append(tabela_vendas)
    
    elements.append(Spacer(1, 20))
    
    # Movimentações
    movimentacoes = data_resumo.get('movimentacoes', {})
    elements.append(Paragraph("📋 Movimentações", subtitulo_style))
    
    mov_data = [
        ['Descrição', 'Valor'],
        ['Sangrias', formatar_moeda(movimentacoes.get('sangrias', 0))],
        ['Suprimentos', formatar_moeda(movimentacoes.get('suprimentos', 0))],
    ]
    
    tabela_mov = Table(mov_data, colWidths=[200, 200])
    tabela_mov.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff7043')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(tabela_mov)
    
    # Rodapé
    elements.append(Spacer(1, 40))
    elements.append(Paragraph(
        f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
        info_style
    ))
    elements.append(Paragraph(
        f"Sistema PDV - {nome_loja}",
        info_style
    ))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
