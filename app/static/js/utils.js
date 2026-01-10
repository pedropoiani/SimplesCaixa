/**
 * Funcoes utilitarias - ES5 Compativel (iOS 9+)
 * Versao: 1.0.1 - 09/01/2026
 */

// Formatar valor em Real (compativel com navegadores antigos)
function formatarMoeda(valor) {
    if (typeof valor !== 'number') {
        valor = parseFloat(valor) || 0;
    }
    
    // Fallback para navegadores sem Intl
    if (typeof Intl === 'undefined' || !Intl.NumberFormat) {
        var fixo = valor.toFixed(2);
        var partes = fixo.split('.');
        var inteiro = partes[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.');
        return 'R$ ' + inteiro + ',' + partes[1];
    }
    
    try {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        }).format(valor);
    } catch (e) {
        var fixo = valor.toFixed(2);
        var partes = fixo.split('.');
        var inteiro = partes[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.');
        return 'R$ ' + inteiro + ',' + partes[1];
    }
}

// Formatar data e hora
function formatarDataHora(dataStr) {
    if (!dataStr) return '';
    var data = new Date(dataStr);
    
    if (isNaN(data.getTime())) return '';
    
    var dia = ('0' + data.getDate()).slice(-2);
    var mes = ('0' + (data.getMonth() + 1)).slice(-2);
    var ano = data.getFullYear();
    var hora = ('0' + data.getHours()).slice(-2);
    var min = ('0' + data.getMinutes()).slice(-2);
    
    return dia + '/' + mes + '/' + ano + ' ' + hora + ':' + min;
}

// Formatar data
function formatarData(dataStr) {
    if (!dataStr) return '';
    var data = new Date(dataStr);
    
    if (isNaN(data.getTime())) return '';
    
    var dia = ('0' + data.getDate()).slice(-2);
    var mes = ('0' + (data.getMonth() + 1)).slice(-2);
    var ano = data.getFullYear();
    
    return dia + '/' + mes + '/' + ano;
}

// Mostrar mensagem de sucesso
function mostrarSucesso(mensagem) {
    alert('OK: ' + mensagem);
}

// Mostrar mensagem de erro
function mostrarErro(mensagem) {
    alert('Erro: ' + mensagem);
}

// Confirmar acao
function confirmar(mensagem) {
    return confirm(mensagem);
}

// Modal generico
function criarModal(titulo, conteudo, botoes) {
    botoes = botoes || [];
    var modalId = 'modal-' + Date.now();
    
    var modal = document.createElement('div');
    modal.id = modalId;
    modal.className = 'modal';
    
    var botoesHtml = '';
    for (var i = 0; i < botoes.length; i++) {
        var botao = botoes[i];
        botoesHtml += '<button class="btn btn-' + botao.tipo + '" onclick="' + botao.acao + '">' + botao.texto + '</button>';
    }
    
    modal.innerHTML = '<div class="modal-content">' +
        '<div class="modal-header">' +
            '<h3>' + titulo + '</h3>' +
            '<button class="modal-close" onclick="fecharModal(\'' + modalId + '\')">&times;</button>' +
        '</div>' +
        '<div class="modal-body">' + conteudo + '</div>' +
        (botoesHtml ? '<div class="modal-footer">' + botoesHtml + '</div>' : '') +
    '</div>';
    
    var container = document.getElementById('modalsContainer');
    if (container) {
        container.appendChild(modal);
    }
    
    // Mostrar modal
    setTimeout(function() {
        modal.classList.add('show');
    }, 10);
    
    // Fechar ao clicar fora
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            fecharModal(modalId);
        }
    });
    
    return modalId;
}

function fecharModal(modalId) {
    var modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('show');
        setTimeout(function() {
            if (modal.parentNode) {
                modal.parentNode.removeChild(modal);
            }
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
    var data = new Date();
    data.setDate(data.getDate() - dias);
    return data.toISOString().split('T')[0];
}

// Exportar para CSV
function exportarCSV(dados, colunas, nomeArquivo) {
    if (!dados || dados.length === 0) {
        mostrarErro('Nao ha dados para exportar');
        return;
    }
    
    // Cabecalho
    var cabecalhos = [];
    for (var c = 0; c < colunas.length; c++) {
        cabecalhos.push(colunas[c].titulo);
    }
    var csv = cabecalhos.join(';') + '\n';
    
    // Dados
    for (var i = 0; i < dados.length; i++) {
        var item = dados[i];
        var linha = [];
        
        for (var j = 0; j < colunas.length; j++) {
            var col = colunas[j];
            var valor = item[col.campo];
            
            // Formatar valor se necessario
            if (col.formato === 'moeda') {
                valor = formatarMoeda(valor);
            } else if (col.formato === 'data') {
                valor = formatarData(valor);
            } else if (col.formato === 'dataHora') {
                valor = formatarDataHora(valor);
            }
            
            // Escapar valores
            linha.push('"' + (valor || '') + '"');
        }
        
        csv += linha.join(';') + '\n';
    }
    
    // Download
    var blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    var link = document.createElement('a');
    var url = URL.createObjectURL(blob);
    
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
    var timeout;
    return function() {
        var context = this;
        var args = arguments;
        var later = function() {
            clearTimeout(timeout);
            func.apply(context, args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
