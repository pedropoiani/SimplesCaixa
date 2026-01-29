/**
 * Gerenciador de Hora Sincronizada
 * Mantém a hora atualizada com o servidor (que sincroniza com API externa)
 */

class TimeSync {
    constructor() {
        this.serverTimeOffset = 0; // Diferença entre hora do servidor e cliente
        this.lastSync = null;
        this.syncInterval = 5 * 60 * 1000; // Sincronizar a cada 5 minutos
        this.isInitialized = false;
    }

    /**
     * Inicializa o sincronizador
     */
    async init() {
        if (this.isInitialized) return;
        
        await this.sync();
        this.isInitialized = true;
        
        // Sincronizar periodicamente
        setInterval(() => this.sync(), this.syncInterval);
        
        console.log('✓ TimeSync inicializado');
    }

    /**
     * Sincroniza com o servidor
     */
    async sync() {
        try {
            const clientTimeBefore = Date.now();
            
            const response = await fetch(API_BASE + '/time/current');
            
            const clientTimeAfter = Date.now();
            
            if (response.ok) {
                const data = await response.json();
                const serverTime = new Date(data.datetime).getTime();
                
                // Calcula tempo médio do cliente (compensa latência)
                const clientTimeAvg = (clientTimeBefore + clientTimeAfter) / 2;
                
                // Calcula offset
                this.serverTimeOffset = serverTime - clientTimeAvg;
                this.lastSync = new Date();
                
                console.log(`✓ Hora sincronizada. Offset: ${(this.serverTimeOffset / 1000).toFixed(2)}s`);
                return true;
            }
        } catch (error) {
            console.error('❌ Erro ao sincronizar hora:', error);
        }
        return false;
    }

    /**
     * Retorna a hora atual sincronizada
     */
    now() {
        if (!this.lastSync) {
            // Se nunca sincronizou, usa hora do cliente
            console.warn('⚠️  Hora não sincronizada, usando hora local');
            return new Date();
        }
        
        const clientTime = Date.now();
        const syncedTime = clientTime + this.serverTimeOffset;
        return new Date(syncedTime);
    }

    /**
     * Retorna a hora atual em formato ISO
     */
    nowISO() {
        return this.now().toISOString();
    }

    /**
     * Retorna a hora atual formatada
     */
    nowFormatted(includeSeconds = true) {
        const date = this.now();
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const seconds = String(date.getSeconds()).padStart(2, '0');
        
        if (includeSeconds) {
            return `${day}/${month}/${year} ${hours}:${minutes}:${seconds}`;
        }
        return `${day}/${month}/${year} ${hours}:${minutes}`;
    }

    /**
     * Obtém status da sincronização do servidor
     */
    async getStatus() {
        try {
            const response = await fetch(API_BASE + '/time/status');
            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Erro ao obter status:', error);
        }
        return null;
    }

    /**
     * Força nova sincronização no servidor
     */
    async forceSync() {
        try {
            const response = await fetch(API_BASE + '/time/sync', {
                method: 'POST'
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log('✓ Sincronização forçada:', data.message);
                // Sincroniza o cliente também
                await this.sync();
                return true;
            }
        } catch (error) {
            console.error('Erro ao forçar sincronização:', error);
        }
        return false;
    }
}

// Instância global
const timeSync = new TimeSync();

// Inicializar quando o documento estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => timeSync.init());
} else {
    timeSync.init();
}

// Exportar para uso global
window.timeSync = timeSync;

/**
 * Função auxiliar para obter hora atual sincronizada
 * Pode ser usada em qualquer lugar do código
 */
function getCurrentTime() {
    return timeSync.now();
}

/**
 * Função auxiliar para obter data/hora ISO sincronizada
 */
function getCurrentTimeISO() {
    return timeSync.nowISO();
}
