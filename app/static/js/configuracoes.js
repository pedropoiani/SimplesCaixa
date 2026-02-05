/**
 * Controle da pagina de configuracoes
 * ES5 Compativel (iOS 9+)
 * Versao: 1.0.1 - 09/01/2026
 */

var formasPagamentoAtual = [];

document.addEventListener('DOMContentLoaded', function() {
    carregarConfiguracao();
});

function carregarConfiguracao() {
    API.getConfiguracao()
        .then(function(config) {
            var nomeLoja = document.getElementById('configNomeLoja');
            var responsavel = document.getElementById('configResponsavel');
            
            if (nomeLoja) nomeLoja.value = config.nome_loja || '';
            if (responsavel) responsavel.value = config.responsavel || '';
            
            formasPagamentoAtual = config.formas_pagamento || [];
            renderizarFormasPagamento();
        })
        .catch(function(error) {
            console.error('Erro ao carregar configuracao:', error);
            mostrarErro('Erro ao carregar configuracoes');
        });
}

function renderizarFormasPagamento() {
    var container = document.getElementById('formasPagamentoLista');
    if (!container) return;
    
    if (formasPagamentoAtual.length === 0) {
        container.innerHTML = '<p class="text-center">Nenhuma forma de pagamento cadastrada</p>';
        return;
    }
    
    var html = '';
    for (var i = 0; i < formasPagamentoAtual.length; i++) {
        var forma = formasPagamentoAtual[i];
        html += '<div class="forma-pagamento-item">' +
            '<span>' + forma + '</span>' +
            '<button type="button" class="btn btn-sm btn-danger" onclick="removerFormaPagamento(' + i + ')">' +
                'Remover' +
            '</button>' +
        '</div>';
    }
    
    container.innerHTML = html;
}

function adicionarFormaPagamento() {
    var input = document.getElementById('novaFormaPagamento');
    if (!input) return;
    
    var forma = input.value.trim();
    
    if (!forma) {
        mostrarErro('Digite o nome da forma de pagamento');
        return;
    }
    
    // Verificar se ja existe
    for (var i = 0; i < formasPagamentoAtual.length; i++) {
        if (formasPagamentoAtual[i] === forma) {
            mostrarErro('Esta forma de pagamento ja existe');
            return;
        }
    }
    
    formasPagamentoAtual.push(forma);
    renderizarFormasPagamento();
    input.value = '';
}

function removerFormaPagamento(index) {
    if (!confirmar('Tem certeza que deseja remover esta forma de pagamento?')) {
        return;
    }
    
    formasPagamentoAtual.splice(index, 1);
    renderizarFormasPagamento();
}

function salvarConfiguracao(event) {
    if (event) event.preventDefault();
    
    var nomeLojaEl = document.getElementById('configNomeLoja');
    var responsavelEl = document.getElementById('configResponsavel');
    
    var nomeLoja = nomeLojaEl ? nomeLojaEl.value : '';
    var responsavel = responsavelEl ? responsavelEl.value : '';
    
    if (!nomeLoja || !responsavel) {
        mostrarErro('Preencha todos os campos obrigatorios');
        return;
    }
    
    if (formasPagamentoAtual.length === 0) {
        mostrarErro('Cadastre pelo menos uma forma de pagamento');
        return;
    }
    
    var dados = {
        nome_loja: nomeLoja,
        responsavel: responsavel,
        formas_pagamento: formasPagamentoAtual
    };
    
    API.updateConfiguracao(dados)
        .then(function(resultado) {
            if (resultado.success) {
                mostrarSucesso('Configuracoes salvas com sucesso!');
            } else {
                mostrarErro(resultado.message);
            }
        })
        .catch(function(error) {
            console.error('Erro ao salvar configuracao:', error);
            mostrarErro('Erro ao salvar configuracoes');
        });
}

