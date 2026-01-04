/**
 * Controle da página de configurações
 */

let formasPagamentoAtual = [];

document.addEventListener('DOMContentLoaded', async () => {
    await carregarConfiguracao();
});

async function carregarConfiguracao() {
    try {
        const config = await API.getConfiguracao();
        
        document.getElementById('configNomeLoja').value = config.nome_loja;
        document.getElementById('configResponsavel').value = config.responsavel;
        
        formasPagamentoAtual = config.formas_pagamento;
        renderizarFormasPagamento();
    } catch (error) {
        console.error('Erro ao carregar configuração:', error);
        mostrarErro('Erro ao carregar configurações');
    }
}

function renderizarFormasPagamento() {
    const container = document.getElementById('formasPagamentoLista');
    
    if (formasPagamentoAtual.length === 0) {
        container.innerHTML = '<p class="text-center">Nenhuma forma de pagamento cadastrada</p>';
        return;
    }
    
    container.innerHTML = formasPagamentoAtual.map((forma, index) => `
        <div class="forma-pagamento-item">
            <span>${forma}</span>
            <button type="button" class="btn btn-sm btn-danger" onclick="removerFormaPagamento(${index})">
                🗑️ Remover
            </button>
        </div>
    `).join('');
}

function adicionarFormaPagamento() {
    const input = document.getElementById('novaFormaPagamento');
    const forma = input.value.trim();
    
    if (!forma) {
        mostrarErro('Digite o nome da forma de pagamento');
        return;
    }
    
    if (formasPagamentoAtual.includes(forma)) {
        mostrarErro('Esta forma de pagamento já existe');
        return;
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

async function salvarConfiguracao(event) {
    event.preventDefault();
    
    const nomeLoja = document.getElementById('configNomeLoja').value;
    const responsavel = document.getElementById('configResponsavel').value;
    
    if (!nomeLoja || !responsavel) {
        mostrarErro('Preencha todos os campos obrigatórios');
        return;
    }
    
    if (formasPagamentoAtual.length === 0) {
        mostrarErro('Cadastre pelo menos uma forma de pagamento');
        return;
    }
    
    const dados = {
        nome_loja: nomeLoja,
        responsavel: responsavel,
        formas_pagamento: formasPagamentoAtual
    };
    
    try {
        const resultado = await API.updateConfiguracao(dados);
        
        if (resultado.success) {
            mostrarSucesso('Configurações salvas com sucesso!');
        } else {
            mostrarErro(resultado.message);
        }
    } catch (error) {
        console.error('Erro ao salvar configuração:', error);
        mostrarErro('Erro ao salvar configurações');
    }
}

async function testarNotificacao(tipo) {
    const resultadoDiv = document.getElementById('resultadoTeste');
    resultadoDiv.innerHTML = '<p class="text-info">⏳ Enviando notificação de teste...</p>';
    
    try {
        const response = await fetch('/api/push/test', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ tipo: tipo })
        });
        
        const resultado = await response.json();
        
        if (resultado.success) {
            resultadoDiv.innerHTML = `
                <div class="alert alert-success">
                    <strong>✅ Sucesso!</strong><br>
                    ${resultado.message}<br>
                    <small>Enviadas: ${resultado.resultado.enviados} | Expiradas: ${resultado.resultado.expirados} | Total: ${resultado.resultado.total}</small>
                </div>
            `;
        } else {
            resultadoDiv.innerHTML = `
                <div class="alert alert-danger">
                    <strong>❌ Erro!</strong><br>
                    ${resultado.message}
                </div>
            `;
        }
    } catch (error) {
        console.error('Erro ao testar notificação:', error);
        resultadoDiv.innerHTML = `
            <div class="alert alert-danger">
                <strong>❌ Erro!</strong><br>
                Não foi possível enviar a notificação de teste.
            </div>
        `;
    }
}
