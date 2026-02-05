/**
 * Controle da pagina de historico
 * ES5 Compativel (iOS 9+)
 * Versao: 1.0.1 - 09/01/2026
 */

document.addEventListener('DOMContentLoaded', function() {
    // Configurar datas padrao
    var dataInicio = document.getElementById('relatorioDataInicio');
    var dataFim = document.getElementById('relatorioDataFim');
    
    if (dataInicio) dataInicio.value = getDataPassada(30);
    if (dataFim) dataFim.value = getDataAtual();
    
    // Listener para periodo customizado
    var filtroPeriodo = document.getElementById('filtroLancPeriodo');
    if (filtroPeriodo) {
        filtroPeriodo.addEventListener('change', function() {
            var custom = this.value === 'customizado';
            var datasCustom = document.getElementById('filtroLancDatasCustom');
            var datasCustom2 = document.getElementById('filtroLancDatasCustom2');
            
            if (datasCustom) datasCustom.style.display = custom ? 'block' : 'none';
            if (datasCustom2) datasCustom2.style.display = custom ? 'block' : 'none';
            
            if (!custom) {
                aplicarFiltroLancamentos();
            }
        });
    }
});

// Tabs
function mostrarTabHistorico(tab) {
    var tabBtns = document.querySelectorAll('.tab-btn');
    var tabContents = document.querySelectorAll('.tab-content');
    
    for (var i = 0; i < tabBtns.length; i++) {
        tabBtns[i].classList.remove('active');
    }
    for (var j = 0; j < tabContents.length; j++) {
        tabContents[j].classList.remove('active');
    }
    
    if (event && event.target) {
        event.target.classList.add('active');
    }
    
    var tabContent = document.getElementById('tab-historico-' + tab);
    if (tabContent) tabContent.classList.add('active');
    
    // Carregar dados se necessario
    if (tab === 'caixas') {
        listarCaixas();
    }
}

// Filtros de Lancamentos
function aplicarFiltroLancamentos() {
    var periodoEl = document.getElementById('filtroLancPeriodo');
    var tipoEl = document.getElementById('filtroLancTipo');
    var categoriaEl = document.getElementById('filtroLancCategoria');
    
    var periodo = periodoEl ? periodoEl.value : 'hoje';
    var tipo = tipoEl ? tipoEl.value : '';
    var categoria = categoriaEl ? categoriaEl.value : '';
    
    var dataInicio, dataFim;
    
    if (periodo === 'customizado') {
        var dataInicioEl = document.getElementById('filtroLancDataInicio');
        var dataFimEl = document.getElementById('filtroLancDataFim');
        
        dataInicio = dataInicioEl ? dataInicioEl.value : '';
        dataFim = dataFimEl ? dataFimEl.value : '';
        
        if (!dataInicio || !dataFim) {
            mostrarErro('Informe as datas');
            return;
        }
    } else if (periodo === 'hoje') {
        dataInicio = getDataAtual();
        dataFim = getDataAtual();
    } else if (periodo === '7dias') {
        dataInicio = getDataPassada(7);
        dataFim = getDataAtual();
    } else if (periodo === '30dias') {
        dataInicio = getDataPassada(30);
        dataFim = getDataAtual();
    }
    
    var filtros = {
        data_inicio: dataInicio + 'T00:00:00',
        data_fim: dataFim + 'T23:59:59'
    };
    
    if (tipo) filtros.tipo = tipo;
    if (categoria) filtros.categoria = categoria;
    
    API.listarLancamentos(filtros)
        .then(function(resultado) {
            if (resultado.success) {
                renderizarResultadosLancamentos(resultado.lancamentos);
            } else {
                mostrarErro('Erro ao buscar lancamentos');
            }
        })
        .catch(function(error) {
            console.error('Erro ao buscar lancamentos:', error);
            mostrarErro('Erro ao buscar lancamentos');
        });
}

function renderizarResultadosLancamentos(lancamentos) {
    var container = document.getElementById('resultadosLancamentos');
    if (!container) return;
    
    if (lancamentos.length === 0) {
        container.innerHTML = '<p class="text-center">Nenhum lancamento encontrado</p>';
        return;
    }
    
    var totalEntradas = 0;
    var totalSaidas = 0;
    
    for (var i = 0; i < lancamentos.length; i++) {
        var l = lancamentos[i];
        if (l.tipo === 'entrada') {
            totalEntradas += l.valor;
        } else {
            totalSaidas += l.valor;
        }
    }
    
    var linhasHtml = '';
    for (var j = 0; j < lancamentos.length; j++) {
        var lanc = lancamentos[j];
        var tipoTexto = lanc.tipo === 'entrada' ? 'Entrada' : 'Saida';
        var cor = lanc.tipo === 'entrada' ? 'var(--success-color)' : 'var(--danger-color)';
        var sinal = lanc.tipo === 'entrada' ? '+' : '-';
        
        linhasHtml += '<tr>' +
            '<td>' + formatarDataHora(lanc.data_hora) + '</td>' +
            '<td>' + tipoTexto + '</td>' +
            '<td>' + lanc.categoria + '</td>' +
            '<td>' + (lanc.forma_pagamento || '-') + '</td>' +
            '<td>' + (lanc.descricao || '-') + '</td>' +
            '<td style="text-align: right; color: ' + cor + '">' + sinal + formatarMoeda(lanc.valor) + '</td>' +
        '</tr>';
    }
    
    var html = '<div class="painel-resumo mb-2">' +
        '<div class="resumo-item">' +
            '<div class="resumo-label">Total de Lancamentos</div>' +
            '<div class="resumo-valor">' + lancamentos.length + '</div>' +
        '</div>' +
        '<div class="resumo-item">' +
            '<div class="resumo-label">Total Entradas</div>' +
            '<div class="resumo-valor entrada-valor">' + formatarMoeda(totalEntradas) + '</div>' +
        '</div>' +
        '<div class="resumo-item">' +
            '<div class="resumo-label">Total Saidas</div>' +
            '<div class="resumo-valor saida-valor">' + formatarMoeda(totalSaidas) + '</div>' +
        '</div>' +
        '<div class="resumo-item">' +
            '<div class="resumo-label">Saldo</div>' +
            '<div class="resumo-valor saldo-valor">' + formatarMoeda(totalEntradas - totalSaidas) + '</div>' +
        '</div>' +
    '</div>' +
    '<div class="table-responsive">' +
        '<table class="table">' +
            '<thead>' +
                '<tr>' +
                    '<th>Data/Hora</th>' +
                    '<th>Tipo</th>' +
                    '<th>Categoria</th>' +
                    '<th>Forma Pgto</th>' +
                    '<th>Descricao</th>' +
                    '<th style="text-align: right;">Valor</th>' +
                '</tr>' +
            '</thead>' +
            '<tbody>' + linhasHtml + '</tbody>' +
        '</table>' +
    '</div>';
    
    container.innerHTML = html;
    window.lancamentosAtual = lancamentos;
}

function exportarLancamentosCSV() {
    if (!window.lancamentosAtual || window.lancamentosAtual.length === 0) {
        mostrarErro('Nao ha dados para exportar');
        return;
    }
    
    var colunas = [
        { campo: 'data_hora', titulo: 'Data/Hora', formato: 'dataHora' },
        { campo: 'tipo', titulo: 'Tipo' },
        { campo: 'categoria', titulo: 'Categoria' },
        { campo: 'forma_pagamento', titulo: 'Forma Pagamento' },
        { campo: 'descricao', titulo: 'Descricao' },
        { campo: 'valor', titulo: 'Valor', formato: 'moeda' }
    ];
    
    var nomeArquivo = 'lancamentos_' + getDataAtual() + '.csv';
    exportarCSV(window.lancamentosAtual, colunas, nomeArquivo);
}

// Listar Caixas
function listarCaixas() {
    var statusEl = document.getElementById('filtroCaixaStatus');
    var status = statusEl ? statusEl.value : '';
    
    var filtros = {};
    if (status) filtros.status = status;
    
    API.listarCaixas(filtros)
        .then(function(resultado) {
            if (resultado.success) {
                renderizarResultadosCaixas(resultado.caixas);
            } else {
                mostrarErro('Erro ao buscar caixas');
            }
        })
        .catch(function(error) {
            console.error('Erro ao buscar caixas:', error);
            mostrarErro('Erro ao buscar caixas');
        });
}

function renderizarResultadosCaixas(caixas) {
    var container = document.getElementById('resultadosCaixas');
    if (!container) return;
    
    if (caixas.length === 0) {
        container.innerHTML = '<p class="text-center">Nenhum caixa encontrado</p>';
        return;
    }
    
    var linhasHtml = '';
    for (var i = 0; i < caixas.length; i++) {
        var c = caixas[i];
        var statusTexto = c.status === 'aberto' ? 'Aberto' : 'Fechado';
        var statusClass = c.status === 'aberto' ? 'status-open' : 'status-closed';
        var diferencaCor = c.diferenca > 0 ? 'var(--success-color)' : (c.diferenca < 0 ? 'var(--danger-color)' : 'inherit');
        
        linhasHtml += '<tr onclick="verDetalhesCaixa(' + c.id + ')" style="cursor: pointer;">' +
            '<td>' + c.id + '</td>' +
            '<td>' + formatarDataHora(c.data_abertura) + '</td>' +
            '<td>' + (c.data_fechamento ? formatarDataHora(c.data_fechamento) : '-') + '</td>' +
            '<td>' + (c.operador || '-') + '</td>' +
            '<td><span class="status-badge ' + statusClass + '">' + statusTexto + '</span></td>' +
            '<td style="text-align: right;">' + formatarMoeda(c.troco_inicial) + '</td>' +
            '<td style="text-align: right;">' + formatarMoeda(c.saldo_atual) + '</td>' +
            '<td style="text-align: right; color: ' + diferencaCor + '">' + (c.diferenca ? formatarMoeda(c.diferenca) : '-') + '</td>' +
        '</tr>';
    }
    
    var html = '<div class="table-responsive">' +
        '<table class="table">' +
            '<thead>' +
                '<tr>' +
                    '<th>ID</th>' +
                    '<th>Abertura</th>' +
                    '<th>Fechamento</th>' +
                    '<th>Operador</th>' +
                    '<th>Status</th>' +
                    '<th style="text-align: right;">Troco Inicial</th>' +
                    '<th style="text-align: right;">Saldo Final</th>' +
                    '<th style="text-align: right;">Diferenca</th>' +
                '</tr>' +
            '</thead>' +
            '<tbody>' + linhasHtml + '</tbody>' +
        '</table>' +
    '</div>';
    
    container.innerHTML = html;
    window.caixasAtual = caixas;
}

function exportarCaixasCSV() {
    if (!window.caixasAtual || window.caixasAtual.length === 0) {
        mostrarErro('Nao ha dados para exportar');
        return;
    }
    
    var colunas = [
        { campo: 'id', titulo: 'ID' },
        { campo: 'data_abertura', titulo: 'Abertura', formato: 'dataHora' },
        { campo: 'data_fechamento', titulo: 'Fechamento', formato: 'dataHora' },
        { campo: 'operador', titulo: 'Operador' },
        { campo: 'status', titulo: 'Status' },
        { campo: 'troco_inicial', titulo: 'Troco Inicial', formato: 'moeda' },
        { campo: 'saldo_atual', titulo: 'Saldo Final', formato: 'moeda' },
        { campo: 'diferenca', titulo: 'Diferenca', formato: 'moeda' }
    ];
    
    var nomeArquivo = 'caixas_' + getDataAtual() + '.csv';
    exportarCSV(window.caixasAtual, colunas, nomeArquivo);
}

function verDetalhesCaixa(id) {
    API.detalhesCaixa(id)
        .then(function(resultado) {
            if (resultado.success) {
                mostrarModalDetalhesCaixa(resultado.caixa, resultado.lancamentos);
            } else {
                mostrarErro('Erro ao carregar detalhes');
            }
        })
        .catch(function(error) {
            console.error('Erro ao carregar detalhes:', error);
            mostrarErro('Erro ao carregar detalhes do caixa');
        });
}

function mostrarModalDetalhesCaixa(caixa, lancamentos) {
    var lancamentosHtml = '';
    if (lancamentos.length > 0) {
        for (var i = 0; i < lancamentos.length; i++) {
            var l = lancamentos[i];
            var sinal = l.tipo === 'entrada' ? '+' : '-';
            lancamentosHtml += '<div class="lancamento-item ' + l.tipo + '">' +
                '<div class="lancamento-info">' +
                    '<div class="lancamento-categoria">' + l.categoria.toUpperCase() + '</div>' +
                    '<div class="lancamento-descricao">' +
                        (l.forma_pagamento ? l.forma_pagamento + ' - ' : '') +
                        formatarDataHora(l.data_hora) +
                        (l.descricao ? '<br><small>' + l.descricao + '</small>' : '') +
                    '</div>' +
                '</div>' +
                '<div class="lancamento-valor ' + l.tipo + '">' + sinal + formatarMoeda(l.valor) + '</div>' +
            '</div>';
        }
    } else {
        lancamentosHtml = '<p class="text-center">Nenhum lancamento</p>';
    }
    
    var valorContadoHtml = '';
    if (caixa.valor_contado) {
        var diferencaCor = caixa.diferenca > 0 ? 'var(--success-color)' : (caixa.diferenca < 0 ? 'var(--danger-color)' : 'inherit');
        var diferencaTexto = caixa.diferenca > 0 ? '(Sobra)' : (caixa.diferenca < 0 ? '(Falta)' : '');
        valorContadoHtml = '<div class="info-section">' +
            '<p><strong>Saldo em Dinheiro (Esperado):</strong> ' + formatarMoeda(caixa.saldo_dinheiro || 0) + '</p>' +
            '<p><strong>Valor Contado:</strong> ' + formatarMoeda(caixa.valor_contado) + '</p>' +
            '<p><strong>Diferenca:</strong> <span style="color: ' + diferencaCor + '">' + formatarMoeda(caixa.diferenca) + ' ' + diferencaTexto + '</span></p>' +
        '</div>';
    }
    
    var conteudo = '<div class="info-section">' +
        '<h4>Informacoes do Caixa</h4>' +
        '<p><strong>ID:</strong> ' + caixa.id + '</p>' +
        '<p><strong>Operador:</strong> ' + (caixa.operador || '-') + '</p>' +
        '<p><strong>Abertura:</strong> ' + formatarDataHora(caixa.data_abertura) + '</p>' +
        '<p><strong>Fechamento:</strong> ' + (caixa.data_fechamento ? formatarDataHora(caixa.data_fechamento) : '-') + '</p>' +
        '<p><strong>Status:</strong> ' + (caixa.status === 'aberto' ? 'Aberto' : 'Fechado') + '</p>' +
        (caixa.observacao ? '<p><strong>Observacao:</strong> ' + caixa.observacao + '</p>' : '') +
    '</div>' +
    '<div class="painel-resumo">' +
        '<div class="resumo-item">' +
            '<div class="resumo-label">Troco Inicial</div>' +
            '<div class="resumo-valor">' + formatarMoeda(caixa.troco_inicial) + '</div>' +
        '</div>' +
        '<div class="resumo-item">' +
            '<div class="resumo-label">Entradas</div>' +
            '<div class="resumo-valor entrada-valor">' + formatarMoeda(caixa.total_entradas) + '</div>' +
        '</div>' +
        '<div class="resumo-item">' +
            '<div class="resumo-label">Saidas</div>' +
            '<div class="resumo-valor saida-valor">' + formatarMoeda(caixa.total_saidas) + '</div>' +
        '</div>' +
        '<div class="resumo-item">' +
            '<div class="resumo-label">Saldo</div>' +
            '<div class="resumo-valor saldo-valor">' + formatarMoeda(caixa.saldo_atual) + '</div>' +
        '</div>' +
        '<div class="resumo-item">' +
            '<div class="resumo-label">Saldo em Dinheiro</div>' +
            '<div class="resumo-valor" style="color: #f6d32d;">' + formatarMoeda(caixa.saldo_dinheiro || 0) + '</div>' +
        '</div>' +
    '</div>' +
    valorContadoHtml +
    '<div style="display: flex; gap: 1rem; justify-content: center; margin-bottom: 1rem; flex-wrap: wrap;">' +
        '<button class="btn btn-primary" onclick="exportarCaixaPDF(' + caixa.id + ')">Baixar PDF</button>' +
        '<button class="btn btn-success" onclick="imprimirCupomTermico(' + caixa.id + ')">Imprimir Termica</button>' +
    '</div>' +
    '<h4 class="mt-2">Lancamentos (' + lancamentos.length + ')</h4>' +
    '<div class="lista-lancamentos" style="max-height: 300px; overflow-y: auto;">' + lancamentosHtml + '</div>';
    
    criarModal('Caixa #' + caixa.id, conteudo, []);
}

// Gerar Relatorio
function gerarRelatorio() {
    var dataInicioEl = document.getElementById('relatorioDataInicio');
    var dataFimEl = document.getElementById('relatorioDataFim');
    
    var dataInicio = dataInicioEl ? dataInicioEl.value : '';
    var dataFim = dataFimEl ? dataFimEl.value : '';
    
    if (!dataInicio || !dataFim) {
        mostrarErro('Informe as datas');
        return;
    }
    
    API.relatorioResumo(dataInicio, dataFim)
        .then(function(resultado) {
            if (resultado.success) {
                renderizarRelatorio(resultado);
            } else {
                mostrarErro('Erro ao gerar relatorio');
            }
        })
        .catch(function(error) {
            console.error('Erro ao gerar relatorio:', error);
            mostrarErro('Erro ao gerar relatorio');
        });
}

function renderizarRelatorio(dados) {
    var container = document.getElementById('resultadoRelatorio');
    if (!container) return;
    
    var categoriasHtml = '';
    for (var i = 0; i < dados.categorias.length; i++) {
        var c = dados.categorias[i];
        var tipoTexto = c.tipo === 'entrada' ? 'Entrada' : 'Saida';
        var cor = c.tipo === 'entrada' ? 'var(--success-color)' : 'var(--danger-color)';
        categoriasHtml += '<tr>' +
            '<td>' + c.categoria + '</td>' +
            '<td>' + tipoTexto + '</td>' +
            '<td style="text-align: right; color: ' + cor + '">' + formatarMoeda(c.total) + '</td>' +
        '</tr>';
    }
    
    var pagamentosHtml = '';
    if (dados.pagamentos.length > 0) {
        for (var j = 0; j < dados.pagamentos.length; j++) {
            var p = dados.pagamentos[j];
            pagamentosHtml += '<tr>' +
                '<td>' + p.forma + '</td>' +
                '<td style="text-align: right;">' + formatarMoeda(p.total) + '</td>' +
            '</tr>';
        }
    } else {
        pagamentosHtml = '<tr><td colspan="2" class="text-center">Nenhuma venda no periodo</td></tr>';
    }
    
    var html = '<div class="info-section">' +
        '<h3>Relatorio do Periodo</h3>' +
        '<p><strong>De:</strong> ' + formatarData(dados.periodo.inicio) + ' <strong>ate</strong> ' + formatarData(dados.periodo.fim) + '</p>' +
    '</div>' +
    '<div class="painel-resumo">' +
        '<div class="resumo-item">' +
            '<div class="resumo-label">Total Entradas</div>' +
            '<div class="resumo-valor entrada-valor">' + formatarMoeda(dados.totais.entradas) + '</div>' +
        '</div>' +
        '<div class="resumo-item">' +
            '<div class="resumo-label">Total Saidas</div>' +
            '<div class="resumo-valor saida-valor">' + formatarMoeda(dados.totais.saidas) + '</div>' +
        '</div>' +
        '<div class="resumo-item">' +
            '<div class="resumo-label">Saldo do Periodo</div>' +
            '<div class="resumo-valor saldo-valor">' + formatarMoeda(dados.totais.saldo) + '</div>' +
        '</div>' +
    '</div>' +
    '<div class="form-row mt-2">' +
        '<div class="form-group" style="flex: 1;">' +
            '<h4>Por Categoria</h4>' +
            '<table class="table">' +
                '<thead><tr><th>Categoria</th><th>Tipo</th><th style="text-align: right;">Total</th></tr></thead>' +
                '<tbody>' + categoriasHtml + '</tbody>' +
            '</table>' +
        '</div>' +
        '<div class="form-group" style="flex: 1;">' +
            '<h4>Por Forma de Pagamento (Vendas)</h4>' +
            '<table class="table">' +
                '<thead><tr><th>Forma de Pagamento</th><th style="text-align: right;">Total</th></tr></thead>' +
                '<tbody>' + pagamentosHtml + '</tbody>' +
            '</table>' +
        '</div>' +
    '</div>' +
    '<div class="mt-2" style="display: flex; gap: 1rem; justify-content: center;">' +
        '<button class="btn btn-primary" onclick="exportarRelatorioPDF()">Baixar PDF</button>' +
    '</div>';
    
    container.innerHTML = html;
    
    // Salvar dados para exportacao
    window.relatorioAtual = dados;
}

// ===== FUNCOES DE EXPORTACAO PDF =====

function exportarRelatorioPDF() {
    var dataInicioEl = document.getElementById('relatorioDataInicio');
    var dataFimEl = document.getElementById('relatorioDataFim');
    
    var dataInicio = dataInicioEl ? dataInicioEl.value : '';
    var dataFim = dataFimEl ? dataFimEl.value : '';
    
    if (!dataInicio || !dataFim) {
        mostrarErro('Informe as datas');
        return;
    }
    
    // Abrir PDF em nova aba
    window.open('/api/relatorio/periodo/pdf?data_inicio=' + dataInicio + 'T00:00:00&data_fim=' + dataFim + 'T23:59:59', '_blank');
}

function exportarCaixaPDF(caixaId) {
    window.open('/api/relatorio/caixa/' + caixaId + '/pdf', '_blank');
}

function imprimirCupomTermico(caixaId) {
    // Abre o cupom termmico em nova aba para impressao
    // Otimizado para impressora termica 80mm (Elgin I9)
    window.open('/api/relatorio/caixa/' + caixaId + '/cupom', '_blank');
}

function exportarResumoDiarioPDF(data) {
    var dataStr = data || getDataAtual();
    window.open('/api/relatorio/resumo-diario/pdf?data=' + dataStr, '_blank');
}
