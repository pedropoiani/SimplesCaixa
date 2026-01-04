/**
 * API Client
 */

const API_BASE = '/api';

const API = {
    // Configuração
    async getConfiguracao() {
        const res = await fetch(`${API_BASE}/configuracao`);
        return await res.json();
    },
    
    async updateConfiguracao(data) {
        const res = await fetch(`${API_BASE}/configuracao`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return await res.json();
    },
    
    // Caixa
    async caixaStatus() {
        const res = await fetch(`${API_BASE}/caixa/status`);
        return await res.json();
    },
    
    async abrirCaixa(data) {
        const res = await fetch(`${API_BASE}/caixa/abrir`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return await res.json();
    },
    
    async fecharCaixa(data) {
        const res = await fetch(`${API_BASE}/caixa/fechar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return await res.json();
    },
    
    async painelCaixa() {
        const res = await fetch(`${API_BASE}/caixa/painel`);
        return await res.json();
    },
    
    async resumoFechamento() {
        const res = await fetch(`${API_BASE}/caixa/resumo-fechamento`);
        return await res.json();
    },
    
    // Lançamentos
    async criarLancamento(data) {
        const res = await fetch(`${API_BASE}/lancamento`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return await res.json();
    },
    
    async deletarLancamento(id) {
        const res = await fetch(`${API_BASE}/lancamento/${id}`, {
            method: 'DELETE'
        });
        return await res.json();
    },
    
    async listarLancamentos(filtros = {}) {
        const params = new URLSearchParams(filtros);
        const res = await fetch(`${API_BASE}/lancamentos?${params}`);
        return await res.json();
    },
    
    // Caixas
    async listarCaixas(filtros = {}) {
        const params = new URLSearchParams(filtros);
        const res = await fetch(`${API_BASE}/caixas?${params}`);
        return await res.json();
    },
    
    async detalhesCaixa(id) {
        const res = await fetch(`${API_BASE}/caixa/${id}`);
        return await res.json();
    },
    
    // Relatórios
    async relatorioResumo(dataInicio, dataFim) {
        const params = new URLSearchParams({ data_inicio: dataInicio, data_fim: dataFim });
        const res = await fetch(`${API_BASE}/relatorio/resumo?${params}`);
        return await res.json();
    }
};
