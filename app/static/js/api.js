/**
 * API Client - ES5 Compativel (iOS 9+)
 * Versao: 1.0.1 - 09/01/2026
 */

var API_BASE = '/api';

var API = {
    // Configuracao
    getConfiguracao: function() {
        return fetch(API_BASE + '/configuracao')
            .then(function(res) {
                return res.json();
            });
    },
    
    updateConfiguracao: function(data) {
        return fetch(API_BASE + '/configuracao', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }).then(function(res) {
            return res.json();
        });
    },
    
    // Caixa
    caixaStatus: function() {
        return fetch(API_BASE + '/caixa/status')
            .then(function(res) {
                return res.json();
            });
    },
    
    abrirCaixa: function(data) {
        return fetch(API_BASE + '/caixa/abrir', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }).then(function(res) {
            return res.json();
        });
    },
    
    fecharCaixa: function(data) {
        return fetch(API_BASE + '/caixa/fechar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }).then(function(res) {
            return res.json();
        });
    },
    
    painelCaixa: function() {
        return fetch(API_BASE + '/caixa/painel')
            .then(function(res) {
                return res.json();
            });
    },
    
    resumoFechamento: function() {
        return fetch(API_BASE + '/caixa/resumo-fechamento')
            .then(function(res) {
                return res.json();
            });
    },
    
    // Lancamentos
    criarLancamento: function(data) {
        return fetch(API_BASE + '/lancamento', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }).then(function(res) {
            return res.json();
        });
    },
    
    deletarLancamento: function(id) {
        return fetch(API_BASE + '/lancamento/' + id, {
            method: 'DELETE'
        }).then(function(res) {
            return res.json();
        });
    },
    
    listarLancamentos: function(filtros) {
        filtros = filtros || {};
        var params = new URLSearchParams(filtros);
        return fetch(API_BASE + '/lancamentos?' + params.toString())
            .then(function(res) {
                return res.json();
            });
    },
    
    // Caixas
    listarCaixas: function(filtros) {
        filtros = filtros || {};
        var params = new URLSearchParams(filtros);
        return fetch(API_BASE + '/caixas?' + params.toString())
            .then(function(res) {
                return res.json();
            });
    },
    
    detalhesCaixa: function(id) {
        return fetch(API_BASE + '/caixa/' + id)
            .then(function(res) {
                return res.json();
            });
    },
    
    // Relatorios
    relatorioResumo: function(dataInicio, dataFim) {
        var params = new URLSearchParams({ data_inicio: dataInicio, data_fim: dataFim });
        return fetch(API_BASE + '/relatorio/resumo?' + params.toString())
            .then(function(res) {
                return res.json();
            });
    }
};
