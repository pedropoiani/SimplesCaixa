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
    
    # Totais por Forma de Pagamento (apenas vendas)
    vendas_por_forma = {}
    for lanc in lancamentos:
        if lanc.get('categoria') == 'venda' and lanc.get('tipo') == 'entrada':
            forma = lanc.get('forma_pagamento') or 'Não informado'
            valor = lanc.get('valor', 0)
            if forma in vendas_por_forma:
                vendas_por_forma[forma] += valor
            else:
                vendas_por_forma[forma] = valor
    
    if vendas_por_forma:
        elements.append(Paragraph("💳 Total por Forma de Pagamento", subtitulo_style))
        
        formas_data = [['Forma de Pagamento', 'Total']]
        total_vendas = 0
        for forma in sorted(vendas_por_forma.keys()):
            valor = vendas_por_forma[forma]
            formas_data.append([forma, formatar_moeda(valor)])
            total_vendas += valor
        
        # Linha de total
        formas_data.append(['TOTAL DE VENDAS', formatar_moeda(total_vendas)])
        
        tabela_formas = Table(formas_data, colWidths=[250, 200])
        tabela_formas.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff7043')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#fff3e0')]),
            # Destacar linha de total
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#26a269')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 11),
        ]))
        elements.append(tabela_formas)
        elements.append(Spacer(1, 20))
    
    # Fechamento de Caixa (apenas se o caixa estiver fechado)
    if caixa_data.get('status') == 'fechado':
        elements.append(Paragraph("💵 Fechamento de Caixa (Dinheiro)", subtitulo_style))
        
        troco_inicial = caixa_data.get('troco_inicial', 0)
        vendas_dinheiro = vendas_por_forma.get('Dinheiro', 0)
        
        # Calcular sangrias e suprimentos em dinheiro
        sangrias_dinheiro = 0
        suprimentos_dinheiro = 0
        
        for lanc in lancamentos:
            if lanc.get('forma_pagamento') == 'Dinheiro' or lanc.get('categoria') in ['sangria', 'suprimento']:
                if lanc.get('categoria') == 'sangria' and lanc.get('tipo') == 'saida':
                    sangrias_dinheiro += lanc.get('valor', 0)
                elif lanc.get('categoria') == 'suprimento' and lanc.get('tipo') == 'entrada':
                    suprimentos_dinheiro += lanc.get('valor', 0)
        
        previsao_dinheiro = troco_inicial + vendas_dinheiro + suprimentos_dinheiro - sangrias_dinheiro
        valor_contado = caixa_data.get('valor_contado', 0)
        
        fechamento_data = [
            ['Descrição', 'Valor'],
            ['Troco Inicial', formatar_moeda(troco_inicial)],
            ['(+) Vendas em Dinheiro', formatar_moeda(vendas_dinheiro)],
            ['(+) Suprimentos', formatar_moeda(suprimentos_dinheiro)],
            ['(-) Sangrias', formatar_moeda(sangrias_dinheiro)],
            ['PREVISÃO DE FECHAMENTO', formatar_moeda(previsao_dinheiro)],
        ]
        
        if valor_contado > 0:
            fechamento_data.append(['Valor Contado', formatar_moeda(valor_contado)])
            diferenca_dinheiro = valor_contado - previsao_dinheiro
            if abs(diferenca_dinheiro) >= 0.01:
                status_dif = f"{'Sobra' if diferenca_dinheiro > 0 else 'Falta'}: {formatar_moeda(abs(diferenca_dinheiro))}"
                fechamento_data.append(['Diferença', status_dif])
        
        tabela_fechamento = Table(fechamento_data, colWidths=[250, 200])
        tabela_fechamento.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#5c6bc0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#e8eaf6')]),
            # Destacar linha de previsão
            ('BACKGROUND', (0, 5), (-1, 5), colors.HexColor('#1a5fb4')),
            ('TEXTCOLOR', (0, 5), (-1, 5), colors.white),
            ('FONTNAME', (0, 5), (-1, 5), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 5), (-1, 5), 11),
        ]))
        elements.append(tabela_fechamento)
        elements.append(Spacer(1, 20))
    
    # Lista de Lançamentos Detalhada
    if lancamentos:
        elements.append(Paragraph("📝 Relação Detalhada de Lançamentos", subtitulo_style))
        
        # Separar por categoria
        vendas = [l for l in lancamentos if l.get('categoria') == 'venda']
        sangrias = [l for l in lancamentos if l.get('categoria') == 'sangria']
        suprimentos = [l for l in lancamentos if l.get('categoria') == 'suprimento']
        outros = [l for l in lancamentos if l.get('categoria') not in ['venda', 'sangria', 'suprimento']]
        
        # VENDAS
        if vendas:
            elements.append(Spacer(1, 10))
            elements.append(Paragraph("💰 VENDAS", ParagraphStyle('VendasTitulo', parent=subtitulo_style, fontSize=12, textColor=colors.HexColor('#26a269'))))
            
            lanc_data = [['Hora', 'Forma Pagamento', 'Descrição', 'Valor']]
            total_vendas = 0
            
            for lanc in vendas:
                hora = ''
                try:
                    dt = datetime.fromisoformat(lanc.get('data_hora', '').replace('Z', '+00:00'))
                    hora = dt.strftime('%H:%M')
                except:
                    hora = '-'
                
                forma_pag = lanc.get('forma_pagamento') or 'Não informado'
                descricao = lanc.get('descricao') or 'Venda'
                
                # Adicionar informação de troco
                if lanc.get('valor_recebido'):
                    troco = lanc.get('valor_recebido') - lanc.get('valor', 0)
                    if troco > 0:
                        descricao += f" | Recebido: {formatar_moeda(lanc.get('valor_recebido'))} | Troco: {formatar_moeda(troco)}"
                
                valor = lanc.get('valor', 0)
                total_vendas += valor
                
                lanc_data.append([
                    hora,
                    forma_pag,
                    descricao,
                    formatar_moeda(valor)
                ])
            
            # Adicionar linha de total
            lanc_data.append(['', '', 'TOTAL VENDAS', formatar_moeda(total_vendas)])
            
            tabela_lanc = Table(lanc_data, colWidths=[50, 110, 240, 80])
            tabela_lanc.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#26a269')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
                ('TOPPADDING', (0, 1), (-1, -1), 5),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#e8f5e9')]),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                # Destacar total
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#26a269')),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 10),
            ]))
            elements.append(tabela_lanc)
        
        # DESPESAS/SAÍDAS
        if sangrias or outros:
            despesas_lista = sangrias + [l for l in outros if l.get('tipo') == 'saida']
            if despesas_lista:
                elements.append(Spacer(1, 15))
                elements.append(Paragraph("💸 DESPESAS E SAÍDAS", ParagraphStyle('DespesasTitulo', parent=subtitulo_style, fontSize=12, textColor=colors.HexColor('#c01c28'))))
                
                lanc_data = [['Hora', 'Categoria', 'Descrição/Motivo', 'Valor']]
                total_despesas = 0
                
                for lanc in despesas_lista:
                    hora = ''
                    try:
                        dt = datetime.fromisoformat(lanc.get('data_hora', '').replace('Z', '+00:00'))
                        hora = dt.strftime('%H:%M')
                    except:
                        hora = '-'
                    
                    categoria = lanc.get('categoria', '-').capitalize()
                    descricao = lanc.get('descricao') or 'Sem descrição'
                    valor = lanc.get('valor', 0)
                    total_despesas += valor
                    
                    lanc_data.append([
                        hora,
                        categoria,
                        descricao,
                        formatar_moeda(valor)
                    ])
                
                # Adicionar linha de total
                lanc_data.append(['', '', 'TOTAL SAÍDAS', formatar_moeda(total_despesas)])
                
                tabela_lanc = Table(lanc_data, colWidths=[50, 80, 270, 80])
                tabela_lanc.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c01c28')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('TOPPADDING', (0, 0), (-1, 0), 8),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
                    ('TOPPADDING', (0, 1), (-1, -1), 5),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#fce4e4')]),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    # Destacar total
                    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#c01c28')),
                    ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, -1), (-1, -1), 10),
                ]))
                elements.append(tabela_lanc)
        
        # SUPRIMENTOS
        if suprimentos:
            elements.append(Spacer(1, 15))
            elements.append(Paragraph("💵 SUPRIMENTOS", ParagraphStyle('SuprimentosTitulo', parent=subtitulo_style, fontSize=12, textColor=colors.HexColor('#1a5fb4'))))
            
            lanc_data = [['Hora', 'Descrição/Motivo', 'Valor']]
            total_suprimentos = 0
            
            for lanc in suprimentos:
                hora = ''
                try:
                    dt = datetime.fromisoformat(lanc.get('data_hora', '').replace('Z', '+00:00'))
                    hora = dt.strftime('%H:%M')
                except:
                    hora = '-'
                
                descricao = lanc.get('descricao') or 'Suprimento'
                valor = lanc.get('valor', 0)
                total_suprimentos += valor
                
                lanc_data.append([
                    hora,
                    descricao,
                    formatar_moeda(valor)
                ])
            
            # Adicionar linha de total
            lanc_data.append(['', 'TOTAL SUPRIMENTOS', formatar_moeda(total_suprimentos)])
            
            tabela_lanc = Table(lanc_data, colWidths=[50, 350, 80])
            tabela_lanc.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5fb4')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
                ('TOPPADDING', (0, 1), (-1, -1), 5),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#e8eaf6')]),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                # Destacar total
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#1a5fb4')),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 10),
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
    
    # Lista de Lançamentos do Período - Detalhada
    lancamentos = dados_relatorio.get('lancamentos', [])
    if lancamentos:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("📝 Relação Detalhada de Lançamentos", subtitulo_style))
        
        # Separar por categoria
        vendas = [l for l in lancamentos if l.get('categoria') == 'venda']
        despesas = [l for l in lancamentos if l.get('tipo') == 'saida']
        suprimentos = [l for l in lancamentos if l.get('categoria') == 'suprimento']
        
        # VENDAS
        if vendas:
            elements.append(Spacer(1, 10))
            elements.append(Paragraph("💰 VENDAS DO PERÍODO", ParagraphStyle('VendasTitulo', parent=subtitulo_style, fontSize=12, textColor=colors.HexColor('#26a269'))))
            
            lanc_data = [['Data/Hora', 'Forma Pag.', 'Descrição', 'Valor']]
            total_vendas = 0
            
            for lanc in vendas:
                data_hora = ''
                try:
                    dt = datetime.fromisoformat(lanc.get('data_hora', '').replace('Z', '+00:00'))
                    data_hora = dt.strftime('%d/%m %H:%M')
                except:
                    data_hora = '-'
                
                forma_pag = lanc.get('forma_pagamento') or 'Não informado'
                descricao = lanc.get('descricao') or 'Venda'
                if len(descricao) > 40:
                    descricao = descricao[:37] + '...'
                
                valor = lanc.get('valor', 0)
                total_vendas += valor
                
                lanc_data.append([
                    data_hora,
                    forma_pag,
                    descricao,
                    formatar_moeda(valor)
                ])
            
            lanc_data.append(['', '', 'TOTAL VENDAS', formatar_moeda(total_vendas)])
            
            tabela_lanc = Table(lanc_data, colWidths=[70, 100, 210, 70])
            tabela_lanc.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#26a269')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                ('TOPPADDING', (0, 1), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#e8f5e9')]),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#26a269')),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ]))
            elements.append(tabela_lanc)
        
        # DESPESAS/SAÍDAS
        if despesas:
            elements.append(Spacer(1, 15))
            elements.append(Paragraph("💸 DESPESAS E SAÍDAS DO PERÍODO", ParagraphStyle('DespesasTitulo', parent=subtitulo_style, fontSize=12, textColor=colors.HexColor('#c01c28'))))
            
            lanc_data = [['Data/Hora', 'Categoria', 'Descrição', 'Valor']]
            total_despesas = 0
            
            for lanc in despesas:
                data_hora = ''
                try:
                    dt = datetime.fromisoformat(lanc.get('data_hora', '').replace('Z', '+00:00'))
                    data_hora = dt.strftime('%d/%m %H:%M')
                except:
                    data_hora = '-'
                
                categoria = lanc.get('categoria', '-').capitalize()
                descricao = lanc.get('descricao') or 'Sem descrição'
                if len(descricao) > 40:
                    descricao = descricao[:37] + '...'
                
                valor = lanc.get('valor', 0)
                total_despesas += valor
                
                lanc_data.append([
                    data_hora,
                    categoria,
                    descricao,
                    formatar_moeda(valor)
                ])
            
            lanc_data.append(['', '', 'TOTAL SAÍDAS', formatar_moeda(total_despesas)])
            
            tabela_lanc = Table(lanc_data, colWidths=[70, 80, 230, 70])
            tabela_lanc.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c01c28')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                ('TOPPADDING', (0, 1), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#fce4e4')]),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#c01c28')),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ]))
            elements.append(tabela_lanc)
        
        # SUPRIMENTOS
        if suprimentos:
            elements.append(Spacer(1, 15))
            elements.append(Paragraph("💵 SUPRIMENTOS DO PERÍODO", ParagraphStyle('SuprimentosTitulo', parent=subtitulo_style, fontSize=12, textColor=colors.HexColor('#1a5fb4'))))
            
            lanc_data = [['Data/Hora', 'Descrição', 'Valor']]
            total_suprimentos = 0
            
            for lanc in suprimentos:
                data_hora = ''
                try:
                    dt = datetime.fromisoformat(lanc.get('data_hora', '').replace('Z', '+00:00'))
                    data_hora = dt.strftime('%d/%m %H:%M')
                except:
                    data_hora = '-'
                
                descricao = lanc.get('descricao') or 'Suprimento'
                if len(descricao) > 50:
                    descricao = descricao[:47] + '...'
                
                valor = lanc.get('valor', 0)
                total_suprimentos += valor
                
                lanc_data.append([
                    data_hora,
                    descricao,
                    formatar_moeda(valor)
                ])
            
            lanc_data.append(['', 'TOTAL SUPRIMENTOS', formatar_moeda(total_suprimentos)])
            
            tabela_lanc = Table(lanc_data, colWidths=[70, 310, 70])
            tabela_lanc.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5fb4')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                ('TOPPADDING', (0, 1), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#e8eaf6')]),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#1a5fb4')),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
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
    
    # Lista de Lançamentos Detalhada
    lancamentos = data_resumo.get('lancamentos', [])
    if lancamentos:
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("📝 Relação Detalhada de Lançamentos", subtitulo_style))
        
        # Separar por categoria
        vendas = [l for l in lancamentos if l.get('categoria') == 'venda' and not l.get('estornado')]
        despesas = [l for l in lancamentos if l.get('tipo') == 'saida' and not l.get('estornado')]
        suprimentos = [l for l in lancamentos if l.get('categoria') == 'suprimento' and not l.get('estornado')]
        
        # VENDAS
        if vendas:
            elements.append(Spacer(1, 10))
            elements.append(Paragraph("💰 VENDAS DO DIA", ParagraphStyle('VendasTitulo', parent=subtitulo_style, fontSize=12, textColor=colors.HexColor('#26a269'))))
            
            lanc_data = [['Hora', 'Forma Pag.', 'Descrição', 'Valor']]
            total_vendas_lista = 0
            
            for lanc in vendas:
                hora = ''
                try:
                    dt = datetime.fromisoformat(lanc.get('data_hora', '').replace('Z', '+00:00'))
                    hora = dt.strftime('%H:%M')
                except:
                    hora = '-'
                
                forma_pag = lanc.get('forma_pagamento') or 'Não informado'
                descricao = lanc.get('descricao') or 'Venda'
                if len(descricao) > 35:
                    descricao = descricao[:32] + '...'
                
                valor = lanc.get('valor', 0)
                total_vendas_lista += valor
                
                lanc_data.append([
                    hora,
                    forma_pag,
                    descricao,
                    formatar_moeda(valor)
                ])
            
            lanc_data.append(['', '', 'TOTAL VENDAS', formatar_moeda(total_vendas_lista)])
            
            tabela_lanc = Table(lanc_data, colWidths=[50, 100, 220, 80])
            tabela_lanc.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#26a269')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                ('TOPPADDING', (0, 1), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#e8f5e9')]),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#26a269')),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ]))
            elements.append(tabela_lanc)
        
        # DESPESAS/SAÍDAS
        if despesas:
            elements.append(Spacer(1, 15))
            elements.append(Paragraph("💸 DESPESAS E SAÍDAS", ParagraphStyle('DespesasTitulo', parent=subtitulo_style, fontSize=12, textColor=colors.HexColor('#c01c28'))))
            
            lanc_data = [['Hora', 'Categoria', 'Descrição', 'Valor']]
            total_despesas = 0
            
            for lanc in despesas:
                hora = ''
                try:
                    dt = datetime.fromisoformat(lanc.get('data_hora', '').replace('Z', '+00:00'))
                    hora = dt.strftime('%H:%M')
                except:
                    hora = '-'
                
                categoria = lanc.get('categoria', '-').capitalize()
                descricao = lanc.get('descricao') or 'Sem descrição'
                if len(descricao) > 35:
                    descricao = descricao[:32] + '...'
                
                valor = lanc.get('valor', 0)
                total_despesas += valor
                
                lanc_data.append([
                    hora,
                    categoria,
                    descricao,
                    formatar_moeda(valor)
                ])
            
            lanc_data.append(['', '', 'TOTAL SAÍDAS', formatar_moeda(total_despesas)])
            
            tabela_lanc = Table(lanc_data, colWidths=[50, 80, 240, 80])
            tabela_lanc.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c01c28')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                ('TOPPADDING', (0, 1), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#fce4e4')]),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#c01c28')),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ]))
            elements.append(tabela_lanc)
        
        # SUPRIMENTOS
        if suprimentos:
            elements.append(Spacer(1, 15))
            elements.append(Paragraph("💵 SUPRIMENTOS", ParagraphStyle('SuprimentosTitulo', parent=subtitulo_style, fontSize=12, textColor=colors.HexColor('#1a5fb4'))))
            
            lanc_data = [['Hora', 'Descrição', 'Valor']]
            total_suprimentos = 0
            
            for lanc in suprimentos:
                hora = ''
                try:
                    dt = datetime.fromisoformat(lanc.get('data_hora', '').replace('Z', '+00:00'))
                    hora = dt.strftime('%H:%M')
                except:
                    hora = '-'
                
                descricao = lanc.get('descricao') or 'Suprimento'
                if len(descricao) > 50:
                    descricao = descricao[:47] + '...'
                
                valor = lanc.get('valor', 0)
                total_suprimentos += valor
                
                lanc_data.append([
                    hora,
                    descricao,
                    formatar_moeda(valor)
                ])
            
            lanc_data.append(['', 'TOTAL SUPRIMENTOS', formatar_moeda(total_suprimentos)])
            
            tabela_lanc = Table(lanc_data, colWidths=[50, 320, 80])
            tabela_lanc.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5fb4')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ALIGN', (2, 1), (2, -1), 'RIGHT'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                ('TOPPADDING', (0, 1), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#e8eaf6')]),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#1a5fb4')),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ]))
            elements.append(tabela_lanc)
    
    # Rodapé
    elements.append(Spacer(1, 30))
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


def gerar_cupom_termico_caixa(caixa_data, lancamentos, nome_loja='Minha Loja'):
    """
    Gera cupom térmico para impressora 80mm (Elgin I9 e similares)
    Papel: 80mm largura = aproximadamente 72mm área útil
    """
    buffer = BytesIO()
    
    # Tamanho do papel: 80mm largura (72mm área de impressão)
    # Altura dinâmica baseada no conteúdo
    largura_papel = 72 * mm
    altura_papel = 297 * mm  # Altura máxima, será cortada pela impressora
    
    doc = SimpleDocTemplate(
        buffer,
        pagesize=(largura_papel, altura_papel),
        rightMargin=2*mm,
        leftMargin=2*mm,
        topMargin=3*mm,
        bottomMargin=3*mm
    )
    
    largura_util = largura_papel - 4*mm  # Descontando margens
    
    # Estilos otimizados para cupom térmico
    styles = getSampleStyleSheet()
    
    titulo_style = ParagraphStyle(
        'TituloTermico',
        parent=styles['Normal'],
        fontSize=11,
        alignment=TA_CENTER,
        spaceAfter=2*mm,
        fontName='Helvetica-Bold'
    )
    
    subtitulo_style = ParagraphStyle(
        'SubtituloTermico',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_CENTER,
        spaceAfter=1*mm,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'NormalTermico',
        parent=styles['Normal'],
        fontSize=7,
        alignment=TA_LEFT,
        spaceAfter=0.5*mm,
        fontName='Helvetica'
    )
    
    central_style = ParagraphStyle(
        'CentralTermico',
        parent=styles['Normal'],
        fontSize=7,
        alignment=TA_CENTER,
        spaceAfter=0.5*mm,
        fontName='Helvetica'
    )
    
    valor_style = ParagraphStyle(
        'ValorTermico',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        spaceAfter=1*mm
    )
    
    elements = []
    
    # Linha divisória
    def linha_divisoria():
        return Paragraph("-" * 48, central_style)
    
    # Cabeçalho
    elements.append(Paragraph(nome_loja.upper(), titulo_style))
    elements.append(Paragraph("FECHAMENTO DE CAIXA", subtitulo_style))
    elements.append(linha_divisoria())
    
    # Informações do caixa
    status_texto = "ABERTO" if caixa_data.get('status') == 'aberto' else "FECHADO"
    elements.append(Paragraph(f"<b>Caixa #{caixa_data.get('id', '-')}</b> - {status_texto}", central_style))
    
    if caixa_data.get('operador'):
        elements.append(Paragraph(f"Operador: {caixa_data.get('operador')}", central_style))
    
    elements.append(Paragraph(f"Abertura: {formatar_data(caixa_data.get('data_abertura'))}", central_style))
    
    if caixa_data.get('data_fechamento'):
        elements.append(Paragraph(f"Fechamento: {formatar_data(caixa_data.get('data_fechamento'))}", central_style))
    
    elements.append(linha_divisoria())
    
    # Resumo financeiro
    elements.append(Paragraph("RESUMO", subtitulo_style))
    
    troco_inicial = caixa_data.get('troco_inicial', 0)
    total_entradas = caixa_data.get('total_entradas', 0)
    total_saidas = caixa_data.get('total_saidas', 0)
    saldo_atual = caixa_data.get('saldo_atual', 0)
    
    resumo_data = [
        ['Troco Inicial:', formatar_moeda(troco_inicial)],
        ['(+) Entradas:', formatar_moeda(total_entradas)],
        ['(-) Saídas:', formatar_moeda(total_saidas)],
    ]
    
    col_width = largura_util / 2
    tabela_resumo = Table(resumo_data, colWidths=[col_width, col_width])
    tabela_resumo.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
    ]))
    elements.append(tabela_resumo)
    
    elements.append(Spacer(1, 2*mm))
    elements.append(Paragraph("SALDO FINAL", subtitulo_style))
    elements.append(Paragraph(formatar_moeda(saldo_atual), valor_style))
    
    # Saldo em dinheiro (usar do caixa_data se disponível, senão calcular)
    saldo_dinheiro = caixa_data.get('saldo_dinheiro')
    
    if saldo_dinheiro is None:
        # Calcular se não estiver disponível (para retrocompatibilidade)
        vendas_dinheiro = 0
        sangrias_total = 0
        suprimentos_total = 0
        despesas_dinheiro = 0
        
        for lanc in lancamentos:
            if lanc.get('categoria') == 'venda' and lanc.get('tipo') == 'entrada':
                if lanc.get('forma_pagamento') == 'Dinheiro':
                    vendas_dinheiro += lanc.get('valor', 0)
            elif lanc.get('categoria') == 'sangria' and lanc.get('tipo') == 'saida':
                sangrias_total += lanc.get('valor', 0)
            elif lanc.get('categoria') == 'suprimento' and lanc.get('tipo') == 'entrada':
                suprimentos_total += lanc.get('valor', 0)
            elif lanc.get('categoria') not in ['venda', 'sangria', 'suprimento'] and lanc.get('tipo') == 'saida':
                if lanc.get('forma_pagamento') == 'Dinheiro' or not lanc.get('forma_pagamento'):
                    despesas_dinheiro += lanc.get('valor', 0)
        
        saldo_dinheiro = troco_inicial + vendas_dinheiro + suprimentos_total - sangrias_total - despesas_dinheiro
    
    elements.append(Spacer(1, 1*mm))
    elements.append(Paragraph("SALDO EM DINHEIRO", subtitulo_style))
    elements.append(Paragraph(formatar_moeda(saldo_dinheiro), valor_style))
    
    # Diferença (se houver)
    if caixa_data.get('valor_contado') is not None:
        elements.append(linha_divisoria())
        valor_contado = caixa_data.get('valor_contado', 0)
        diferenca = caixa_data.get('diferenca', 0)
        
        elements.append(Paragraph(f"Valor Contado: {formatar_moeda(valor_contado)}", central_style))
        
        if abs(diferenca) < 0.01:
            elements.append(Paragraph("Diferença: CONFERIDO", central_style))
        elif diferenca > 0:
            elements.append(Paragraph(f"Diferença: +{formatar_moeda(diferenca)} (SOBRA)", central_style))
        else:
            elements.append(Paragraph(f"Diferença: {formatar_moeda(diferenca)} (FALTA)", central_style))
    
    elements.append(linha_divisoria())
    
    # Vendas por forma de pagamento
    vendas_por_forma = {}
    total_vendas = 0
    for lanc in lancamentos:
        if lanc.get('categoria') == 'venda' and lanc.get('tipo') == 'entrada':
            forma = lanc.get('forma_pagamento') or 'N/I'
            valor = lanc.get('valor', 0)
            vendas_por_forma[forma] = vendas_por_forma.get(forma, 0) + valor
            total_vendas += valor
    
    if vendas_por_forma:
        elements.append(Paragraph("VENDAS POR PAGAMENTO", subtitulo_style))
        
        formas_data = []
        for forma in sorted(vendas_por_forma.keys()):
            formas_data.append([forma, formatar_moeda(vendas_por_forma[forma])])
        formas_data.append(['TOTAL VENDAS', formatar_moeda(total_vendas)])
        
        tabela_formas = Table(formas_data, colWidths=[col_width, col_width])
        tabela_formas.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -2), 'Helvetica'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('LINEABOVE', (0, -1), (-1, -1), 0.5, colors.black),
        ]))
        elements.append(tabela_formas)
        elements.append(linha_divisoria())
    
    # Contagem de lançamentos
    qtd_vendas = len([l for l in lancamentos if l.get('categoria') == 'venda'])
    qtd_sangrias = len([l for l in lancamentos if l.get('categoria') == 'sangria'])
    qtd_suprimentos = len([l for l in lancamentos if l.get('categoria') == 'suprimento'])
    
    elements.append(Paragraph("MOVIMENTO", subtitulo_style))
    elements.append(Paragraph(f"Vendas: {qtd_vendas} | Sangrias: {qtd_sangrias} | Suprimentos: {qtd_suprimentos}", central_style))
    
    elements.append(linha_divisoria())
    
    # ===== LANÇAMENTOS DETALHADOS =====
    if lancamentos:
        # Separar por categoria
        vendas = [l for l in lancamentos if l.get('categoria') == 'venda']
        sangrias = [l for l in lancamentos if l.get('categoria') == 'sangria']
        suprimentos = [l for l in lancamentos if l.get('categoria') == 'suprimento']
        outros = [l for l in lancamentos if l.get('categoria') not in ['venda', 'sangria', 'suprimento']]
        
        item_style = ParagraphStyle(
            'ItemTermico',
            parent=styles['Normal'],
            fontSize=6,
            alignment=TA_LEFT,
            spaceAfter=0.3*mm,
            fontName='Helvetica'
        )
        
        # VENDAS
        if vendas:
            elements.append(Paragraph("VENDAS", subtitulo_style))
            
            for lanc in vendas:
                hora = ''
                try:
                    dt = datetime.fromisoformat(lanc.get('data_hora', '').replace('Z', '+00:00'))
                    hora = dt.strftime('%H:%M')
                except:
                    hora = '--:--'
                
                forma = lanc.get('forma_pagamento') or 'N/I'
                valor = formatar_moeda(lanc.get('valor', 0))
                descricao = lanc.get('descricao') or ''
                
                # Linha principal: hora, forma e valor
                elements.append(Paragraph(f"{hora} {forma[:12]:<12} {valor}", item_style))
                
                # Descrição em linha separada se existir
                if descricao:
                    desc_curta = descricao[:35] + '...' if len(descricao) > 35 else descricao
                    elements.append(Paragraph(f"  {desc_curta}", item_style))
            
            elements.append(linha_divisoria())
        
        # SANGRIAS
        if sangrias:
            elements.append(Paragraph("SANGRIAS", subtitulo_style))
            
            total_sangrias = 0
            for lanc in sangrias:
                hora = ''
                try:
                    dt = datetime.fromisoformat(lanc.get('data_hora', '').replace('Z', '+00:00'))
                    hora = dt.strftime('%H:%M')
                except:
                    hora = '--:--'
                
                valor = lanc.get('valor', 0)
                total_sangrias += valor
                descricao = lanc.get('descricao') or 'Sangria'
                desc_curta = descricao[:25] + '...' if len(descricao) > 25 else descricao
                
                elements.append(Paragraph(f"{hora} {desc_curta:<25} -{formatar_moeda(valor)}", item_style))
            
            elements.append(Paragraph(f"<b>TOTAL SANGRIAS: {formatar_moeda(total_sangrias)}</b>", central_style))
            elements.append(linha_divisoria())
        
        # SUPRIMENTOS
        if suprimentos:
            elements.append(Paragraph("SUPRIMENTOS", subtitulo_style))
            
            total_suprimentos = 0
            for lanc in suprimentos:
                hora = ''
                try:
                    dt = datetime.fromisoformat(lanc.get('data_hora', '').replace('Z', '+00:00'))
                    hora = dt.strftime('%H:%M')
                except:
                    hora = '--:--'
                
                valor = lanc.get('valor', 0)
                total_suprimentos += valor
                descricao = lanc.get('descricao') or 'Suprimento'
                desc_curta = descricao[:25] + '...' if len(descricao) > 25 else descricao
                
                elements.append(Paragraph(f"{hora} {desc_curta:<25} +{formatar_moeda(valor)}", item_style))
            
            elements.append(Paragraph(f"<b>TOTAL SUPRIMENTOS: {formatar_moeda(total_suprimentos)}</b>", central_style))
            elements.append(linha_divisoria())
        
        # OUTROS
        if outros:
            elements.append(Paragraph("OUTROS", subtitulo_style))
            
            for lanc in outros:
                hora = ''
                try:
                    dt = datetime.fromisoformat(lanc.get('data_hora', '').replace('Z', '+00:00'))
                    hora = dt.strftime('%H:%M')
                except:
                    hora = '--:--'
                
                tipo = '+' if lanc.get('tipo') == 'entrada' else '-'
                valor = formatar_moeda(lanc.get('valor', 0))
                categoria = lanc.get('categoria') or 'outros'
                descricao = lanc.get('descricao') or categoria
                desc_curta = descricao[:25] + '...' if len(descricao) > 25 else descricao
                
                elements.append(Paragraph(f"{hora} {desc_curta:<25} {tipo}{valor}", item_style))
            
            elements.append(linha_divisoria())
    
    # Observação (se houver)
    if caixa_data.get('observacao'):
        elements.append(Paragraph(f"Obs: {caixa_data.get('observacao')}", normal_style))
        elements.append(linha_divisoria())
    
    # Rodapé
    elements.append(Spacer(1, 2*mm))
    elements.append(Paragraph(
        f"Impresso: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        central_style
    ))
    elements.append(Paragraph("Sistema PDV", central_style))
    elements.append(Spacer(1, 5*mm))  # Espaço para corte
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
