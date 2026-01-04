"""
Módulo de Push Notifications
"""
import os
import json
from pywebpush import webpush, WebPushException

# Chaves VAPID - Em produção, gere suas próprias chaves!
# Para gerar: vapid --gen
VAPID_PRIVATE_KEY = os.environ.get('VAPID_PRIVATE_KEY', 'OFuJ_KxHxr5kGn_SJ7MzT_rZVxsQxKEjPVuCNFqwXqE')
VAPID_PUBLIC_KEY = os.environ.get('VAPID_PUBLIC_KEY', 'BKpvfQvs_7V5QhKEWtJe4uBK2xAhxvxV0lz1p_Z3Q8p6VJnXMN_y3dqKxE0xVME7dqZv8jSFmLkVDnHw5LqGvqY')
VAPID_CLAIMS = {
    "sub": os.environ.get('VAPID_EMAIL', 'mailto:admin@sualojapdv.com')
}


def enviar_push(subscription_info, titulo, corpo, dados=None, icone='/static/img/icon-192.png'):
    """
    Envia uma notificação push para uma subscrição específica
    """
    try:
        payload = {
            'title': titulo,
            'body': corpo,
            'icon': icone,
            'badge': '/static/img/badge-72.png',
            'vibrate': [200, 100, 200],
            'data': dados or {},
            'tag': dados.get('tipo', 'geral') if dados else 'geral',
            'requireInteraction': True
        }
        
        webpush(
            subscription_info=subscription_info,
            data=json.dumps(payload),
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims=VAPID_CLAIMS
        )
        return True
    except WebPushException as e:
        print(f"Erro ao enviar push: {e}")
        # Se a subscrição expirou, retorna código específico
        if e.response and e.response.status_code in [404, 410]:
            return 'expired'
        return False
    except Exception as e:
        print(f"Erro inesperado ao enviar push: {e}")
        return False


def enviar_para_todos(db, PushSubscription, titulo, corpo, tipo_notificacao='geral', dados=None):
    """
    Envia notificação para todas as subscrições ativas
    tipo_notificacao: 'sangria', 'abertura', 'fechamento', 'resumo_diario'
    """
    # Filtrar subscrições ativas baseado no tipo
    query = PushSubscription.query.filter_by(ativo=True)
    
    if tipo_notificacao == 'sangria':
        query = query.filter_by(notificar_sangria=True)
    elif tipo_notificacao == 'abertura':
        query = query.filter_by(notificar_abertura=True)
    elif tipo_notificacao == 'fechamento':
        query = query.filter_by(notificar_fechamento=True)
    elif tipo_notificacao == 'resumo_diario':
        query = query.filter_by(notificar_resumo_diario=True)
    
    subscriptions = query.all()
    
    enviados = 0
    expirados = 0
    
    for sub in subscriptions:
        subscription_info = {
            'endpoint': sub.endpoint,
            'keys': {
                'p256dh': sub.p256dh,
                'auth': sub.auth
            }
        }
        
        resultado = enviar_push(
            subscription_info, 
            titulo, 
            corpo, 
            dados={'tipo': tipo_notificacao, **(dados or {})}
        )
        
        if resultado == True:
            enviados += 1
        elif resultado == 'expired':
            # Marcar subscrição como inativa
            sub.ativo = False
            expirados += 1
    
    db.session.commit()
    
    return {
        'enviados': enviados,
        'expirados': expirados,
        'total': len(subscriptions)
    }


def notificar_sangria(db, PushSubscription, valor, motivo=''):
    """Notifica sobre uma sangria realizada"""
    titulo = '💸 Sangria Realizada!'
    corpo = f'Valor: R$ {valor:.2f}'
    if motivo:
        corpo += f'\nMotivo: {motivo}'
    
    return enviar_para_todos(
        db, PushSubscription, 
        titulo, corpo, 
        'sangria',
        {'valor': valor, 'motivo': motivo}
    )


def notificar_abertura(db, PushSubscription, operador, troco_inicial):
    """Notifica sobre abertura de caixa"""
    titulo = '🔓 Caixa Aberto!'
    corpo = f'Operador: {operador or "Não informado"}\nTroco: R$ {troco_inicial:.2f}'
    
    return enviar_para_todos(
        db, PushSubscription,
        titulo, corpo,
        'abertura',
        {'operador': operador, 'troco_inicial': troco_inicial}
    )


def notificar_fechamento(db, PushSubscription, total_vendas, diferenca=None):
    """Notifica sobre fechamento de caixa"""
    titulo = '🔒 Caixa Fechado!'
    corpo = f'Total de Vendas: R$ {total_vendas:.2f}'
    if diferenca is not None:
        if diferenca > 0:
            corpo += f'\nSobra: R$ {diferenca:.2f}'
        elif diferenca < 0:
            corpo += f'\nFalta: R$ {abs(diferenca):.2f}'
        else:
            corpo += '\n✅ Caixa conferido!'
    
    return enviar_para_todos(
        db, PushSubscription,
        titulo, corpo,
        'fechamento',
        {'total_vendas': total_vendas, 'diferenca': diferenca}
    )


def notificar_resumo_diario(db, PushSubscription, resumo):
    """Envia resumo diário"""
    titulo = '📊 Resumo do Dia'
    corpo = f"Vendas: R$ {resumo['total_vendas']:.2f}\n"
    corpo += f"Sangrias: R$ {resumo['total_sangrias']:.2f}\n"
    corpo += f"Lucro líq.: R$ {resumo['lucro_liquido']:.2f}"
    
    return enviar_para_todos(
        db, PushSubscription,
        titulo, corpo,
        'resumo_diario',
        resumo
    )


def get_vapid_public_key():
    """Retorna a chave pública VAPID para o frontend"""
    return VAPID_PUBLIC_KEY
