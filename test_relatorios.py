#!/usr/bin/env python3
"""
Script de teste para as funcionalidades de relatórios
Testa geração de PDFs e endpoints da API
"""

import sys
import os
from datetime import datetime, timedelta
from app import create_app
from app.models import db, Caixa, Lancamento, Configuracao
from app.pdf_generator import (
    gerar_relatorio_caixa_pdf,
    gerar_relatorio_periodo_pdf,
    gerar_resumo_diario_pdf
)


def criar_dados_teste():
    """Cria dados de teste no banco de dados"""
    print("\n📊 Criando dados de teste...")
    
    # Configuração
    config = Configuracao.get_config()
    config.nome_loja = "Loja Teste"
    config.responsavel = "Gerente Teste"
    
    # Criar caixa de teste
    hoje = datetime.now()
    caixa = Caixa(
        operador="Operador Teste",
        troco_inicial=100.00,
        status='fechado',
        data_abertura=hoje.replace(hour=8, minute=0),
        data_fechamento=hoje.replace(hour=18, minute=0),
        valor_contado=1400.00,
        diferenca=0.00
    )
    db.session.add(caixa)
    db.session.flush()
    
    # Criar lançamentos de teste
    lancamentos_teste = [
        # Vendas
        {
            'tipo': 'entrada',
            'categoria': 'venda',
            'valor': 100.00,
            'forma_pagamento': 'Dinheiro',
            'descricao': 'Venda 1',
            'data_hora': hoje.replace(hour=9, minute=30)
        },
        {
            'tipo': 'entrada',
            'categoria': 'venda',
            'valor': 250.00,
            'forma_pagamento': 'PIX',
            'descricao': 'Venda 2',
            'data_hora': hoje.replace(hour=10, minute=15)
        },
        {
            'tipo': 'entrada',
            'categoria': 'venda',
            'valor': 350.00,
            'forma_pagamento': 'Cartão de Crédito',
            'descricao': 'Venda 3',
            'data_hora': hoje.replace(hour=11, minute=45)
        },
        {
            'tipo': 'entrada',
            'categoria': 'venda',
            'valor': 180.00,
            'forma_pagamento': 'Cartão de Débito',
            'descricao': 'Venda 4',
            'data_hora': hoje.replace(hour=14, minute=20)
        },
        {
            'tipo': 'entrada',
            'categoria': 'venda',
            'valor': 420.00,
            'forma_pagamento': 'PIX',
            'descricao': 'Venda 5',
            'data_hora': hoje.replace(hour=15, minute=30)
        },
        {
            'tipo': 'entrada',
            'categoria': 'venda',
            'valor': 200.00,
            'forma_pagamento': 'Dinheiro',
            'descricao': 'Venda 6',
            'data_hora': hoje.replace(hour=16, minute=10)
        },
        # Sangrias
        {
            'tipo': 'saida',
            'categoria': 'sangria',
            'valor': 150.00,
            'forma_pagamento': None,
            'descricao': 'Sangria para banco',
            'data_hora': hoje.replace(hour=12, minute=0)
        },
        {
            'tipo': 'saida',
            'categoria': 'sangria',
            'valor': 50.00,
            'forma_pagamento': None,
            'descricao': 'Sangria para despesas',
            'data_hora': hoje.replace(hour=17, minute=0)
        },
        # Suprimento
        {
            'tipo': 'entrada',
            'categoria': 'suprimento',
            'valor': 50.00,
            'forma_pagamento': None,
            'descricao': 'Reforço de caixa',
            'data_hora': hoje.replace(hour=13, minute=0)
        }
    ]
    
    for lanc_data in lancamentos_teste:
        lanc = Lancamento(
            caixa_id=caixa.id,
            **lanc_data
        )
        db.session.add(lanc)
    
    db.session.commit()
    print(f"✓ Caixa #{caixa.id} criado com {len(lancamentos_teste)} lançamentos")
    
    return caixa.id


def testar_relatorio_caixa(caixa_id):
    """Testa geração de relatório de caixa específico"""
    print(f"\n🧪 Testando relatório de caixa #{caixa_id}...")
    
    try:
        caixa = Caixa.query.get(caixa_id)
        if not caixa:
            print(f"❌ Caixa #{caixa_id} não encontrado")
            return False
        
        lancamentos = Lancamento.query.filter_by(caixa_id=caixa_id).all()
        
        pdf_buffer = gerar_relatorio_caixa_pdf(
            caixa.to_dict(),
            [l.to_dict() for l in lancamentos],
            "Loja Teste"
        )
        
        # Salvar PDF
        filename = f"test_relatorio_caixa_{caixa_id}.pdf"
        with open(filename, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        file_size = os.path.getsize(filename)
        print(f"✓ PDF do caixa gerado: {filename} ({file_size} bytes)")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao gerar PDF do caixa: {e}")
        import traceback
        traceback.print_exc()
        return False


def testar_relatorio_periodo():
    """Testa geração de relatório por período"""
    print("\n🧪 Testando relatório por período...")
    
    try:
        hoje = datetime.now()
        inicio = (hoje - timedelta(days=7)).replace(hour=0, minute=0, second=0)
        fim = hoje.replace(hour=23, minute=59, second=59)
        
        # Buscar dados
        from sqlalchemy import func, and_
        
        total_entradas = db.session.query(func.sum(Lancamento.valor)).filter(
            and_(
                Lancamento.tipo == 'entrada',
                Lancamento.data_hora >= inicio,
                Lancamento.data_hora <= fim
            )
        ).scalar() or 0
        
        total_saidas = db.session.query(func.sum(Lancamento.valor)).filter(
            and_(
                Lancamento.tipo == 'saida',
                Lancamento.data_hora >= inicio,
                Lancamento.data_hora <= fim
            )
        ).scalar() or 0
        
        categorias = db.session.query(
            Lancamento.categoria,
            Lancamento.tipo,
            func.sum(Lancamento.valor).label('total')
        ).filter(
            and_(
                Lancamento.data_hora >= inicio,
                Lancamento.data_hora <= fim
            )
        ).group_by(Lancamento.categoria, Lancamento.tipo).all()
        
        pagamentos = db.session.query(
            Lancamento.forma_pagamento,
            func.sum(Lancamento.valor).label('total')
        ).filter(
            and_(
                Lancamento.categoria == 'venda',
                Lancamento.estorno == None,
                Lancamento.data_hora >= inicio,
                Lancamento.data_hora <= fim
            )
        ).group_by(Lancamento.forma_pagamento).all()
        
        lancamentos = Lancamento.query.filter(
            and_(
                Lancamento.data_hora >= inicio,
                Lancamento.data_hora <= fim
            )
        ).all()
        
        dados_relatorio = {
            'periodo': {
                'inicio': inicio.isoformat(),
                'fim': fim.isoformat()
            },
            'totais': {
                'entradas': float(total_entradas),
                'saidas': float(total_saidas),
                'saldo': float(total_entradas - total_saidas)
            },
            'categorias': [
                {'categoria': c.categoria, 'tipo': c.tipo, 'total': float(c.total)}
                for c in categorias
            ],
            'pagamentos': [
                {'forma': p.forma_pagamento or 'Não informado', 'total': float(p.total)}
                for p in pagamentos
            ],
            'lancamentos': [l.to_dict() for l in lancamentos]
        }
        
        pdf_buffer = gerar_relatorio_periodo_pdf(dados_relatorio, "Loja Teste")
        
        # Salvar PDF
        filename = "test_relatorio_periodo.pdf"
        with open(filename, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        file_size = os.path.getsize(filename)
        print(f"✓ PDF do período gerado: {filename} ({file_size} bytes)")
        print(f"  - Período: {inicio.strftime('%d/%m/%Y')} a {fim.strftime('%d/%m/%Y')}")
        print(f"  - Total entradas: R$ {total_entradas:,.2f}")
        print(f"  - Total saídas: R$ {total_saidas:,.2f}")
        print(f"  - Saldo: R$ {total_entradas - total_saidas:,.2f}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao gerar PDF do período: {e}")
        import traceback
        traceback.print_exc()
        return False


def testar_resumo_diario():
    """Testa geração de resumo diário"""
    print("\n🧪 Testando resumo diário...")
    
    try:
        hoje = datetime.now()
        data = hoje.date()
        inicio_dia = datetime.combine(data, datetime.min.time())
        fim_dia = datetime.combine(data, datetime.max.time())
        
        lancamentos = Lancamento.query.filter(
            Lancamento.data_hora >= inicio_dia,
            Lancamento.data_hora <= fim_dia
        ).all()
        
        vendas_dinheiro = 0
        vendas_pix = 0
        vendas_cartao_credito = 0
        vendas_cartao_debito = 0
        total_sangrias = 0
        total_suprimentos = 0
        
        for lanc in lancamentos:
            if lanc.estorno:
                continue
            if lanc.categoria == 'venda':
                forma = (lanc.forma_pagamento or '').lower()
                if 'dinheiro' in forma:
                    vendas_dinheiro += lanc.valor
                elif 'pix' in forma:
                    vendas_pix += lanc.valor
                elif 'crédito' in forma or 'credito' in forma:
                    vendas_cartao_credito += lanc.valor
                elif 'débito' in forma or 'debito' in forma:
                    vendas_cartao_debito += lanc.valor
            elif lanc.categoria == 'sangria':
                total_sangrias += lanc.valor
            elif lanc.categoria == 'suprimento':
                total_suprimentos += lanc.valor
        
        total_vendas = vendas_dinheiro + vendas_pix + vendas_cartao_credito + vendas_cartao_debito
        
        data_resumo = {
            'data': data.strftime('%Y-%m-%d'),
            'total_vendas': total_vendas,
            'vendas': {
                'dinheiro': vendas_dinheiro,
                'pix': vendas_pix,
                'cartao_credito': vendas_cartao_credito,
                'cartao_debito': vendas_cartao_debito
            },
            'movimentacoes': {
                'sangrias': total_sangrias,
                'suprimentos': total_suprimentos
            }
        }
        
        pdf_buffer = gerar_resumo_diario_pdf(data_resumo, "Loja Teste")
        
        # Salvar PDF
        filename = "test_resumo_diario.pdf"
        with open(filename, 'wb') as f:
            f.write(pdf_buffer.getvalue())
        
        file_size = os.path.getsize(filename)
        print(f"✓ PDF do resumo diário gerado: {filename} ({file_size} bytes)")
        print(f"  - Data: {data.strftime('%d/%m/%Y')}")
        print(f"  - Total vendas: R$ {total_vendas:,.2f}")
        print(f"  - Dinheiro: R$ {vendas_dinheiro:,.2f}")
        print(f"  - PIX: R$ {vendas_pix:,.2f}")
        print(f"  - Cartão Crédito: R$ {vendas_cartao_credito:,.2f}")
        print(f"  - Cartão Débito: R$ {vendas_cartao_debito:,.2f}")
        print(f"  - Sangrias: R$ {total_sangrias:,.2f}")
        print(f"  - Suprimentos: R$ {total_suprimentos:,.2f}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao gerar PDF do resumo diário: {e}")
        import traceback
        traceback.print_exc()
        return False


def testar_endpoints_api():
    """Testa os endpoints da API de relatórios"""
    print("\n🧪 Testando endpoints da API...")
    
    from flask import Flask
    
    try:
        app = create_app()
        client = app.test_client()
        
        # Teste 1: Relatório resumo
        hoje = datetime.now()
        inicio = (hoje - timedelta(days=1)).isoformat()
        fim = hoje.isoformat()
        
        response = client.get(f'/api/relatorio/resumo?data_inicio={inicio}&data_fim={fim}')
        if response.status_code == 200:
            data = response.get_json()
            print(f"✓ GET /api/relatorio/resumo - Status {response.status_code}")
            print(f"  - Entradas: R$ {data['totais']['entradas']:,.2f}")
            print(f"  - Saídas: R$ {data['totais']['saidas']:,.2f}")
            print(f"  - Saldo: R$ {data['totais']['saldo']:,.2f}")
        else:
            print(f"❌ GET /api/relatorio/resumo - Status {response.status_code}")
            return False
        
        # Teste 2: PDF de caixa
        caixa = Caixa.query.filter_by(status='fechado').first()
        if caixa:
            response = client.get(f'/api/relatorio/caixa/{caixa.id}/pdf')
            if response.status_code == 200 and response.mimetype == 'application/pdf':
                print(f"✓ GET /api/relatorio/caixa/{caixa.id}/pdf - Status {response.status_code}")
                print(f"  - Content-Type: {response.mimetype}")
                print(f"  - Tamanho: {len(response.data)} bytes")
            else:
                print(f"❌ GET /api/relatorio/caixa/{caixa.id}/pdf - Status {response.status_code}")
                return False
        
        # Teste 3: PDF de período
        response = client.get(f'/api/relatorio/periodo/pdf?data_inicio={inicio}&data_fim={fim}')
        if response.status_code == 200 and response.mimetype == 'application/pdf':
            print(f"✓ GET /api/relatorio/periodo/pdf - Status {response.status_code}")
            print(f"  - Content-Type: {response.mimetype}")
            print(f"  - Tamanho: {len(response.data)} bytes")
        else:
            print(f"❌ GET /api/relatorio/periodo/pdf - Status {response.status_code}")
            return False
        
        # Teste 4: PDF de resumo diário
        data_str = hoje.strftime('%Y-%m-%d')
        response = client.get(f'/api/relatorio/resumo-diario/pdf?data={data_str}')
        if response.status_code == 200 and response.mimetype == 'application/pdf':
            print(f"✓ GET /api/relatorio/resumo-diario/pdf - Status {response.status_code}")
            print(f"  - Content-Type: {response.mimetype}")
            print(f"  - Tamanho: {len(response.data)} bytes")
        else:
            print(f"❌ GET /api/relatorio/resumo-diario/pdf - Status {response.status_code}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar endpoints: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Executa todos os testes de relatórios"""
    print("=" * 60)
    print("🔍 TESTE DE RELATÓRIOS - SimplesCaixa")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        # Criar banco de dados
        db.create_all()
        
        # Criar dados de teste
        caixa_id = criar_dados_teste()
        
        # Executar testes
        resultados = []
        
        resultados.append(("Relatório de Caixa (PDF)", testar_relatorio_caixa(caixa_id)))
        resultados.append(("Relatório de Período (PDF)", testar_relatorio_periodo()))
        resultados.append(("Resumo Diário (PDF)", testar_resumo_diario()))
        resultados.append(("Endpoints da API", testar_endpoints_api()))
        
        # Resumo final
        print("\n" + "=" * 60)
        print("📊 RESUMO DOS TESTES")
        print("=" * 60)
        
        sucesso = 0
        falha = 0
        
        for nome, resultado in resultados:
            status = "✓ PASSOU" if resultado else "❌ FALHOU"
            print(f"{status} - {nome}")
            if resultado:
                sucesso += 1
            else:
                falha += 1
        
        print("\n" + "-" * 60)
        print(f"Total: {len(resultados)} testes")
        print(f"Sucesso: {sucesso} ✓")
        print(f"Falha: {falha} ❌")
        print("=" * 60)
        
        if falha == 0:
            print("\n🎉 Todos os testes passaram com sucesso!")
            return 0
        else:
            print(f"\n⚠️  {falha} teste(s) falharam")
            return 1


if __name__ == '__main__':
    sys.exit(main())
