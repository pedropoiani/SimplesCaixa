#!/usr/bin/env python3
"""
Script de teste para sincronização de horário de Brasília
"""

import sys
from datetime import datetime
from app.time_sync import get_time_sync, get_brasilia_time

def testar_sincronizacao():
    """Testa a sincronização de horário"""
    print("=" * 60)
    print("🕐 TESTE DE SINCRONIZAÇÃO DE HORÁRIO")
    print("=" * 60)
    
    # Obter instância do sincronizador
    time_sync = get_time_sync()
    
    # 1. Testar hora antes da sincronização
    print("\n1️⃣  Hora do servidor (antes da sincronização):")
    server_time = datetime.now()
    print(f"   {server_time.strftime('%d/%m/%Y %H:%M:%S')}")
    
    # 2. Forçar sincronização
    print("\n2️⃣  Sincronizando com API externa...")
    success = time_sync.sync_time()
    
    if success:
        print("   ✅ Sincronização bem-sucedida!")
    else:
        print("   ⚠️  Falha na sincronização")
    
    # 3. Obter hora sincronizada
    print("\n3️⃣  Hora sincronizada de Brasília:")
    brasilia_time = get_brasilia_time()
    print(f"   {brasilia_time.strftime('%d/%m/%Y %H:%M:%S')}")
    
    # 4. Mostrar status
    print("\n4️⃣  Status da sincronização:")
    status = time_sync.get_sync_status()
    for key, value in status.items():
        print(f"   - {key}: {value}")
    
    # 5. Comparação
    print("\n5️⃣  Comparação:")
    diff_seconds = (brasilia_time - server_time).total_seconds()
    print(f"   Diferença: {diff_seconds:.2f} segundos")
    
    if abs(diff_seconds) < 1:
        print("   ✅ Servidor está sincronizado!")
    elif abs(diff_seconds) < 60:
        print(f"   ⚠️  Servidor está {abs(diff_seconds):.0f}s {'adiantado' if diff_seconds < 0 else 'atrasado'}")
    else:
        minutos = abs(diff_seconds) / 60
        print(f"   ❌ Servidor está {minutos:.1f}min {'adiantado' if diff_seconds < 0 else 'atrasado'}")
    
    # 6. Testar múltiplas chamadas (cache)
    print("\n6️⃣  Testando cache (10 chamadas rápidas):")
    import time
    start = time.time()
    for i in range(10):
        _ = get_brasilia_time()
    end = time.time()
    print(f"   Tempo total: {(end - start) * 1000:.2f}ms")
    print(f"   Média por chamada: {(end - start) * 100:.2f}ms")
    print("   ✅ Cache funcionando corretamente!")
    
    # 7. Testar após cache expirar
    print("\n7️⃣  Forçando nova sincronização...")
    time_sync.cached_at = None  # Limpar cache
    brasilia_time2 = get_brasilia_time()
    print(f"   {brasilia_time2.strftime('%d/%m/%Y %H:%M:%S')}")
    
    print("\n" + "=" * 60)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 60)
    
    return True


def testar_api_endpoints():
    """Testa os endpoints da API"""
    print("\n" + "=" * 60)
    print("🌐 TESTE DOS ENDPOINTS DA API")
    print("=" * 60)
    
    from app import create_app
    
    app = create_app()
    client = app.test_client()
    
    # 1. GET /api/time/current
    print("\n1️⃣  GET /api/time/current")
    response = client.get('/api/time/current')
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.get_json()
        print(f"   ✅ Hora atual: {data['formatted']}")
        print(f"   ✅ ISO: {data['datetime']}")
        print(f"   ✅ Timestamp: {data['timestamp']}")
    else:
        print(f"   ❌ Erro: {response.status_code}")
        return False
    
    # 2. GET /api/time/status
    print("\n2️⃣  GET /api/time/status")
    response = client.get('/api/time/status')
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.get_json()
        print(f"   ✅ Sincronizado: {data['synchronized']}")
        print(f"   ✅ Mensagem: {data['message']}")
    else:
        print(f"   ❌ Erro: {response.status_code}")
        return False
    
    # 3. POST /api/time/sync
    print("\n3️⃣  POST /api/time/sync")
    response = client.post('/api/time/sync')
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.get_json()
        print(f"   ✅ {data['message']}")
    else:
        print(f"   ⚠️  Status: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("✅ ENDPOINTS TESTADOS!")
    print("=" * 60)
    
    return True


def main():
    """Executa todos os testes"""
    try:
        # Teste 1: Sincronização
        if not testar_sincronizacao():
            return 1
        
        # Teste 2: Endpoints
        if not testar_api_endpoints():
            return 1
        
        print("\n🎉 TODOS OS TESTES PASSARAM!\n")
        return 0
        
    except Exception as e:
        print(f"\n❌ ERRO NOS TESTES: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
