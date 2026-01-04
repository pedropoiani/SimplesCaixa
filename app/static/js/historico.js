/**
 * Controle da página de histórico
 */

document.addEventListener('DOMContentLoaded', () => {
    // Configurar datas padrão
    document.getElementById('relatorioDataInicio').value = getDataPassada(30);
    document.getElementById('relatorioDataFim').value = getDataAtual();
    
    // Listener para período customizado
    document.getElementById('filtroLancPeriodo').addEventListener('change', function() {
        const custom = this.value === 'customizado';
        document.getElementById('filtroLancDatasCustom').style.display = custom ? 'block' : 'none';
        document.getElementById('filtroLancDatasCustom2').style.display = custom ? 'block' : 'none';
        
        if (!custom) {
            aplicarFiltroLancamentos();
        }
    });
});

// Tabs
function mostrarTabHistorico(tab) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    event.target.classList.add('active');
    document.getElementById(`tab-historico-${tab}`).classList.add('active');
    
    // Carregar dados se necessário
    if (tab === 'caixas') {
        listarCaixas();
    }
}

// Filtros de Lançamentos
async function aplicarFiltroLancamentos() {
    const periodo = document.getElementById('filtroLancPeriodo').value;
    const tipo = document.getElementById('filtroLancTipo').value;
    const categoria = document.getElementById('filtroLancCategoria').value;
    
    let dataInicio, dataFim;
    
    if (periodo === 'customizado') {
        dataInicio = document.getElementById('filtroLancDataInicio').value;
        dataFim = document.getElementById('filtroLancDataFim').value;
        
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
    
    const filtros = {
        data_inicio: dataInicio + 'T00:00:00',
        data_fim: dataFim + 'T23:59:59'
    };
    
    if (tipo) filtros.tipo = tipo;
    if (categoria) filtros.categoria = categoria;
    
    try {
        const resultado = await API.listarLancamentos(filtros);
        
        if (resultado.success) {
            renderizarResultadosLancamentos(resultado.lancamentos);
        } else {
            mostrarErro('Erro ao buscar lançamentos');
        }
    } catch (error) {
        console.error('Erro ao buscar lançamentos:', error);
        mostrarErro('Erro ao buscar lançamentos');
    }
}

function renderizarResultadosLancamentos(lancamentos) {
    const container = document.getElementById('resultadosLancamentos');
    
    if (lancamentos.length === 0) {
        container.innerHTML = '<p class="text-center">Nenhum lançamento encontrado</p>';
        return;
    }
    
    const totalEntradas = lancamentos
        .filter(l => l.tipo === 'entrada')
        .reduce((sum, l) => sum + l.valor, 0);
    
    const totalSaidas = lancamentos
        .filter(l => l.tipo === 'saida')
        .reduce((sum, l) => sum + l.valor, 0);
    
    const html = `
        <div class="painel-resumo mb-2">
            <div class="resumo-item">
                <div class="resumo-label">Total de Lançamentos</div>
                <div class="resumo-valor">${lancamentos.length}</div>
            </div>
            <div class="resumo-item">
                <div class="resumo-label">Total Entradas</div>
                <div class="resumo-valor entrada-valor">${formatarMoeda(totalEntradas)}</div>
            </div>
            <div class="resumo-item">
                <div class="resumo-label">Total Saídas</div>
                <div class="resumo-valor saida-valor">${formatarMoeda(totalSaidas)}</div>
            </div>
            <div class="resumo-item">
                <div class="resumo-label">Saldo</div>
                <div class="resumo-valor saldo-valor">${formatarMoeda(totalEntradas - totalSaidas)}</div>
            </div>
        </div>
        
        <div class="table-responsive">
            <table class="table">
                <thead>
                    <tr>
                        <th>Data/Hora</th>
                        <th>Tipo</th>
                        <th>Categoria</th>
                        <th>Forma Pgto</th>
                        <th>Descrição</th>
                        <th style="text-align: right;">Valor</th>
                    </tr>
                </thead>
                <tbody>
                    ${lancamentos.map(l => `
                        <tr>
                            <td>${formatarDataHora(l.data_hora)}</td>
                            <td>${l.tipo === 'entrada' ? '⬆️ Entrada' : '⬇️ Saída'}</td>
                            <td>${l.categoria}</td>
                            <td>${l.forma_pagamento || '-'}</td>
                            <td>${l.descricao || '-'}</td>
                            <td style="text-align: right; color: ${l.tipo === 'entrada' ? 'var(--success-color)' : 'var(--danger-color)'}">
                                ${l.tipo === 'entrada' ? '+' : '-'}${formatarMoeda(l.valor)}
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
    
    container.innerHTML = html;
    window.lancamentosAtual = lancamentos;
}

function exportarLancamentosCSV() {
    if (!window.lancamentosAtual || window.lancamentosAtual.length === 0) {
        mostrarErro('Não há dados para exportar');
        return;
    }
    
    const colunas = [
        { campo: 'data_hora', titulo: 'Data/Hora', formato: 'dataHora' },
        { campo: 'tipo', titulo: 'Tipo' },
        { campo: 'categoria', titulo: 'Categoria' },
        { campo: 'forma_pagamento', titulo: 'Forma Pagamento' },
        { campo: 'descricao', titulo: 'Descrição' },
        { campo: 'valor', titulo: 'Valor', formato: 'moeda' }
    ];
    
    const nomeArquivo = `lancamentos_${getDataAtual()}.csv`;
    exportarCSV(window.lancamentosAtual, colunas, nomeArquivo);
}

// Listar Caixas
async function listarCaixas() {
    const status = document.getElementById('filtroCaixaStatus').value;
    
    const filtros = {};
    if (status) filtros.status = status;
    
    try {
        const resultado = await API.listarCaixas(filtros);
        
        if (resultado.success) {
            renderizarResultadosCaixas(resultado.caixas);
        } else {
            mostrarErro('Erro ao buscar caixas');
        }
    } catch (error) {
        console.error('Erro ao buscar caixas:', error);
        mostrarErro('Erro ao buscar caixas');
    }
}

function renderizarResultadosCaixas(caixas) {
    const container = document.getElementById('resultadosCaixas');
    
    if (caixas.length === 0) {
        container.innerHTML = '<p class="text-center">Nenhum caixa encontrado</p>';
        return;
    }
    
    const html = `
        <div class="table-responsive">
            <table class="table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Abertura</th>
                        <th>Fechamento</th>
                        <th>Operador</th>
                        <th>Status</th>
                        <th style="text-align: right;">Troco Inicial</th>
                        <th style="text-align: right;">Saldo Final</th>
                        <th style="text-align: right;">Diferença</th>
                    </tr>
                </thead>
                <tbody>
                    ${caixas.map(c => `
                        <tr onclick="verDetalhesCaixa(${c.id})" style="cursor: pointer;">
                            <td>${c.id}</td>
                            <td>${formatarDataHora(c.data_abertura)}</td>
                            <td>${c.data_fechamento ? formatarDataHora(c.data_fechamento) : '-'}</td>
                            <td>${c.operador || '-'}</td>
                            <td>
                                <span class="status-badge ${c.status === 'aberto' ? 'status-open' : 'status-closed'}">
                                    ${c.status === 'aberto' ? '🔓 Aberto' : '🔒 Fechado'}
                                </span>
                            </td>
                            <td style="text-align: right;">${formatarMoeda(c.troco_inicial)}</td>
                            <td style="text-align: right;">${formatarMoeda(c.saldo_atual)}</td>
                            <td style="text-align: right; color: ${c.diferenca > 0 ? 'var(--success-color)' : c.diferenca < 0 ? 'var(--danger-color)' : 'inherit'}">
                                ${c.diferenca ? formatarMoeda(c.diferenca) : '-'}
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
    
    container.innerHTML = html;
    window.caixasAtual = caixas;
}

function exportarCaixasCSV() {
    if (!window.caixasAtual || window.caixasAtual.length === 0) {
        mostrarErro('Não há dados para exportar');
        return;
    }
    
    const colunas = [
        { campo: 'id', titulo: 'ID' },
        { campo: 'data_abertura', titulo: 'Abertura', formato: 'dataHora' },
        { campo: 'data_fechamento', titulo: 'Fechamento', formato: 'dataHora' },
        { campo: 'operador', titulo: 'Operador' },
        { campo: 'status', titulo: 'Status' },
        { campo: 'troco_inicial', titulo: 'Troco Inicial', formato: 'moeda' },
        { campo: 'saldo_atual', titulo: 'Saldo Final', formato: 'moeda' },
        { campo: 'diferenca', titulo: 'Diferença', formato: 'moeda' }
    ];
    
    const nomeArquivo = `caixas_${getDataAtual()}.csv`;
    exportarCSV(window.caixasAtual, colunas, nomeArquivo);
}

async function verDetalhesCaixa(id) {
    try {
        const resultado = await API.detalhesCaixa(id);
        
        if (resultado.success) {
            mostrarModalDetalhesCaixa(resultado.caixa, resultado.lancamentos);
        } else {
            mostrarErro('Erro ao carregar detalhes');
        }
    } catch (error) {
        console.error('Erro ao carregar detalhes:', error);
        mostrarErro('Erro ao carregar detalhes do caixa');
    }
}

function mostrarModalDetalhesCaixa(caixa, lancamentos) {
    const conteudo = `
        <div class="info-section">
            <h4>Informações do Caixa</h4>
            <p><strong>ID:</strong> ${caixa.id}</p>
            <p><strong>Operador:</strong> ${caixa.operador || '-'}</p>
            <p><strong>Abertura:</strong> ${formatarDataHora(caixa.data_abertura)}</p>
            <p><strong>Fechamento:</strong> ${caixa.data_fechamento ? formatarDataHora(caixa.data_fechamento) : '-'}</p>
            <p><strong>Status:</strong> ${caixa.status === 'aberto' ? '🔓 Aberto' : '🔒 Fechado'}</p>
            ${caixa.observacao ? `<p><strong>Observação:</strong> ${caixa.observacao}</p>` : ''}
        </div>
        
        <div class="painel-resumo">
            <div class="resumo-item">
                <div class="resumo-label">Troco Inicial</div>
                <div class="resumo-valor">${formatarMoeda(caixa.troco_inicial)}</div>
            </div>
            <div class="resumo-item">
                <div class="resumo-label">Entradas</div>
                <div class="resumo-valor entrada-valor">${formatarMoeda(caixa.total_entradas)}</div>
            </div>
            <div class="resumo-item">
                <div class="resumo-label">Saídas</div>
                <div class="resumo-valor saida-valor">${formatarMoeda(caixa.total_saidas)}</div>
            </div>
            <div class="resumo-item">
                <div class="resumo-label">Saldo</div>
                <div class="resumo-valor saldo-valor">${formatarMoeda(caixa.saldo_atual)}</div>
            </div>
        </div>
        
        ${caixa.valor_contado ? `
            <div class="info-section">
                <p><strong>Valor Contado:</strong> ${formatarMoeda(caixa.valor_contado)}</p>
                <p><strong>Diferença:</strong> 
                    <span style="color: ${caixa.diferenca > 0 ? 'var(--success-color)' : caixa.diferenca < 0 ? 'var(--danger-color)' : 'inherit'}">
                        ${formatarMoeda(caixa.diferenca)}
                        ${caixa.diferenca > 0 ? '(Sobra)' : caixa.diferenca < 0 ? '(Falta)' : ''}
                    </span>
                </p>
            </div>
        ` : ''}
        
        <div style="display: flex; gap: 1rem; justify-content: center; margin-bottom: 1rem;">
            <button class="btn btn-primary" onclick="exportarCaixaPDF(${caixa.id})">
                📄 Baixar PDF
            </button>
        </div>
        
        <h4 class="mt-2">Lançamentos (${lancamentos.length})</h4>
        <div class="lista-lancamentos" style="max-height: 300px; overflow-y: auto;">
            ${lancamentos.length > 0 ? lancamentos.map(l => `
                <div class="lancamento-item ${l.tipo}">
                    <div class="lancamento-info">
                        <div class="lancamento-categoria">${l.categoria.toUpperCase()}</div>
                        <div class="lancamento-descricao">
                            ${l.forma_pagamento ? `${l.forma_pagamento} • ` : ''}
                            ${formatarDataHora(l.data_hora)}
                            ${l.descricao ? `<br><small>${l.descricao}</small>` : ''}
                        </div>
                    </div>
                    <div class="lancamento-valor ${l.tipo}">
                        ${l.tipo === 'entrada' ? '+' : '-'}${formatarMoeda(l.valor)}
                    </div>
                </div>
            `).join('') : '<p class="text-center">Nenhum lançamento</p>'}
        </div>
    `;
    
    criarModal(`💰 Caixa #${caixa.id}`, conteudo, []);
}

// Gerar Relatório
async function gerarRelatorio() {
    const dataInicio = document.getElementById('relatorioDataInicio').value;
    const dataFim = document.getElementById('relatorioDataFim').value;
    
    if (!dataInicio || !dataFim) {
        mostrarErro('Informe as datas');
        return;
    }
    
    try {
        const resultado = await API.relatorioResumo(dataInicio, dataFim);
        
        if (resultado.success) {
            renderizarRelatorio(resultado);
        } else {
            mostrarErro('Erro ao gerar relatório');
        }
    } catch (error) {
        console.error('Erro ao gerar relatório:', error);
        mostrarErro('Erro ao gerar relatório');
    }
}

function renderizarRelatorio(dados) {
    const container = document.getElementById('resultadoRelatorio');
    
    const html = `
        <div class="info-section">
            <h3>📊 Relatório do Período</h3>
            <p><strong>De:</strong> ${formatarData(dados.periodo.inicio)} 
               <strong>até</strong> ${formatarData(dados.periodo.fim)}</p>
        </div>
        
        <div class="painel-resumo">
            <div class="resumo-item">
                <div class="resumo-label">Total Entradas</div>
                <div class="resumo-valor entrada-valor">${formatarMoeda(dados.totais.entradas)}</div>
            </div>
            <div class="resumo-item">
                <div class="resumo-label">Total Saídas</div>
                <div class="resumo-valor saida-valor">${formatarMoeda(dados.totais.saidas)}</div>
            </div>
            <div class="resumo-item">
                <div class="resumo-label">Saldo do Período</div>
                <div class="resumo-valor saldo-valor">${formatarMoeda(dados.totais.saldo)}</div>
            </div>
        </div>
        
        <div class="form-row mt-2">
            <div class="form-group" style="flex: 1;">
                <h4>Por Categoria</h4>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Categoria</th>
                            <th>Tipo</th>
                            <th style="text-align: right;">Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${dados.categorias.map(c => `
                            <tr>
                                <td>${c.categoria}</td>
                                <td>${c.tipo === 'entrada' ? '⬆️ Entrada' : '⬇️ Saída'}</td>
                                <td style="text-align: right; color: ${c.tipo === 'entrada' ? 'var(--success-color)' : 'var(--danger-color)'}">
                                    ${formatarMoeda(c.total)}
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
            
            <div class="form-group" style="flex: 1;">
                <h4>Por Forma de Pagamento (Vendas)</h4>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Forma de Pagamento</th>
                            <th style="text-align: right;">Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${dados.pagamentos.length > 0 ? dados.pagamentos.map(p => `
                            <tr>
                                <td>${p.forma}</td>
                                <td style="text-align: right;">${formatarMoeda(p.total)}</td>
                            </tr>
                        `).join('') : '<tr><td colspan="2" class="text-center">Nenhuma venda no período</td></tr>'}
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="mt-2" style="display: flex; gap: 1rem; justify-content: center;">
            <button class="btn btn-primary" onclick="exportarRelatorioPDF()">
                📄 Baixar PDF
            </button>
        </div>
    `;
    
    container.innerHTML = html;
    
    // Salvar dados para exportação
    window.relatorioAtual = dados;
}

// ===== FUNÇÕES DE EXPORTAÇÃO PDF =====

function exportarRelatorioPDF() {
    const dataInicio = document.getElementById('relatorioDataInicio').value;
    const dataFim = document.getElementById('relatorioDataFim').value;
    
    if (!dataInicio || !dataFim) {
        mostrarErro('Informe as datas');
        return;
    }
    
    // Abrir PDF em nova aba
    window.open(`/api/relatorio/periodo/pdf?data_inicio=${dataInicio}T00:00:00&data_fim=${dataFim}T23:59:59`, '_blank');
}

function exportarCaixaPDF(caixaId) {
    window.open(`/api/relatorio/caixa/${caixaId}/pdf`, '_blank');
}

function exportarResumoDiarioPDF(data) {
    const dataStr = data || getDataAtual();
    window.open(`/api/relatorio/resumo-diario/pdf?data=${dataStr}`, '_blank');
}
