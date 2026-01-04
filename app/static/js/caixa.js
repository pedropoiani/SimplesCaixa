/**
 * PDV-MF - Controle de Caixa
 * Interface estilo PDV profissional com teclado virtual
 */

let caixaAtual = null;
let formasPagamento = [];
let valorAtual = '';
let valorRecebidoAtual = '';
let campoAtivo = 'valor';

// ====================================
// INICIALIZAÇÃO
// ====================================

document.addEventListener('DOMContentLoaded', async () => {
    await carregarFormasPagamento();
    await verificarCaixa();
    await carregarNomeLoja();
});

async function carregarNomeLoja() {
    try {
        const config = await API.getConfiguracao();
        document.getElementById('nomeLoja').textContent = config.nome_loja || 'PDV-MF';
    } catch (error) {
        console.error('Erro ao carregar configurações:', error);
    }
}

async function carregarFormasPagamento() {
    try {
        const config = await API.getConfiguracao();
        formasPagamento = config.formas_pagamento;
    } catch (error) {
        console.error('Erro ao carregar formas de pagamento:', error);
        formasPagamento = ['Dinheiro', 'PIX', 'Cartão Crédito', 'Cartão Débito'];
    }
}

async function verificarCaixa() {
    try {
        const status = await API.caixaStatus();
        
        if (status.aberto) {
            caixaAtual = status.caixa;
            mostrarCaixaAberto();
            await carregarPainel();
            await carregarUltimosLancamentos();
        } else {
            caixaAtual = null;
            mostrarCaixaFechado();
        }
    } catch (error) {
        console.error('Erro ao verificar caixa:', error);
        mostrarNotificacao('Erro ao verificar status do caixa', 'erro');
    }
}

function mostrarCaixaAberto() {
    document.getElementById('caixaFechado').style.display = 'none';
    document.getElementById('caixaAberto').style.display = 'block';
    
    if (caixaAtual && caixaAtual.operador) {
        document.getElementById('nomeOperador').textContent = caixaAtual.operador;
    } else {
        document.getElementById('nomeOperador').textContent = '-';
    }
}

function mostrarCaixaFechado() {
    document.getElementById('caixaFechado').style.display = 'flex';
    document.getElementById('caixaAberto').style.display = 'none';
}

// ====================================
// NOTIFICAÇÕES
// ====================================

function mostrarNotificacao(mensagem, tipo = 'info') {
    // Remove notificação existente
    const existente = document.querySelector('.notificacao-pdv');
    if (existente) existente.remove();
    
    const notificacao = document.createElement('div');
    notificacao.className = `notificacao-pdv ${tipo}`;
    notificacao.innerHTML = `
        <span>${tipo === 'sucesso' ? '✅' : tipo === 'erro' ? '❌' : 'ℹ️'} ${mensagem}</span>
    `;
    
    // Adicionar estilos inline
    notificacao.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        font-weight: 600;
        z-index: 9999;
        animation: slideIn 0.3s ease;
        ${tipo === 'sucesso' ? 'background: #26a269; color: white;' : ''}
        ${tipo === 'erro' ? 'background: #c01c28; color: white;' : ''}
        ${tipo === 'info' ? 'background: #1c71d8; color: white;' : ''}
    `;
    
    document.body.appendChild(notificacao);
    
    setTimeout(() => {
        notificacao.style.opacity = '0';
        setTimeout(() => notificacao.remove(), 300);
    }, 3000);
}

// ====================================
// MODAL GENÉRICO PDV
// ====================================

function abrirModalPDV(titulo, conteudo, corHeader = 'primary') {
    fecharModalPDV();
    
    const cores = {
        primary: 'linear-gradient(135deg, #1a5fb4, #0d4a8f)',
        success: 'linear-gradient(135deg, #26a269, #1e8054)',
        danger: 'linear-gradient(135deg, #c01c28, #a11720)',
        warning: 'linear-gradient(135deg, #e5a50a, #c48d09)',
        info: 'linear-gradient(135deg, #1c71d8, #1a5fb4)'
    };
    
    const modal = document.createElement('div');
    modal.id = 'modalPDV';
    modal.className = 'modal-pdv show';
    modal.innerHTML = `
        <div class="modal-pdv-content">
            <div class="modal-pdv-header" style="background: ${cores[corHeader] || cores.primary}">
                <h3>${titulo}</h3>
                <button class="modal-pdv-close" onclick="fecharModalPDV()">&times;</button>
            </div>
            <div class="modal-pdv-body">
                ${conteudo}
            </div>
        </div>
    `;
    
    document.getElementById('modalsContainer').appendChild(modal);
    
    // Fechar ao clicar fora
    modal.addEventListener('click', (e) => {
        if (e.target === modal) fecharModalPDV();
    });
}

function fecharModalPDV() {
    const modal = document.getElementById('modalPDV');
    if (modal) modal.remove();
    
    // Limpar variáveis
    valorAtual = '';
    valorRecebidoAtual = '';
    campoAtivo = 'valor';
}

// ====================================
// TECLADO VIRTUAL
// ====================================

function teclarNumero(num) {
    if (campoAtivo === 'valor') {
        valorAtual += num;
        atualizarDisplayValor();
    } else if (campoAtivo === 'recebido') {
        valorRecebidoAtual += num;
        atualizarDisplayRecebido();
    }
}

function limparTeclado() {
    if (campoAtivo === 'valor') {
        valorAtual = '';
        atualizarDisplayValor();
    } else if (campoAtivo === 'recebido') {
        valorRecebidoAtual = '';
        atualizarDisplayRecebido();
    }
}

function apagarUltimo() {
    if (campoAtivo === 'valor') {
        valorAtual = valorAtual.slice(0, -1);
        atualizarDisplayValor();
    } else if (campoAtivo === 'recebido') {
        valorRecebidoAtual = valorRecebidoAtual.slice(0, -1);
        atualizarDisplayRecebido();
    }
}

function atualizarDisplayValor() {
    const display = document.getElementById('displayValor');
    if (display) {
        display.textContent = formatarValorDisplay(valorAtual);
    }
    calcularTroco();
}

function atualizarDisplayRecebido() {
    const display = document.getElementById('displayRecebido');
    if (display) {
        display.textContent = formatarValorDisplay(valorRecebidoAtual);
    }
    calcularTroco();
}

function formatarValorDisplay(valor) {
    if (!valor) return 'R$ 0,00';
    
    // Remove tudo que não é número
    valor = valor.replace(/\D/g, '');
    
    // Converte para centavos
    const centavos = parseInt(valor) || 0;
    const reais = centavos / 100;
    
    return formatarMoeda(reais);
}

function getValorNumerico(valorStr) {
    if (!valorStr) return 0;
    valorStr = valorStr.replace(/\D/g, '');
    return (parseInt(valorStr) || 0) / 100;
}

function calcularTroco() {
    const trocoDisplay = document.getElementById('displayTroco');
    const secaoTroco = document.getElementById('secaoTroco');
    if (!trocoDisplay || !secaoTroco) return;
    
    const valor = getValorNumerico(valorAtual);
    const recebido = getValorNumerico(valorRecebidoAtual);
    const troco = recebido - valor;
    
    if (recebido > 0 && troco >= 0) {
        trocoDisplay.textContent = formatarMoeda(troco);
        secaoTroco.style.display = 'block';
    } else {
        secaoTroco.style.display = 'none';
    }
}

function setarCampoAtivo(campo) {
    campoAtivo = campo;
    
    // Atualizar visual
    document.querySelectorAll('.valor-display').forEach(el => {
        el.classList.remove('ativo');
    });
    
    const displayAtivo = document.getElementById(campo === 'valor' ? 'containerValor' : 'containerRecebido');
    if (displayAtivo) {
        displayAtivo.classList.add('ativo');
    }
}

function setarValorRapido(valor) {
    valorRecebidoAtual = String(valor * 100);
    atualizarDisplayRecebido();
}

// ====================================
// MODAL ABRIR CAIXA
// ====================================

function modalAbrirCaixa() {
    const conteudo = `
        <div class="modal-layout-horizontal">
            <div class="modal-lado-esquerdo">
                <div class="form-group-pdv">
                    <label>OPERADOR</label>
                    <input type="text" id="inputOperador" class="form-control-pdv" placeholder="Nome do operador">
                </div>
                
                <div class="form-group-pdv">
                    <label>TROCO INICIAL</label>
                    <div class="valor-display ativo" id="containerValor" onclick="setarCampoAtivo('valor')">
                        <div class="valor-display-label">Valor em caixa</div>
                        <div class="valor-display-numero" id="displayValor">R$ 0,00</div>
                    </div>
                </div>
            </div>
            
            <div class="modal-lado-direito">
                <div class="teclado-virtual compacto">
                    <button class="tecla" onclick="teclarNumero('1')">1</button>
                    <button class="tecla" onclick="teclarNumero('2')">2</button>
                    <button class="tecla" onclick="teclarNumero('3')">3</button>
                    <button class="tecla" onclick="teclarNumero('4')">4</button>
                    <button class="tecla" onclick="teclarNumero('5')">5</button>
                    <button class="tecla" onclick="teclarNumero('6')">6</button>
                    <button class="tecla" onclick="teclarNumero('7')">7</button>
                    <button class="tecla" onclick="teclarNumero('8')">8</button>
                    <button class="tecla" onclick="teclarNumero('9')">9</button>
                    <button class="tecla limpar" onclick="limparTeclado()">C</button>
                    <button class="tecla" onclick="teclarNumero('0')">0</button>
                    <button class="tecla backspace" onclick="apagarUltimo()">⌫</button>
                    <button class="tecla confirmar" onclick="confirmarAbrirCaixa()">✅ ABRIR</button>
                </div>
            </div>
        </div>
    `;
    
    abrirModalPDV('🔓 Abrir Caixa', conteudo, 'success');
}

async function confirmarAbrirCaixa() {
    const operador = document.getElementById('inputOperador').value;
    const troco = getValorNumerico(valorAtual);
    
    try {
        const resultado = await API.abrirCaixa({
            operador: operador,
            troco_inicial: troco
        });
        
        if (resultado.success) {
            mostrarNotificacao('Caixa aberto com sucesso!', 'sucesso');
            fecharModalPDV();
            await verificarCaixa();
        } else {
            mostrarNotificacao(resultado.message, 'erro');
        }
    } catch (error) {
        console.error('Erro ao abrir caixa:', error);
        mostrarNotificacao('Erro ao abrir caixa', 'erro');
    }
}

// ====================================
// MODAL VENDA
// ====================================

let formaSelecionada = '';

function modalVenda() {
    formaSelecionada = '';
    
    let formasHtml = formasPagamento.map(forma => `
        <button class="forma-btn" onclick="selecionarForma('${forma}')" id="forma-${forma.replace(/\s/g, '')}">
            <span>${getIconeForma(forma)} ${forma}</span>
        </button>
    `).join('');
    
    const conteudo = `
        <div class="modal-layout-horizontal">
            <div class="modal-lado-esquerdo">
                <div class="form-group-pdv">
                    <label>FORMA DE PAGAMENTO</label>
                    <div class="formas-pagamento-grid">
                        ${formasHtml}
                    </div>
                </div>
                
                <div id="areaValorVenda" style="display: none;">
                    <div class="form-group-pdv">
                        <label>VALOR DA VENDA</label>
                        <div class="valor-display ativo" id="containerValor" onclick="setarCampoAtivo('valor')">
                            <div class="valor-display-label">Total</div>
                            <div class="valor-display-numero" id="displayValor">R$ 0,00</div>
                        </div>
                    </div>
                    
                    <div id="areaDinheiro" style="display: none;">
                        <div class="form-group-pdv">
                            <label>VALOR RECEBIDO</label>
                            <div class="valor-display compacto" id="containerRecebido" onclick="setarCampoAtivo('recebido')">
                                <div class="valor-display-label">Recebido</div>
                                <div class="valor-display-numero" id="displayRecebido">R$ 0,00</div>
                            </div>
                        </div>
                        
                        <div class="valores-rapidos">
                            <button class="valor-rapido-btn" onclick="setarValorRapido(10)">R$10</button>
                            <button class="valor-rapido-btn" onclick="setarValorRapido(20)">R$20</button>
                            <button class="valor-rapido-btn" onclick="setarValorRapido(50)">R$50</button>
                            <button class="valor-rapido-btn" onclick="setarValorRapido(100)">R$100</button>
                        </div>
                        
                        <div class="secao-troco" id="secaoTroco" style="display: none;">
                            <h4>💵 TROCO</h4>
                            <div class="valor-display-numero" id="displayTroco" style="font-size: 1.5rem; color: #26a269;">R$ 0,00</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="modal-lado-direito">
                <div class="teclado-virtual compacto">
                    <button class="tecla" onclick="teclarNumero('1')">1</button>
                    <button class="tecla" onclick="teclarNumero('2')">2</button>
                    <button class="tecla" onclick="teclarNumero('3')">3</button>
                    <button class="tecla" onclick="teclarNumero('4')">4</button>
                    <button class="tecla" onclick="teclarNumero('5')">5</button>
                    <button class="tecla" onclick="teclarNumero('6')">6</button>
                    <button class="tecla" onclick="teclarNumero('7')">7</button>
                    <button class="tecla" onclick="teclarNumero('8')">8</button>
                    <button class="tecla" onclick="teclarNumero('9')">9</button>
                    <button class="tecla limpar" onclick="limparTeclado()">C</button>
                    <button class="tecla" onclick="teclarNumero('0')">0</button>
                    <button class="tecla backspace" onclick="apagarUltimo()">⌫</button>
                    <button class="tecla confirmar" onclick="confirmarVenda()">✅ CONFIRMAR</button>
                </div>
            </div>
        </div>
    `;
    
    abrirModalPDV('💳 Nova Venda', conteudo, 'success');
}

function getIconeForma(forma) {
    const icones = {
        'Dinheiro': '💵',
        'PIX': '📱',
        'Cartão Crédito': '💳',
        'Cartão Débito': '💳',
        'Crédito': '💳',
        'Débito': '💳',
        'Transferência': '🏦',
        'Cheque': '📝'
    };
    return icones[forma] || '💰';
}

function selecionarForma(forma) {
    formaSelecionada = forma;
    
    // Atualizar visual
    document.querySelectorAll('.forma-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(`forma-${forma.replace(/\s/g, '')}`).classList.add('active');
    
    // Mostrar área de valor
    document.getElementById('areaValorVenda').style.display = 'block';
    
    // Mostrar/esconder campos específicos de dinheiro
    const areaDinheiro = document.getElementById('areaDinheiro');
    if (forma === 'Dinheiro') {
        areaDinheiro.style.display = 'block';
    } else {
        areaDinheiro.style.display = 'none';
    }
    
    // Limpar valores
    valorAtual = '';
    valorRecebidoAtual = '';
    campoAtivo = 'valor';
    atualizarDisplayValor();
}

async function confirmarVenda() {
    if (!formaSelecionada) {
        mostrarNotificacao('Selecione a forma de pagamento', 'erro');
        return;
    }
    
    const valor = getValorNumerico(valorAtual);
    
    if (valor <= 0) {
        mostrarNotificacao('Informe o valor da venda', 'erro');
        return;
    }
    
    // Validação específica para dinheiro
    if (formaSelecionada === 'Dinheiro') {
        const recebido = getValorNumerico(valorRecebidoAtual);
        
        if (recebido <= 0) {
            mostrarNotificacao('Informe o valor recebido', 'erro');
            return;
        }
        
        if (recebido < valor) {
            mostrarNotificacao('Valor recebido menor que o valor da venda', 'erro');
            return;
        }
    }
    
    const dados = {
        tipo: 'entrada',
        categoria: 'venda',
        forma_pagamento: formaSelecionada,
        valor: valor,
        descricao: ''
    };
    
    if (formaSelecionada === 'Dinheiro') {
        dados.valor_recebido = getValorNumerico(valorRecebidoAtual);
    }
    
    try {
        const resultado = await API.criarLancamento(dados);
        
        if (resultado.success) {
            mostrarNotificacao('Venda registrada com sucesso!', 'sucesso');
            fecharModalPDV();
            await carregarPainel();
            await carregarUltimosLancamentos();
        } else {
            mostrarNotificacao(resultado.message, 'erro');
        }
    } catch (error) {
        console.error('Erro ao registrar venda:', error);
        mostrarNotificacao('Erro ao registrar venda', 'erro');
    }
}

// ====================================
// MODAL SANGRIA
// ====================================

function modalSangria() {
    const conteudo = `
        <div class="modal-layout-horizontal">
            <div class="modal-lado-esquerdo">
                <div class="info-message" style="margin-bottom: 0.75rem; padding: 0.75rem;">
                    💸 Sangria é a retirada de dinheiro do caixa
                </div>
                
                <div class="form-group-pdv">
                    <label>VALOR DA SANGRIA</label>
                    <div class="valor-display ativo" id="containerValor" onclick="setarCampoAtivo('valor')">
                        <div class="valor-display-label">Valor a retirar</div>
                        <div class="valor-display-numero" id="displayValor">R$ 0,00</div>
                    </div>
                </div>
                
                <div class="form-group-pdv">
                    <label>MOTIVO RÁPIDO</label>
                    <div class="motivos-rapidos">
                        <button class="motivo-btn" onclick="setarMotivo('Alimentação')">🍔 Alimentação</button>
                        <button class="motivo-btn" onclick="setarMotivo('Embalagem')">📦 Embalagem</button>
                        <button class="motivo-btn" onclick="setarMotivo('Pró-labore')">💼 Pró-labore</button>
                        <button class="motivo-btn" onclick="setarMotivo('Transporte')">🚗 Transporte</button>
                        <button class="motivo-btn" onclick="setarMotivo('Pagamento')">💳 Pagamento</button>
                        <button class="motivo-btn" onclick="setarMotivo('Retirada banco')">🏦 Banco</button>
                    </div>
                </div>
                
                <div class="form-group-pdv">
                    <label>MOTIVO</label>
                    <input type="text" id="inputMotivo" class="form-control-pdv" placeholder="Ou digite aqui...">
                </div>
            </div>
            
            <div class="modal-lado-direito">
                <div class="teclado-virtual compacto">
                    <button class="tecla" onclick="teclarNumero('1')">1</button>
                    <button class="tecla" onclick="teclarNumero('2')">2</button>
                    <button class="tecla" onclick="teclarNumero('3')">3</button>
                    <button class="tecla" onclick="teclarNumero('4')">4</button>
                    <button class="tecla" onclick="teclarNumero('5')">5</button>
                    <button class="tecla" onclick="teclarNumero('6')">6</button>
                    <button class="tecla" onclick="teclarNumero('7')">7</button>
                    <button class="tecla" onclick="teclarNumero('8')">8</button>
                    <button class="tecla" onclick="teclarNumero('9')">9</button>
                    <button class="tecla limpar" onclick="limparTeclado()">C</button>
                    <button class="tecla" onclick="teclarNumero('0')">0</button>
                    <button class="tecla backspace" onclick="apagarUltimo()">⌫</button>
                    <button class="tecla confirmar" style="background: #c01c28;" onclick="confirmarSangria()">💸 CONFIRMAR</button>
                </div>
            </div>
        </div>
    `;
    
    abrirModalPDV('💸 Sangria', conteudo, 'danger');
}

function setarMotivo(motivo) {
    document.getElementById('inputMotivo').value = motivo;
    
    // Atualizar visual dos botões
    document.querySelectorAll('.motivo-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
}

async function confirmarSangria() {
    const valor = getValorNumerico(valorAtual);
    const motivo = document.getElementById('inputMotivo')?.value || '';
    
    if (valor <= 0) {
        mostrarNotificacao('Informe o valor da sangria', 'erro');
        return;
    }
    
    const dados = {
        tipo: 'saida',
        categoria: 'sangria',
        valor: valor,
        descricao: motivo
    };
    
    try {
        const resultado = await API.criarLancamento(dados);
        
        if (resultado.success) {
            mostrarNotificacao('Sangria registrada com sucesso!', 'sucesso');
            fecharModalPDV();
            await carregarPainel();
            await carregarUltimosLancamentos();
        } else {
            mostrarNotificacao(resultado.message, 'erro');
        }
    } catch (error) {
        console.error('Erro ao registrar sangria:', error);
        mostrarNotificacao('Erro ao registrar sangria', 'erro');
    }
}

// ====================================
// MODAL SUPRIMENTO
// ====================================

function modalSuprimento() {
    const conteudo = `
        <div class="modal-layout-horizontal">
            <div class="modal-lado-esquerdo">
                <div class="info-message" style="margin-bottom: 0.75rem; padding: 0.75rem;">
                    💰 Suprimento é a entrada de dinheiro no caixa
                </div>
                
                <div class="form-group-pdv">
                    <label>VALOR DO SUPRIMENTO</label>
                    <div class="valor-display ativo" id="containerValor" onclick="setarCampoAtivo('valor')">
                        <div class="valor-display-label">Valor a adicionar</div>
                        <div class="valor-display-numero" id="displayValor">R$ 0,00</div>
                    </div>
                </div>
                
                <div class="form-group-pdv">
                    <label>MOTIVO RÁPIDO</label>
                    <div class="motivos-rapidos">
                        <button class="motivo-btn" onclick="setarMotivo('Troco do banco')">🏦 Troco banco</button>
                        <button class="motivo-btn" onclick="setarMotivo('Reforço de caixa')">💵 Reforço</button>
                        <button class="motivo-btn" onclick="setarMotivo('Devolução')">↩️ Devolução</button>
                        <button class="motivo-btn" onclick="setarMotivo('Acerto')">📋 Acerto</button>
                    </div>
                </div>
                
                <div class="form-group-pdv">
                    <label>MOTIVO</label>
                    <input type="text" id="inputMotivo" class="form-control-pdv" placeholder="Ou digite aqui...">
                </div>
            </div>
            
            <div class="modal-lado-direito">
                <div class="teclado-virtual compacto">
                    <button class="tecla" onclick="teclarNumero('1')">1</button>
                    <button class="tecla" onclick="teclarNumero('2')">2</button>
                    <button class="tecla" onclick="teclarNumero('3')">3</button>
                    <button class="tecla" onclick="teclarNumero('4')">4</button>
                    <button class="tecla" onclick="teclarNumero('5')">5</button>
                    <button class="tecla" onclick="teclarNumero('6')">6</button>
                    <button class="tecla" onclick="teclarNumero('7')">7</button>
                    <button class="tecla" onclick="teclarNumero('8')">8</button>
                    <button class="tecla" onclick="teclarNumero('9')">9</button>
                    <button class="tecla limpar" onclick="limparTeclado()">C</button>
                    <button class="tecla" onclick="teclarNumero('0')">0</button>
                    <button class="tecla backspace" onclick="apagarUltimo()">⌫</button>
                    <button class="tecla confirmar" style="background: #1c71d8;" onclick="confirmarSuprimento()">💰 CONFIRMAR</button>
                </div>
            </div>
        </div>
    `;
    
    abrirModalPDV('💰 Suprimento', conteudo, 'info');
}

async function confirmarSuprimento() {
    const valor = getValorNumerico(valorAtual);
    const motivo = document.getElementById('inputMotivo')?.value || '';
    
    if (valor <= 0) {
        mostrarNotificacao('Informe o valor do suprimento', 'erro');
        return;
    }
    
    const dados = {
        tipo: 'entrada',
        categoria: 'suprimento',
        valor: valor,
        descricao: motivo
    };
    
    try {
        const resultado = await API.criarLancamento(dados);
        
        if (resultado.success) {
            mostrarNotificacao('Suprimento registrado com sucesso!', 'sucesso');
            fecharModalPDV();
            await carregarPainel();
            await carregarUltimosLancamentos();
        } else {
            mostrarNotificacao(resultado.message, 'erro');
        }
    } catch (error) {
        console.error('Erro ao registrar suprimento:', error);
        mostrarNotificacao('Erro ao registrar suprimento', 'erro');
    }
}

// ====================================
// MODAL OUTROS
// ====================================

let tipoOutros = 'entrada';

function modalOutros() {
    tipoOutros = 'entrada';
    
    const conteudo = `
        <div class="modal-layout-horizontal">
            <div class="modal-lado-esquerdo">
                <div class="form-group-pdv">
                    <label>TIPO DE LANÇAMENTO</label>
                    <div class="tipo-toggle">
                        <button class="tipo-btn active entrada" onclick="setarTipoOutros('entrada')" id="btnEntrada">
                            ⬆️ ENTRADA
                        </button>
                        <button class="tipo-btn saida" onclick="setarTipoOutros('saida')" id="btnSaida">
                            ⬇️ SAÍDA
                        </button>
                    </div>
                </div>
                
                <div class="form-group-pdv">
                    <label>VALOR</label>
                    <div class="valor-display ativo" id="containerValor" onclick="setarCampoAtivo('valor')">
                        <div class="valor-display-label">Valor do lançamento</div>
                        <div class="valor-display-numero" id="displayValor">R$ 0,00</div>
                    </div>
                </div>
                
                <div class="form-group-pdv">
                    <label>DESCRIÇÃO *</label>
                    <input type="text" id="inputDescricao" class="form-control-pdv" placeholder="Descrição do lançamento" required>
                </div>
            </div>
            
            <div class="modal-lado-direito">
                <div class="teclado-virtual compacto">
                    <button class="tecla" onclick="teclarNumero('1')">1</button>
                    <button class="tecla" onclick="teclarNumero('2')">2</button>
                    <button class="tecla" onclick="teclarNumero('3')">3</button>
                    <button class="tecla" onclick="teclarNumero('4')">4</button>
                    <button class="tecla" onclick="teclarNumero('5')">5</button>
                    <button class="tecla" onclick="teclarNumero('6')">6</button>
                    <button class="tecla" onclick="teclarNumero('7')">7</button>
                    <button class="tecla" onclick="teclarNumero('8')">8</button>
                    <button class="tecla" onclick="teclarNumero('9')">9</button>
                    <button class="tecla limpar" onclick="limparTeclado()">C</button>
                    <button class="tecla" onclick="teclarNumero('0')">0</button>
                    <button class="tecla backspace" onclick="apagarUltimo()">⌫</button>
                    <button class="tecla confirmar" onclick="confirmarOutros()">📝 CONFIRMAR</button>
                </div>
            </div>
        </div>
    `;
    
    abrirModalPDV('📝 Outros Lançamentos', conteudo, 'primary');
}

function setarTipoOutros(tipo) {
    tipoOutros = tipo;
    
    document.querySelectorAll('.tipo-btn').forEach(btn => btn.classList.remove('active'));
    document.getElementById(tipo === 'entrada' ? 'btnEntrada' : 'btnSaida').classList.add('active');
}

async function confirmarOutros() {
    const valor = getValorNumerico(valorAtual);
    const descricao = document.getElementById('inputDescricao')?.value || '';
    
    if (valor <= 0) {
        mostrarNotificacao('Informe o valor', 'erro');
        return;
    }
    
    if (!descricao) {
        mostrarNotificacao('Informe a descrição', 'erro');
        return;
    }
    
    const dados = {
        tipo: tipoOutros,
        categoria: 'outros',
        valor: valor,
        descricao: descricao
    };
    
    try {
        const resultado = await API.criarLancamento(dados);
        
        if (resultado.success) {
            mostrarNotificacao('Lançamento registrado com sucesso!', 'sucesso');
            fecharModalPDV();
            await carregarPainel();
            await carregarUltimosLancamentos();
        } else {
            mostrarNotificacao(resultado.message, 'erro');
        }
    } catch (error) {
        console.error('Erro ao registrar lançamento:', error);
        mostrarNotificacao('Erro ao registrar lançamento', 'erro');
    }
}

// ====================================
// MODAL FECHAR CAIXA
// ====================================

let resumoFechamento = null;

async function modalFecharCaixa() {
    if (!caixaAtual) return;
    
    // Carregar resumo detalhado
    try {
        const resultado = await API.resumoFechamento();
        if (resultado.success) {
            resumoFechamento = resultado;
        } else {
            mostrarNotificacao('Erro ao carregar resumo', 'erro');
            return;
        }
    } catch (error) {
        console.error('Erro ao carregar resumo:', error);
        mostrarNotificacao('Erro ao carregar resumo', 'erro');
        return;
    }
    
    const v = resumoFechamento.vendas;
    const m = resumoFechamento.movimentacoes;
    
    const conteudo = `
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
            <!-- Resumo de Vendas -->
            <div style="background: rgba(0,0,0,0.2); border-radius: 10px; padding: 0.75rem;">
                <h4 style="color: #26a269; margin-bottom: 0.5rem; font-size: 0.85rem;">💳 VENDAS DO DIA</h4>
                <div style="display: flex; flex-direction: column; gap: 0.25rem; font-size: 0.8rem;">
                    ${v.dinheiro > 0 ? `<div style="display: flex; justify-content: space-between;"><span>💵 Dinheiro</span><span style="color: #26a269;">${formatarMoeda(v.dinheiro)}</span></div>` : ''}
                    ${v.pix > 0 ? `<div style="display: flex; justify-content: space-between;"><span>📱 PIX</span><span style="color: #26a269;">${formatarMoeda(v.pix)}</span></div>` : ''}
                    ${v.cartao_credito > 0 ? `<div style="display: flex; justify-content: space-between;"><span>💳 Crédito</span><span style="color: #26a269;">${formatarMoeda(v.cartao_credito)}</span></div>` : ''}
                    ${v.cartao_debito > 0 ? `<div style="display: flex; justify-content: space-between;"><span>💳 Débito</span><span style="color: #26a269;">${formatarMoeda(v.cartao_debito)}</span></div>` : ''}
                    ${v.outras > 0 ? `<div style="display: flex; justify-content: space-between;"><span>📦 Outras</span><span style="color: #26a269;">${formatarMoeda(v.outras)}</span></div>` : ''}
                    <div style="display: flex; justify-content: space-between; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 0.35rem; margin-top: 0.25rem; font-weight: 700;">
                        <span>TOTAL VENDAS</span><span style="color: #26a269;">${formatarMoeda(v.total)}</span>
                    </div>
                </div>
            </div>
            
            <!-- Movimentações -->
            <div style="background: rgba(0,0,0,0.2); border-radius: 10px; padding: 0.75rem;">
                <h4 style="color: #1c71d8; margin-bottom: 0.5rem; font-size: 0.85rem;">📊 MOVIMENTAÇÕES</h4>
                <div style="display: flex; flex-direction: column; gap: 0.25rem; font-size: 0.8rem;">
                    <div style="display: flex; justify-content: space-between;"><span>💰 Troco Inicial</span><span>${formatarMoeda(resumoFechamento.troco_inicial)}</span></div>
                    ${m.suprimentos > 0 ? `<div style="display: flex; justify-content: space-between;"><span>⬆️ Suprimentos</span><span style="color: #26a269;">+${formatarMoeda(m.suprimentos)}</span></div>` : ''}
                    ${m.sangrias > 0 ? `<div style="display: flex; justify-content: space-between;"><span>⬇️ Sangrias</span><span style="color: #c01c28;">-${formatarMoeda(m.sangrias)}</span></div>` : ''}
                    ${m.troco_dado > 0 ? `<div style="display: flex; justify-content: space-between;"><span>💵 Troco Dado</span><span style="color: #c01c28;">-${formatarMoeda(m.troco_dado)}</span></div>` : ''}
                </div>
            </div>
        </div>
        
        <!-- Dinheiro Esperado -->
        <div style="background: linear-gradient(135deg, #1a5fb4, #0d4a8f); border-radius: 10px; padding: 1rem; margin-bottom: 1rem; text-align: center;">
            <div style="font-size: 0.75rem; color: rgba(255,255,255,0.8); margin-bottom: 0.25rem;">💵 DINHEIRO ESPERADO NO CAIXA</div>
            <div style="font-size: 1.75rem; font-weight: 700; color: white;">${formatarMoeda(resumoFechamento.dinheiro_esperado)}</div>
            <div style="font-size: 0.7rem; color: rgba(255,255,255,0.6); margin-top: 0.25rem;">
                (Troco inicial + Vendas dinheiro - Troco dado - Sangrias + Suprimentos)
            </div>
        </div>
        
        <div class="modal-layout-horizontal">
            <div class="modal-lado-esquerdo">
                <div class="form-group-pdv">
                    <label>💵 VALOR CONTADO (DINHEIRO FÍSICO)</label>
                    <div class="valor-display ativo" id="containerValor" onclick="setarCampoAtivo('valor')">
                        <div class="valor-display-label">Conte o dinheiro no caixa</div>
                        <div class="valor-display-numero" id="displayValor">R$ 0,00</div>
                    </div>
                </div>
                
                <div id="diferencaInfo" class="info-message" style="display: none; padding: 0.75rem;">
                    <strong>Diferença:</strong> <span id="diferencaValor"></span>
                </div>
                
                <div class="form-group-pdv">
                    <label>OBSERVAÇÕES</label>
                    <input type="text" id="inputObs" class="form-control-pdv" placeholder="Observações do fechamento">
                </div>
            </div>
            
            <div class="modal-lado-direito">
                <div class="teclado-virtual compacto">
                    <button class="tecla" onclick="teclarNumeroFechar('1')">1</button>
                    <button class="tecla" onclick="teclarNumeroFechar('2')">2</button>
                    <button class="tecla" onclick="teclarNumeroFechar('3')">3</button>
                    <button class="tecla" onclick="teclarNumeroFechar('4')">4</button>
                    <button class="tecla" onclick="teclarNumeroFechar('5')">5</button>
                    <button class="tecla" onclick="teclarNumeroFechar('6')">6</button>
                    <button class="tecla" onclick="teclarNumeroFechar('7')">7</button>
                    <button class="tecla" onclick="teclarNumeroFechar('8')">8</button>
                    <button class="tecla" onclick="teclarNumeroFechar('9')">9</button>
                    <button class="tecla limpar" onclick="limparTeclado(); calcularDiferenca();">C</button>
                    <button class="tecla" onclick="teclarNumeroFechar('0')">0</button>
                    <button class="tecla backspace" onclick="apagarUltimo(); calcularDiferenca();">⌫</button>
                    <button class="tecla confirmar" style="background: #c01c28;" onclick="confirmarFecharCaixa()">🔒 FECHAR</button>
                </div>
            </div>
        </div>
    `;
    
    abrirModalPDV('🔒 Fechar Caixa', conteudo, 'danger');
}

function teclarNumeroFechar(num) {
    valorAtual += num;
    atualizarDisplayValor();
    calcularDiferenca();
}

function calcularDiferenca() {
    const valorContado = getValorNumerico(valorAtual);
    
    if (valorContado <= 0 || !resumoFechamento) {
        document.getElementById('diferencaInfo').style.display = 'none';
        return;
    }
    
    const diferenca = valorContado - resumoFechamento.dinheiro_esperado;
    const diferencaInfo = document.getElementById('diferencaInfo');
    const diferencaValor = document.getElementById('diferencaValor');
    
    diferencaInfo.style.display = 'block';
    
    if (diferenca > 0.01) {
        diferencaInfo.className = 'success-message';
        diferencaValor.innerHTML = `<span style="color: #26a269">+${formatarMoeda(diferenca)} (Sobra)</span>`;
    } else if (diferenca < -0.01) {
        diferencaInfo.className = 'error-message';
        diferencaValor.innerHTML = `<span style="color: #c01c28">${formatarMoeda(diferenca)} (Falta)</span>`;
    } else {
        diferencaInfo.className = 'success-message';
        diferencaValor.innerHTML = `<span style="color: #26a269">✅ Caixa conferido!</span>`;
    }
}

async function confirmarFecharCaixa() {
    if (!confirm('Tem certeza que deseja fechar o caixa? Esta ação não pode ser desfeita.')) {
        return;
    }
    
    const valorContado = getValorNumerico(valorAtual);
    const observacao = document.getElementById('inputObs')?.value || '';
    
    const dados = {
        observacao: observacao
    };
    
    if (valorContado > 0) {
        dados.valor_contado = valorContado;
    }
    
    try {
        const resultado = await API.fecharCaixa(dados);
        
        if (resultado.success) {
            mostrarNotificacao('Caixa fechado com sucesso!', 'sucesso');
            fecharModalPDV();
            await verificarCaixa();
        } else {
            mostrarNotificacao(resultado.message, 'erro');
        }
    } catch (error) {
        console.error('Erro ao fechar caixa:', error);
        mostrarNotificacao('Erro ao fechar caixa', 'erro');
    }
}

// ====================================
// PAINEL E LANÇAMENTOS
// ====================================

async function carregarPainel() {
    try {
        const painel = await API.painelCaixa();
        
        if (painel.success) {
            caixaAtual = painel.caixa;
            const totais = painel.totais;
            
            document.getElementById('trocoInicial').textContent = formatarMoeda(totais.troco_inicial);
            document.getElementById('totalEntradas').textContent = formatarMoeda(totais.total_entradas);
            document.getElementById('totalSaidas').textContent = formatarMoeda(totais.total_saidas);
            document.getElementById('saldoAtual').textContent = formatarMoeda(totais.saldo_atual);
            
            // Atualizar objeto caixaAtual com totais
            caixaAtual.total_entradas = totais.total_entradas;
            caixaAtual.total_saidas = totais.total_saidas;
            caixaAtual.saldo_atual = totais.saldo_atual;
        }
    } catch (error) {
        console.error('Erro ao carregar painel:', error);
    }
}

async function carregarUltimosLancamentos() {
    if (!caixaAtual) return;
    
    try {
        const resultado = await API.listarLancamentos({ caixa_id: caixaAtual.id });
        
        if (resultado.success) {
            const lancamentos = resultado.lancamentos.slice(0, 8); // Últimos 8
            renderizarLancamentos(lancamentos);
        }
    } catch (error) {
        console.error('Erro ao carregar lançamentos:', error);
    }
}

function renderizarLancamentos(lancamentos) {
    const container = document.getElementById('listaLancamentos');
    
    if (lancamentos.length === 0) {
        container.innerHTML = '<p class="text-center" style="color: var(--text-muted);">Nenhum lançamento ainda</p>';
        return;
    }
    
    container.innerHTML = lancamentos.map(l => `
        <div class="lancamento-item ${l.tipo}">
            <div class="lancamento-info">
                <div class="lancamento-categoria">${getCategoriaDisplay(l.categoria)}</div>
                <div class="lancamento-descricao">
                    ${l.forma_pagamento ? `${getIconeForma(l.forma_pagamento)} ${l.forma_pagamento}` : ''}
                    ${l.descricao ? `• ${l.descricao}` : ''}
                </div>
            </div>
            <div class="lancamento-valor ${l.tipo}">
                ${l.tipo === 'entrada' ? '+' : '-'}${formatarMoeda(l.valor)}
            </div>
        </div>
    `).join('');
}

function getCategoriaDisplay(categoria) {
    const map = {
        'venda': '💳 VENDA',
        'sangria': '💸 SANGRIA',
        'suprimento': '💰 SUPRIMENTO',
        'outros': '📝 OUTROS'
    };
    return map[categoria] || categoria.toUpperCase();
}
