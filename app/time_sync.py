"""
Módulo para obter hora sincronizada de Brasília via internet
Usa a World Time API como fonte confiável
"""
import requests
from datetime import datetime, timedelta
from threading import Lock
import pytz

class BrasiliaTimeSync:
    """
    Gerenciador de horário sincronizado de Brasília
    """
    def __init__(self):
        self.cached_time = None
        self.cached_at = None
        self.offset_seconds = 0
        self.cache_duration = 300  # 5 minutos
        self.lock = Lock()
        self.timezone = pytz.timezone('America/Sao_Paulo')
        
        # APIs alternativas (fallback)
        self.apis = [
            'http://worldtimeapi.org/api/timezone/America/Sao_Paulo',
            'http://worldtimeapi.org/api/timezone/America/Fortaleza',  # Mesmo fuso
            'http://worldtimeapi.org/api/timezone/America/Bahia',  # Mesmo fuso
        ]
    
    def get_time_from_api(self):
        """
        Busca a hora atual da API externa
        """
        for api_url in self.apis:
            try:
                response = requests.get(api_url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    # Formato: 2026-01-28T21:30:45.123456-03:00
                    datetime_str = data.get('datetime')
                    if datetime_str:
                        # Parse ISO format com timezone
                        api_time = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                        return api_time
            except Exception as e:
                print(f"⚠️  Erro ao buscar hora da API {api_url}: {e}")
                continue
        
        return None
    
    def sync_time(self):
        """
        Sincroniza com a API e calcula o offset em relação ao servidor
        """
        with self.lock:
            try:
                # Marca o tempo do servidor antes da requisição
                server_time_before = datetime.now()
                
                # Busca hora da API
                api_time = self.get_time_from_api()
                
                if api_time:
                    # Marca o tempo do servidor depois da requisição
                    server_time_after = datetime.now()
                    
                    # Calcula o tempo médio do servidor (compensando latência)
                    server_time_avg = server_time_before + (server_time_after - server_time_before) / 2
                    
                    # Remove timezone info para comparação
                    if api_time.tzinfo:
                        api_time_naive = api_time.replace(tzinfo=None)
                    else:
                        api_time_naive = api_time
                    
                    # Calcula o offset (diferença entre API e servidor)
                    self.offset_seconds = (api_time_naive - server_time_avg).total_seconds()
                    
                    # Atualiza cache
                    self.cached_time = api_time_naive
                    self.cached_at = server_time_avg
                    
                    print(f"✓ Hora sincronizada com API. Offset: {self.offset_seconds:.2f}s")
                    return True
                else:
                    print("⚠️  Não foi possível sincronizar com nenhuma API")
                    return False
                    
            except Exception as e:
                print(f"❌ Erro ao sincronizar hora: {e}")
                return False
    
    def get_current_time(self, force_sync=False):
        """
        Retorna a hora atual de Brasília sincronizada
        
        Args:
            force_sync: Força nova sincronização com a API
            
        Returns:
            datetime: Hora atual de Brasília
        """
        with self.lock:
            now = datetime.now()
            
            # Verifica se precisa sincronizar
            needs_sync = (
                force_sync or
                self.cached_at is None or
                (now - self.cached_at).total_seconds() > self.cache_duration
            )
            
            if needs_sync:
                # Tenta sincronizar em background (não bloqueia se falhar)
                self.sync_time()
            
            # Se tem cache válido, usa o offset calculado
            if self.cached_at is not None:
                adjusted_time = now + timedelta(seconds=self.offset_seconds)
                return adjusted_time
            
            # Fallback: retorna hora do servidor
            return now
    
    def get_current_time_iso(self, force_sync=False):
        """
        Retorna a hora atual em formato ISO string
        """
        return self.get_current_time(force_sync).isoformat()
    
    def get_sync_status(self):
        """
        Retorna informações sobre o status da sincronização
        """
        with self.lock:
            if self.cached_at is None:
                return {
                    'synchronized': False,
                    'message': 'Nunca sincronizado',
                    'using_server_time': True
                }
            
            now = datetime.now()
            age_seconds = (now - self.cached_at).total_seconds()
            is_fresh = age_seconds < self.cache_duration
            
            return {
                'synchronized': True,
                'last_sync': self.cached_at.isoformat(),
                'age_seconds': age_seconds,
                'is_fresh': is_fresh,
                'offset_seconds': self.offset_seconds,
                'using_server_time': not is_fresh,
                'message': f'Sincronizado há {age_seconds:.0f}s (offset: {self.offset_seconds:.2f}s)'
            }


# Instância global singleton
_time_sync = None

def get_time_sync():
    """
    Retorna a instância singleton do sincronizador
    """
    global _time_sync
    if _time_sync is None:
        _time_sync = BrasiliaTimeSync()
        # Sincroniza na primeira vez
        _time_sync.sync_time()
    return _time_sync


def get_brasilia_time():
    """
    Função de conveniência para obter a hora atual de Brasília
    """
    return get_time_sync().get_current_time()


def get_brasilia_time_iso():
    """
    Função de conveniência para obter a hora atual de Brasília em ISO format
    """
    return get_time_sync().get_current_time_iso()
