"""
Rotas da aplicação
"""
from flask import Blueprint, render_template, request, jsonify, Response
from app.models import db, Caixa, Lancamento, Configuracao, Estorno
from app.pdf_generator import (
    gerar_relatorio_caixa_pdf, gerar_relatorio_periodo_pdf, gerar_resumo_diario_pdf,
    gerar_cupom_termico_caixa
)
from app.time_sync import get_time_sync, get_brasilia_time, get_brasilia_time_iso
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_

main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)

# ===== ROTAS DE VIEWS =====

@main_bp.route('/')
def index():
    """Página principal - painel de lançamentos"""
    return render_template('index.html')

@main_bp.route('/historico')
def historico():
    """Página de histórico e relatórios"""
    return render_template('historico.html')

@main_bp.route('/configuracoes')
def configuracoes():
    """Página de configurações"""
    return render_template('configuracoes.html')

@main_bp.route('/gerente')
def gerente():
    """Painel do gerente/dono - acesso mobile"""
    return render_template('gerente.html')

@main_bp.route('/time-demo')
def time_demo():
    """Página de demonstração da sincronização de horário"""
    return render_template('time-demo.html')

# ===== API - CONFIGURAÇÕES =====

@api_bp.route('/configuracao', methods=['GET'])
def get_configuracao():
    """Obter configurações do sistema"""
    config = Configuracao.get_config()
    return jsonify({
        'nome_loja': config.nome_loja,
        'responsavel': config.responsavel,
        'formas_pagamento': config.formas_pagamento.split(',')
    })

@api_bp.route('/configuracao', methods=['PUT'])
def update_configuracao():
    """Atualizar configurações"""
    data = request.json
    config = Configuracao.get_config()
    
    if 'nome_loja' in data:
        config.nome_loja = data['nome_loja']
    if 'responsavel' in data:
        config.responsavel = data['responsavel']
    if 'formas_pagamento' in data:
        config.formas_pagamento = ','.join(data['formas_pagamento'])
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Configurações atualizadas'})

# ===== API - HORA SINCRONIZADA =====

@api_bp.route('/time/current', methods=['GET'])
def get_current_time():
    """Obter hora atual sincronizada de Brasília"""
    time_sync = get_time_sync()
    current_time = time_sync.get_current_time()
    
    return jsonify({
        'success': True,
        'datetime': current_time.isoformat(),
        'timestamp': int(current_time.timestamp()),
        'formatted': current_time.strftime('%d/%m/%Y %H:%M:%S'),
        'timezone': 'America/Sao_Paulo'
    })

@api_bp.route('/time/status', methods=['GET'])
def get_time_status():
    """Obter status da sincronização de horário"""
    time_sync = get_time_sync()
    status = time_sync.get_sync_status()
    
    return jsonify({
        'success': True,
        **status
    })

@api_bp.route('/time/sync', methods=['POST'])
def force_time_sync():
    """Forçar sincronização com a API externa"""
    time_sync = get_time_sync()
    success = time_sync.sync_time()
    
    if success:
        status = time_sync.get_sync_status()
        return jsonify({
            'success': True,
            'message': 'Hora sincronizada com sucesso',
            **status
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Falha ao sincronizar com a API'
        }), 500

# ===== API - CAIXA =====

@api_bp.route('/caixa/status', methods=['GET'])
def caixa_status():
    """Verificar se há caixa aberto"""
    caixa = Caixa.query.filter_by(status='aberto').first()
    
    if caixa:
        return jsonify({
            'aberto': True,
            'caixa': caixa.to_dict()
        })
    
    return jsonify({'aberto': False})

@api_bp.route('/caixa/abrir', methods=['POST'])
def abrir_caixa():
    """Abrir um novo caixa"""
    # Verificar se já existe caixa aberto
    caixa_aberto = Caixa.query.filter_by(status='aberto').first()
    if caixa_aberto:
        return jsonify({'success': False, 'message': 'Já existe um caixa aberto'}), 400
    
    data = request.json
    
    caixa = Caixa(
        operador=data.get('operador', ''),
        troco_inicial=float(data.get('troco_inicial', 0)),
        status='aberto'
    )
    
    db.session.add(caixa)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Caixa aberto com sucesso',
        'caixa': caixa.to_dict()
    })

@api_bp.route('/caixa/fechar', methods=['POST'])
def fechar_caixa():
    """Fechar o caixa atual"""
    caixa = Caixa.query.filter_by(status='aberto').first()
    
    if not caixa:
        return jsonify({'success': False, 'message': 'Não há caixa aberto'}), 400
    
    data = request.json
    
    caixa.data_fechamento = datetime.now()
    caixa.status = 'fechado'
    
    # Calcular total de vendas para notificação
    totais = caixa.calcular_totais()
    total_vendas = totais['total_entradas']
    
    if 'valor_contado' in data:
        valor_contado = float(data['valor_contado'])
        caixa.valor_contado = valor_contado
        # A diferença deve ser calculada em relação ao saldo em dinheiro, não ao saldo total
        saldo_dinheiro = caixa.calcular_saldo_dinheiro()
        caixa.diferenca = valor_contado - saldo_dinheiro
    
    if 'observacao' in data:
        caixa.observacao = data['observacao']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Caixa fechado com sucesso',
        'caixa': caixa.to_dict()
    })

@api_bp.route('/caixa/painel', methods=['GET'])
def painel_caixa():
    """Obter dados do painel do caixa atual"""
    caixa = Caixa.query.filter_by(status='aberto').first()
    
    if not caixa:
        return jsonify({'success': False, 'message': 'Não há caixa aberto'}), 400
    
    totais = caixa.calcular_totais()
    
    # Resumo por forma de pagamento
    vendas = Lancamento.query.filter_by(
        caixa_id=caixa.id,
        tipo='entrada',
        categoria='venda'
    ).filter(Lancamento.estorno == None).all()
    
    resumo_pagamentos = {}
    for venda in vendas:
        forma = venda.forma_pagamento or 'Não informado'
        resumo_pagamentos[forma] = resumo_pagamentos.get(forma, 0) + venda.valor
    
    # Resumo por categoria
    lancamentos = Lancamento.query.filter_by(caixa_id=caixa.id).all()
    
    resumo_categorias = {}
    for lanc in lancamentos:
        if lanc.estorno:
            continue
        cat = lanc.categoria
        resumo_categorias[cat] = resumo_categorias.get(cat, 0) + lanc.valor
    
    return jsonify({
        'success': True,
        'caixa': caixa.to_dict(),
        'totais': totais,
        'resumo_pagamentos': resumo_pagamentos,
        'resumo_categorias': resumo_categorias
    })

@api_bp.route('/caixa/resumo-fechamento', methods=['GET'])
def resumo_fechamento():
    """Obter resumo detalhado para fechamento do caixa"""
    caixa = Caixa.query.filter_by(status='aberto').first()
    
    if not caixa:
        return jsonify({'success': False, 'message': 'Não há caixa aberto'}), 400
    
    lancamentos = Lancamento.query.filter_by(caixa_id=caixa.id).all()
    
    # Separar por forma de pagamento
    vendas_dinheiro = 0
    vendas_pix = 0
    vendas_cartao_credito = 0
    vendas_cartao_debito = 0
    vendas_outras = 0
    total_troco_dado = 0
    
    total_sangrias = 0
    total_suprimentos = 0
    total_outros_entrada = 0
    total_outros_saida = 0
    total_estornos_dinheiro = 0
    
    for lanc in lancamentos:
        if lanc.estorno:
            continue
        if lanc.categoria == 'venda':
            forma = (lanc.forma_pagamento or '').lower()
            if 'dinheiro' in forma:
                vendas_dinheiro += lanc.valor
                # Somar troco dado (sai do caixa físico)
                if lanc.troco and lanc.troco > 0:
                    total_troco_dado += lanc.troco
            elif 'pix' in forma:
                vendas_pix += lanc.valor
            elif 'crédito' in forma or 'credito' in forma:
                vendas_cartao_credito += lanc.valor
            elif 'débito' in forma or 'debito' in forma:
                vendas_cartao_debito += lanc.valor
            else:
                vendas_outras += lanc.valor
        elif lanc.categoria == 'sangria':
            total_sangrias += lanc.valor
        elif lanc.categoria == 'suprimento':
            total_suprimentos += lanc.valor
        elif lanc.categoria == 'outros':
            if lanc.tipo == 'entrada':
                total_outros_entrada += lanc.valor
            else:
                total_outros_saida += lanc.valor
        elif lanc.categoria == 'estorno':
            forma = (lanc.forma_pagamento or '').lower()
            if 'dinheiro' in forma:
                total_estornos_dinheiro += lanc.valor
    
    # Total de vendas
    total_vendas = vendas_dinheiro + vendas_pix + vendas_cartao_credito + vendas_cartao_debito + vendas_outras
    
    # Usar o método do modelo para calcular dinheiro esperado
    dinheiro_esperado = caixa.calcular_saldo_dinheiro()
    
    return jsonify({
        'success': True,
        'troco_inicial': caixa.troco_inicial,
        'vendas': {
            'dinheiro': vendas_dinheiro,
            'pix': vendas_pix,
            'cartao_credito': vendas_cartao_credito,
            'cartao_debito': vendas_cartao_debito,
            'outras': vendas_outras,
            'total': total_vendas
        },
        'movimentacoes': {
            'sangrias': total_sangrias,
            'suprimentos': total_suprimentos,
            'troco_dado': total_troco_dado,
            'outros_entrada': total_outros_entrada,
            'outros_saida': total_outros_saida
        },
        'dinheiro_esperado': dinheiro_esperado
    })

# ===== API - LANÇAMENTOS =====

@api_bp.route('/lancamento', methods=['POST'])
def criar_lancamento():
    """Criar novo lançamento"""
    caixa = Caixa.query.filter_by(status='aberto').first()
    
    if not caixa:
        return jsonify({'success': False, 'message': 'Não há caixa aberto'}), 400
    
    data = request.json
    
    # Validações
    if 'tipo' not in data or 'categoria' not in data or 'valor' not in data:
        return jsonify({'success': False, 'message': 'Dados incompletos'}), 400
    
    valor = float(data['valor'])
    
    lancamento = Lancamento(
        caixa_id=caixa.id,
        tipo=data['tipo'],
        categoria=data['categoria'],
        valor=valor,
        forma_pagamento=data.get('forma_pagamento'),
        descricao=data.get('descricao')
    )
    
    # Calcular troco para vendas em dinheiro
    if data['categoria'] == 'venda' and 'valor_recebido' in data:
        valor_recebido = float(data['valor_recebido'])
        lancamento.valor_recebido = valor_recebido
        lancamento.troco = valor_recebido - valor
    
    db.session.add(lancamento)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Lançamento criado com sucesso',
        'lancamento': lancamento.to_dict()
    })

@api_bp.route('/lancamento/<int:id>', methods=['DELETE'])
def deletar_lancamento(id):
    """Deletar um lançamento"""
    lancamento = Lancamento.query.get(id)
    
    if not lancamento:
        return jsonify({'success': False, 'message': 'Lançamento não encontrado'}), 404
    
    # Verificar se o caixa ainda está aberto
    if lancamento.caixa.status != 'aberto':
        return jsonify({'success': False, 'message': 'Não é possível deletar lançamento de caixa fechado'}), 400
    
    db.session.delete(lancamento)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Lançamento deletado com sucesso'})

# ===== API - HISTÓRICO =====

@api_bp.route('/lancamentos', methods=['GET'])
def listar_lancamentos():
    """Listar lançamentos com filtros"""
    # Parâmetros de filtro
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    tipo = request.args.get('tipo')
    categoria = request.args.get('categoria')
    caixa_id = request.args.get('caixa_id')
    
    query = Lancamento.query
    
    if caixa_id:
        query = query.filter_by(caixa_id=int(caixa_id))
    
    if data_inicio:
        data_inicio_dt = datetime.fromisoformat(data_inicio)
        query = query.filter(Lancamento.data_hora >= data_inicio_dt)
    
    if data_fim:
        data_fim_dt = datetime.fromisoformat(data_fim)
        query = query.filter(Lancamento.data_hora <= data_fim_dt)
    
    if tipo:
        query = query.filter_by(tipo=tipo)
    
    if categoria:
        query = query.filter_by(categoria=categoria)
    
    lancamentos = query.order_by(Lancamento.data_hora.desc()).all()
    
    return jsonify({
        'success': True,
        'lancamentos': [l.to_dict() for l in lancamentos]
    })

@api_bp.route('/caixas', methods=['GET'])
def listar_caixas():
    """Listar todos os caixas"""
    status = request.args.get('status')
    
    query = Caixa.query
    
    if status:
        query = query.filter_by(status=status)
    
    caixas = query.order_by(Caixa.data_abertura.desc()).all()
    
    return jsonify({
        'success': True,
        'caixas': [c.to_dict() for c in caixas]
    })

@api_bp.route('/caixa/<int:id>', methods=['GET'])
def detalhes_caixa(id):
    """Obter detalhes completos de um caixa"""
    caixa = Caixa.query.get(id)
    
    if not caixa:
        return jsonify({'success': False, 'message': 'Caixa não encontrado'}), 404
    
    lancamentos = Lancamento.query.filter_by(caixa_id=id).order_by(Lancamento.data_hora).all()
    
    return jsonify({
        'success': True,
        'caixa': caixa.to_dict(),
        'lancamentos': [l.to_dict() for l in lancamentos]
    })

# ===== API - RELATÓRIOS =====

@api_bp.route('/relatorio/resumo', methods=['GET'])
def relatorio_resumo():
    """Gerar relatório resumido por período"""
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    if not data_inicio or not data_fim:
        return jsonify({'success': False, 'message': 'Período não informado'}), 400
    
    data_inicio_dt = datetime.fromisoformat(data_inicio)
    data_fim_dt = datetime.fromisoformat(data_fim)
    
    # Total de entradas e saídas
    total_entradas = db.session.query(func.sum(Lancamento.valor)).filter(
        and_(
            Lancamento.tipo == 'entrada',
            Lancamento.data_hora >= data_inicio_dt,
            Lancamento.data_hora <= data_fim_dt
        )
    ).scalar() or 0
    
    total_saidas = db.session.query(func.sum(Lancamento.valor)).filter(
        and_(
            Lancamento.tipo == 'saida',
            Lancamento.data_hora >= data_inicio_dt,
            Lancamento.data_hora <= data_fim_dt
        )
    ).scalar() or 0
    
    # Resumo por categoria
    categorias = db.session.query(
        Lancamento.categoria,
        Lancamento.tipo,
        func.sum(Lancamento.valor).label('total')
    ).filter(
        and_(
            Lancamento.data_hora >= data_inicio_dt,
            Lancamento.data_hora <= data_fim_dt
        )
    ).group_by(Lancamento.categoria, Lancamento.tipo).all()
    
    # Resumo por forma de pagamento (apenas vendas)
    pagamentos = db.session.query(
        Lancamento.forma_pagamento,
        func.sum(Lancamento.valor).label('total')
    ).filter(
        and_(
            Lancamento.categoria == 'venda',
            Lancamento.estorno == None,
            Lancamento.data_hora >= data_inicio_dt,
            Lancamento.data_hora <= data_fim_dt
        )
    ).group_by(Lancamento.forma_pagamento).all()
    
    return jsonify({
        'success': True,
        'periodo': {
            'inicio': data_inicio,
            'fim': data_fim
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
        ]
    })


# ===== API - GERENTE (Dashboard Mobile) =====

@api_bp.route('/gerente/resumo-hoje', methods=['GET'])
def resumo_hoje():
    """Resumo por data para o painel do gerente"""
    data_param = request.args.get('data')
    hoje = datetime.now().date()

    if data_param:
        try:
            dia_requisitado = datetime.fromisoformat(data_param).date()
        except ValueError:
            return jsonify({'success': False, 'message': 'Data inválida'}), 400
    else:
        dia_requisitado = hoje

    inicio_dia = datetime.combine(dia_requisitado, datetime.min.time())
    fim_dia = datetime.combine(dia_requisitado, datetime.max.time())

    caixas_dia = Caixa.query.filter(
        Caixa.data_abertura >= inicio_dia,
        Caixa.data_abertura <= fim_dia
    ).all()

    lancamentos = Lancamento.query.filter(
        Lancamento.data_hora >= inicio_dia,
        Lancamento.data_hora <= fim_dia
    ).all()

    vendas_dinheiro = 0
    vendas_pix = 0
    vendas_cartao_credito = 0
    vendas_cartao_debito = 0
    vendas_outras = 0
    total_sangrias = 0
    total_suprimentos = 0
    total_troco_dado = 0
    total_outros_entrada = 0
    total_outros_saida = 0
    total_estornos_dinheiro = 0

    for lanc in lancamentos:
        if lanc.estorno:
            continue
        if lanc.categoria == 'venda':
            forma = (lanc.forma_pagamento or '').lower()
            if 'dinheiro' in forma:
                vendas_dinheiro += lanc.valor
                if lanc.troco and lanc.troco > 0:
                    total_troco_dado += lanc.troco
            elif 'pix' in forma:
                vendas_pix += lanc.valor
            elif 'crédito' in forma or 'credito' in forma:
                vendas_cartao_credito += lanc.valor
            elif 'débito' in forma or 'debito' in forma:
                vendas_cartao_debito += lanc.valor
            else:
                vendas_outras += lanc.valor
        elif lanc.categoria == 'sangria':
            total_sangrias += lanc.valor
        elif lanc.categoria == 'suprimento':
            total_suprimentos += lanc.valor
        elif lanc.categoria == 'estorno':
            forma = (lanc.forma_pagamento or '').lower()
            if 'dinheiro' in forma:
                total_estornos_dinheiro += lanc.valor
        elif lanc.categoria == 'outros':
            if lanc.tipo == 'entrada':
                total_outros_entrada += lanc.valor
            else:
                total_outros_saida += lanc.valor

    total_vendas = (
        vendas_dinheiro + vendas_pix + vendas_cartao_credito +
        vendas_cartao_debito + vendas_outras
    )

    troco_inicial_total = sum((c.troco_inicial or 0) for c in caixas_dia)
    dinheiro_esperado = (
        troco_inicial_total
        + vendas_dinheiro
        - total_troco_dado
        - total_sangrias
        + total_suprimentos
        + total_outros_entrada
        - total_outros_saida
        - total_estornos_dinheiro
    )

    caixa_atual = Caixa.query.filter_by(status='aberto').first()

    return jsonify({
        'success': True,
        'data': dia_requisitado.isoformat(),
        'periodo': {
            'data': dia_requisitado.isoformat(),
            'display': dia_requisitado.strftime('%d/%m/%Y')
        },
        'caixa_aberto': caixa_atual is not None,
        'caixa_atual': caixa_atual.to_dict() if caixa_atual else None,
        'total_vendas': total_vendas,
        'saldo_final_dinheiro': dinheiro_esperado,
        'vendas': {
            'dinheiro': vendas_dinheiro,
            'pix': vendas_pix,
            'cartao_credito': vendas_cartao_credito,
            'cartao_debito': vendas_cartao_debito
        },
        'movimentacoes': {
            'sangrias': total_sangrias,
            'suprimentos': total_suprimentos,
            'troco_dado': total_troco_dado,
            'outros_entrada': total_outros_entrada,
            'outros_saida': total_outros_saida
        },
        'qtd_caixas': len(caixas_dia),
        'qtd_lancamentos': len(lancamentos)
    })


@api_bp.route('/gerente/ultimas-movimentacoes', methods=['GET'])
def ultimas_movimentacoes():
    """Últimas movimentações em tempo real"""
    limite = request.args.get('limite', 20, type=int)
    
    lancamentos = Lancamento.query.order_by(
        Lancamento.data_hora.desc()
    ).limit(limite).all()
    
    return jsonify({
        'success': True,
        'lancamentos': [l.to_dict() for l in lancamentos]
    })


@api_bp.route('/gerente/datas-com-movimento', methods=['GET'])
def datas_com_movimento():
    """Retorna lista de datas que possuem movimentações (últimos 30 dias)"""
    try:
        from datetime import timedelta
        data_limite = datetime.now() - timedelta(days=30)
        
        # Buscar datas únicas com lançamentos
        datas = db.session.query(
            func.date(Lancamento.data_hora).label('data')
        ).filter(
            Lancamento.data_hora >= data_limite
        ).distinct().all()
        
        # Converter para lista de strings ISO
        datas_formatadas = [d.data for d in datas if d.data]
        
        return jsonify({
            'success': True,
            'datas': datas_formatadas
        })
    except Exception as e:
        print(f"Erro ao buscar datas com movimento: {e}")
        return jsonify({
            'success': False,
            'message': str(e),
            'datas': []
        }), 500


@api_bp.route('/gerente/estornar-venda', methods=['POST'])
def estornar_venda():
    """Registra o estorno de uma venda"""
    data = request.json or {}
    lancamento_id = data.get('lancamento_id')
    motivo = (data.get('motivo') or '').strip()

    if not lancamento_id:
        return jsonify({'success': False, 'message': 'ID da venda obrigatório'}), 400
    if not motivo:
        return jsonify({'success': False, 'message': 'Motivo do estorno obrigatório'}), 400

    lancamento = Lancamento.query.get(lancamento_id)

    if not lancamento or lancamento.categoria != 'venda' or lancamento.tipo != 'entrada':
        return jsonify({'success': False, 'message': 'Venda não encontrada'}), 404

    if lancamento.estorno:
        return jsonify({'success': False, 'message': 'Venda já estornada'}), 400

    caixa = lancamento.caixa
    if not caixa:
        return jsonify({'success': False, 'message': 'Caixa associado à venda não encontrado'}), 400

    estorno_lancamento = Lancamento(
        caixa_id=caixa.id,
        tipo='saida',
        categoria='estorno',
        valor=lancamento.valor,
        forma_pagamento=lancamento.forma_pagamento,
        descricao=f'Estorno da venda #{lancamento.id}: {motivo}'
    )

    estorno_registro = Estorno(
        lancamento=lancamento,
        motivo=motivo
    )

    db.session.add(estorno_lancamento)
    db.session.add(estorno_registro)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Venda estornada com sucesso',
        'venda': lancamento.to_dict(),
        'estorno': estorno_registro.to_dict()
    })


@api_bp.route('/gerente/sangrias-hoje', methods=['GET'])
def sangrias_hoje():
    """Lista todas as sangrias do dia"""
    hoje = datetime.now().date()
    inicio_dia = datetime.combine(hoje, datetime.min.time())
    fim_dia = datetime.combine(hoje, datetime.max.time())
    
    sangrias = Lancamento.query.filter(
        Lancamento.categoria == 'sangria',
        Lancamento.data_hora >= inicio_dia,
        Lancamento.data_hora <= fim_dia
    ).order_by(Lancamento.data_hora.desc()).all()
    
    return jsonify({
        'success': True,
        'sangrias': [s.to_dict() for s in sangrias],
        'total': sum(s.valor for s in sangrias)
    })


@api_bp.route('/gerente/resumo-semana', methods=['GET'])
def resumo_semana():
    """Resumo dos últimos 7 dias"""
    hoje = datetime.now().date()
    inicio_semana = hoje - timedelta(days=6)
    
    dias = []
    for i in range(7):
        dia = inicio_semana + timedelta(days=i)
        inicio_dia = datetime.combine(dia, datetime.min.time())
        fim_dia = datetime.combine(dia, datetime.max.time())
        
        total_vendas = db.session.query(func.sum(Lancamento.valor)).filter(
            and_(
                Lancamento.categoria == 'venda',
                Lancamento.estorno == None,
                Lancamento.data_hora >= inicio_dia,
                Lancamento.data_hora <= fim_dia
            )
        ).scalar() or 0
        
        dias.append({
            'data': dia.isoformat(),
            'dia_semana': dia.strftime('%a'),
            'total': float(total_vendas)
        })
    
    return jsonify({
        'success': True,
        'dias': dias,
        'total_semana': sum(d['total'] for d in dias)
    })



# ===== API - RELATÓRIOS PDF =====

@api_bp.route('/relatorio/caixa/<int:id>/pdf', methods=['GET'])
def relatorio_caixa_pdf(id):
    """Gerar PDF de um caixa específico"""
    caixa = Caixa.query.get(id)
    
    if not caixa:
        return jsonify({'success': False, 'message': 'Caixa não encontrado'}), 404
    
    lancamentos = Lancamento.query.filter_by(caixa_id=id).order_by(Lancamento.data_hora).all()
    
    config = Configuracao.get_config()
    
    pdf_buffer = gerar_relatorio_caixa_pdf(
        caixa.to_dict(),
        [l.to_dict() for l in lancamentos],
        config.nome_loja
    )
    
    filename = f"relatorio_caixa_{id}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    
    return Response(
        pdf_buffer.getvalue(),
        mimetype='application/pdf',
        headers={
            'Content-Disposition': f'attachment; filename={filename}',
            'Content-Type': 'application/pdf'
        }
    )


@api_bp.route('/relatorio/caixa/<int:id>/cupom', methods=['GET'])
def cupom_termico_caixa(id):
    """Gerar cupom térmico para impressora 80mm (Elgin I9 e similares)"""
    caixa = Caixa.query.get(id)
    
    if not caixa:
        return jsonify({'success': False, 'message': 'Caixa não encontrado'}), 404
    
    lancamentos = Lancamento.query.filter_by(caixa_id=id).order_by(Lancamento.data_hora).all()
    
    config = Configuracao.get_config()
    
    pdf_buffer = gerar_cupom_termico_caixa(
        caixa.to_dict(),
        [l.to_dict() for l in lancamentos],
        config.nome_loja
    )
    
    filename = f"cupom_caixa_{id}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    
    return Response(
        pdf_buffer.getvalue(),
        mimetype='application/pdf',
        headers={
            'Content-Disposition': f'inline; filename={filename}',
            'Content-Type': 'application/pdf'
        }
    )


@api_bp.route('/relatorio/periodo/pdf', methods=['GET'])
def relatorio_periodo_pdf():
    """Gerar PDF de relatório por período"""
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    if not data_inicio or not data_fim:
        return jsonify({'success': False, 'message': 'Período não informado'}), 400
    
    data_inicio_dt = datetime.fromisoformat(data_inicio)
    data_fim_dt = datetime.fromisoformat(data_fim)
    
    # Buscar dados do relatório
    total_entradas = db.session.query(func.sum(Lancamento.valor)).filter(
        and_(
            Lancamento.tipo == 'entrada',
            Lancamento.data_hora >= data_inicio_dt,
            Lancamento.data_hora <= data_fim_dt
        )
    ).scalar() or 0
    
    total_saidas = db.session.query(func.sum(Lancamento.valor)).filter(
        and_(
            Lancamento.tipo == 'saida',
            Lancamento.data_hora >= data_inicio_dt,
            Lancamento.data_hora <= data_fim_dt
        )
    ).scalar() or 0
    
    categorias = db.session.query(
        Lancamento.categoria,
        Lancamento.tipo,
        func.sum(Lancamento.valor).label('total')
    ).filter(
        and_(
            Lancamento.data_hora >= data_inicio_dt,
            Lancamento.data_hora <= data_fim_dt
        )
    ).group_by(Lancamento.categoria, Lancamento.tipo).all()
    
    pagamentos = db.session.query(
        Lancamento.forma_pagamento,
        func.sum(Lancamento.valor).label('total')
    ).filter(
        and_(
            Lancamento.categoria == 'venda',
            Lancamento.estorno == None,
            Lancamento.data_hora >= data_inicio_dt,
            Lancamento.data_hora <= data_fim_dt
        )
    ).group_by(Lancamento.forma_pagamento).all()
    
    # Buscar todos os lançamentos do período
    lancamentos = Lancamento.query.filter(
        and_(
            Lancamento.data_hora >= data_inicio_dt,
            Lancamento.data_hora <= data_fim_dt
        )
    ).order_by(Lancamento.data_hora).all()
    
    dados_relatorio = {
        'periodo': {
            'inicio': data_inicio,
            'fim': data_fim
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
    
    config = Configuracao.get_config()
    
    pdf_buffer = gerar_relatorio_periodo_pdf(dados_relatorio, config.nome_loja)
    
    filename = f"relatorio_{data_inicio}_{data_fim}.pdf"
    
    return Response(
        pdf_buffer.getvalue(),
        mimetype='application/pdf',
        headers={
            'Content-Disposition': f'attachment; filename={filename}',
            'Content-Type': 'application/pdf'
        }
    )


@api_bp.route('/relatorio/resumo-diario/pdf', methods=['GET'])
def resumo_diario_pdf():
    """Gerar PDF do resumo diário"""
    data_str = request.args.get('data', datetime.now().strftime('%Y-%m-%d'))
    
    try:
        data = datetime.strptime(data_str, '%Y-%m-%d').date()
    except:
        data = datetime.now().date()
    
    inicio_dia = datetime.combine(data, datetime.min.time())
    fim_dia = datetime.combine(data, datetime.max.time())
    
    lancamentos = Lancamento.query.filter(
        Lancamento.data_hora >= inicio_dia,
        Lancamento.data_hora <= fim_dia
    ).order_by(Lancamento.data_hora).all()
    
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
        'data': data_str,
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
        },
        'lancamentos': [l.to_dict() for l in lancamentos]
    }
    
    config = Configuracao.get_config()
    
    pdf_buffer = gerar_resumo_diario_pdf(data_resumo, config.nome_loja)
    
    filename = f"resumo_diario_{data_str}.pdf"
    
    return Response(
        pdf_buffer.getvalue(),
        mimetype='application/pdf',
        headers={
            'Content-Disposition': f'attachment; filename={filename}',
            'Content-Type': 'application/pdf'
        }
    )
