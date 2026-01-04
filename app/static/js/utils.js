/**
 * Funções utilitárias
 */

// Formatar valor em Real
function formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor);
}

// Formatar data e hora
function formatarDataHora(dataStr) {
    if (!dataStr) return '';
    const data = new Date(dataStr);
    return new Intl.DateTimeFormat('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(data);
}

// Formatar data
function formatarData(dataStr) {
    if (!dataStr) return '';
    const data = new Date(dataStr);
    return new Intl.DateTimeFormat('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    }).format(data);
}

// Mostrar mensagem de sucesso
function mostrarSucesso(mensagem) {
    alert('✅ ' + mensagem);
}

// Mostrar mensagem de erro
function mostrarErro(mensagem) {
    alert('❌ ' + mensagem);
}

// Confirmar ação
function confirmar(mensagem) {
    return confirm(mensagem);
}

// Modal genérico
function criarModal(titulo, conteudo, botoes = []) {
    const modalId = 'modal-' + Date.now();
    
    const modal = document.createElement('div');
    modal.id = modalId;
    modal.className = 'modal';
    
    let botoesHtml = '';
    botoes.forEach(botao => {
        botoesHtml += `<button class="btn btn-${botao.tipo}" onclick="${botao.acao}">${botao.texto}</button>`;
    });
    
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>${titulo}</h3>
                <button class="modal-close" onclick="fecharModal('${modalId}')">&times;</button>
            </div>
            <div class="modal-body">
                ${conteudo}
            </div>
            ${botoesHtml ? `<div class="modal-footer">${botoesHtml}</div>` : ''}
        </div>
    `;
    
    document.getElementById('modalsContainer').appendChild(modal);
    
    // Mostrar modal
    setTimeout(() => {
        modal.classList.add('show');
    }, 10);
    
    // Fechar ao clicar fora
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            fecharModal(modalId);
        }
    });
    
    return modalId;
}

function fecharModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
        setTimeout(() => {
            modal.remove();
        }, 300);
    }
}

// Obter data atual em formato ISO
function getDataAtual() {
    return new Date().toISOString().split('T')[0];
}

// Obter data/hora atual em formato ISO
function getDataHoraAtual() {
    return new Date().toISOString();
}

// Calcular data passada
function getDataPassada(dias) {
    const data = new Date();
    data.setDate(data.getDate() - dias);
    return data.toISOString().split('T')[0];
}

// Exportar para CSV
function exportarCSV(dados, colunas, nomeArquivo) {
    if (!dados || dados.length === 0) {
        mostrarErro('Não há dados para exportar');
        return;
    }
    
    // Cabeçalho
    let csv = colunas.map(c => c.titulo).join(';') + '\n';
    
    // Dados
    dados.forEach(item => {
        const linha = colunas.map(c => {
            let valor = item[c.campo];
            
            // Formatar valor se necessário
            if (c.formato === 'moeda') {
                valor = formatarMoeda(valor);
            } else if (c.formato === 'data') {
                valor = formatarData(valor);
            } else if (c.formato === 'dataHora') {
                valor = formatarDataHora(valor);
            }
            
            // Escapar valores
            return `"${valor || ''}"`;
        });
        
        csv += linha.join(';') + '\n';
    });
    
    // Download
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', nomeArquivo);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    mostrarSucesso('Arquivo exportado com sucesso!');
}

// Debounce para inputs
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
