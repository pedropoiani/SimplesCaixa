/**
 * PDV-MF - Controle de Caixa
 * Interface estilo PDV profissional com teclado virtual
 * Versao: 1.0.5 - 10/01/2026
 * ES5 Compativel (iOS 9+)
 */

var caixaAtual = null;
var dadosFechamentoTemp = null;
var formasPagamento = [];
var valorAtual = '';
var valorRecebidoAtual = '';
var campoAtivo = 'valor';
var formaSelecionada = '';
var tipoOutros = 'entrada';
var resumoFechamento = null;

// ====================================
// INICIALIZACAO
// ====================================

document.addEventListener('DOMContentLoaded', function() {
    inicializarCaixa();
});

function inicializarCaixa() {
    carregarFormasPagamento()
        .then(function() {
            return verificarCaixa();
        })
        .then(function() {
            return carregarNomeLoja();
        })
        .catch(function(error) {
            console.error('Erro na inicializacao:', error);
        });
}

function carregarNomeLoja() {
    return API.getConfiguracao()
        .then(function(config) {
            var el = document.getElementById('nomeLoja');
            if (el) {
                el.textContent = config.nome_loja || 'PDV-MF';
            }
        })
        .catch(function(error) {
            console.error('Erro ao carregar configuracoes:', error);
        });
}

function carregarFormasPagamento() {
    return API.getConfiguracao()
        .then(function(config) {
            formasPagamento = config.formas_pagamento || ['Dinheiro', 'PIX', 'Cartao Credito', 'Cartao Debito'];
        })
        .catch(function(error) {
            console.error('Erro ao carregar formas de pagamento:', error);
            formasPagamento = ['Dinheiro', 'PIX', 'Cartao Credito', 'Cartao Debito'];
        });
}

function verificarCaixa() {
    return API.caixaStatus()
        .then(function(status) {
            if (status.aberto) {
                caixaAtual = status.caixa;
                mostrarCaixaAberto();
                return carregarPainel()
                    .then(function() {
                        return carregarUltimosLancamentos();
                    });
            } else {
                caixaAtual = null;
                mostrarCaixaFechado();
            }
        })
        .catch(function(error) {
            console.error('Erro ao verificar caixa:', error);
            mostrarNotificacao('Erro ao verificar status do caixa', 'erro');
        });
}

function mostrarCaixaAberto() {
    var fechado = document.getElementById('caixaFechado');
    var aberto = document.getElementById('caixaAberto');
    
    if (fechado) fechado.style.display = 'none';
    if (aberto) aberto.style.display = 'block';
    
    var operadorEl = document.getElementById('nomeOperador');
    if (operadorEl) {
        if (caixaAtual && caixaAtual.operador) {
            operadorEl.textContent = caixaAtual.operador;
        } else {
            operadorEl.textContent = '-';
        }
    }
}

function mostrarCaixaFechado() {
    var fechado = document.getElementById('caixaFechado');
    var aberto = document.getElementById('caixaAberto');
    
    if (fechado) fechado.style.display = 'flex';
    if (aberto) aberto.style.display = 'none';
}

// ====================================
// NOTIFICACOES
// ====================================

function mostrarNotificacao(mensagem, tipo) {
    tipo = tipo || 'info';
    
    // Remove notificacao existente
    var existente = document.querySelector('.notificacao-pdv');
    if (existente) existente.parentNode.removeChild(existente);
    
    var icone = 'info' === tipo ? 'i' : ('sucesso' === tipo ? 'v' : 'x');
    var iconeTxt = tipo === 'sucesso' ? '✓' : (tipo === 'erro' ? '✗' : 'i');
    
    var notificacao = document.createElement('div');
    notificacao.className = 'notificacao-pdv ' + tipo;
    notificacao.innerHTML = '<span>' + iconeTxt + ' ' + mensagem + '</span>';
    
    var bgColor = '#1c71d8';
    if (tipo === 'sucesso') bgColor = '#26a269';
    if (tipo === 'erro') bgColor = '#c01c28';
    
    notificacao.style.cssText = 'position: fixed; top: 80px; right: 20px; padding: 1rem 1.5rem; border-radius: 12px; font-weight: 600; z-index: 9999; background: ' + bgColor + '; color: white;';
    
    document.body.appendChild(notificacao);
    
    setTimeout(function() {
        notificacao.style.opacity = '0';
        setTimeout(function() {
            if (notificacao.parentNode) {
                notificacao.parentNode.removeChild(notificacao);
            }
        }, 300);
    }, 3000);
}

// ====================================
// MODAL GENERICO PDV
// ====================================

function abrirModalPDV(titulo, conteudo, corHeader) {
    corHeader = corHeader || 'primary';
    fecharModalPDV();
    
    var cores = {
        primary: 'linear-gradient(135deg, #1a5fb4, #0d4a8f)',
        success: 'linear-gradient(135deg, #26a269, #1e8054)',
        danger: 'linear-gradient(135deg, #c01c28, #a11720)',
        warning: 'linear-gradient(135deg, #e5a50a, #c48d09)',
        info: 'linear-gradient(135deg, #1c71d8, #1a5fb4)'
    };
    
    var modal = document.createElement('div');
    modal.id = 'modalPDV';
    modal.className = 'modal-pdv show';
    modal.innerHTML = '<div class="modal-pdv-content">' +
        '<div class="modal-pdv-header" style="background: ' + (cores[corHeader] || cores.primary) + '">' +
            '<h3>' + titulo + '</h3>' +
            '<button class="modal-pdv-close" onclick="fecharModalPDV()">&times;</button>' +
        '</div>' +
        '<div class="modal-pdv-body">' + conteudo + '</div>' +
    '</div>';
    
    var container = document.getElementById('modalsContainer');
    if (container) {
        container.appendChild(modal);
    }
    
    // Fechar ao clicar fora
    modal.addEventListener('click', function(e) {
        if (e.target === modal) fecharModalPDV();
    });
}

function fecharModalPDV() {
    var modal = document.getElementById('modalPDV');
    if (modal && modal.parentNode) {
        modal.parentNode.removeChild(modal);
    }
    
    // Limpar variaveis
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
    var display = document.getElementById('displayValor');
    if (display) {
        display.textContent = formatarValorDisplay(valorAtual);
    }
    
    // Tambem atualizar input se existir
    var inputValor = document.getElementById('inputValor');
    if (inputValor) {
        inputValor.value = formatarValorDisplay(valorAtual);
    }
    
    calcularTroco();
}

function atualizarDisplayRecebido() {
    var display = document.getElementById('displayRecebido');
    if (display) {
        display.textContent = formatarValorDisplay(valorRecebidoAtual);
    }
    
    // Tambem atualizar input se existir
    var inputRecebido = document.getElementById('inputRecebido');
    if (inputRecebido) {
        inputRecebido.value = formatarValorDisplay(valorRecebidoAtual);
    }
    
    calcularTroco();
}

// Funcao para tratar input de teclado fisico
function configurarInputValor(inputId, campo) {
    var input = document.getElementById(inputId);
    if (!input) return;
    
    input.addEventListener('input', function(e) {
        var valor = e.target.value.replace(/\D/g, '');
        if (campo === 'valor') {
            valorAtual = valor;
            e.target.value = formatarValorDisplay(valorAtual);
        } else if (campo === 'recebido') {
            valorRecebidoAtual = valor;
            e.target.value = formatarValorDisplay(valorRecebidoAtual);
        }
        calcularTroco();
    });
    
    input.addEventListener('focus', function() {
        campoAtivo = campo;
    });
}

// ====================================
// MODAL DE CONFIRMACAO CUSTOMIZADO (iOS compativel)
// ====================================

function mostrarConfirmacao(titulo, mensagem, onConfirm) {
    var overlay = document.createElement('div');
    overlay.id = 'confirmOverlay';
    overlay.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.8); z-index: 10000; display: flex; align-items: center; justify-content: center;';
    
    var box = document.createElement('div');
    box.style.cssText = 'background: #2d2d2d; border-radius: 12px; padding: 1.5rem; max-width: 90%; width: 400px; text-align: center; border: 2px solid #c01c28;';
    
    box.innerHTML = '<div style="font-size: 1.2rem; font-weight: 700; color: #ff6b6b; margin-bottom: 1rem;">' + titulo + '</div>' +
        '<div style="font-size: 1rem; color: white; margin-bottom: 1.5rem; line-height: 1.4;">' + mensagem + '</div>' +
        '<div style="display: flex; gap: 1rem; justify-content: center;">' +
            '<button id="btnCancelarConfirm" style="padding: 0.8rem 1.5rem; border: none; border-radius: 8px; font-size: 1rem; font-weight: 600; background: #555; color: white; cursor: pointer; min-width: 100px;">CANCELAR</button>' +
            '<button id="btnConfirmarConfirm" style="padding: 0.8rem 1.5rem; border: none; border-radius: 8px; font-size: 1rem; font-weight: 600; background: #c01c28; color: white; cursor: pointer; min-width: 100px;">CONFIRMAR</button>' +
        '</div>';
    
    overlay.appendChild(box);
    document.body.appendChild(overlay);
    
    document.getElementById('btnCancelarConfirm').onclick = function() {
        document.body.removeChild(overlay);
    };
    
    document.getElementById('btnConfirmarConfirm').onclick = function() {
        document.body.removeChild(overlay);
        if (onConfirm) onConfirm();
    };
}

// Gerar teclado inline compacto (2 linhas)
function gerarTecladoInline(btnConfirmarTexto, btnConfirmarOnclick) {
    return '<div class="teclado-inline">' +
        '<div class="teclado-linha">' +
            '<button class="tecla-inline" onclick="teclarNumero(\'1\')">1</button>' +
            '<button class="tecla-inline" onclick="teclarNumero(\'2\')">2</button>' +
            '<button class="tecla-inline" onclick="teclarNumero(\'3\')">3</button>' +
            '<button class="tecla-inline" onclick="teclarNumero(\'4\')">4</button>' +
            '<button class="tecla-inline" onclick="teclarNumero(\'5\')">5</button>' +
            '<button class="tecla-inline" onclick="teclarNumero(\'6\')">6</button>' +
            '<button class="tecla-inline" onclick="teclarNumero(\'7\')">7</button>' +
            '<button class="tecla-inline" onclick="teclarNumero(\'8\')">8</button>' +
            '<button class="tecla-inline" onclick="teclarNumero(\'9\')">9</button>' +
            '<button class="tecla-inline" onclick="teclarNumero(\'0\')">0</button>' +
            '<button class="tecla-inline limpar" onclick="limparTeclado()">C</button>' +
            '<button class="tecla-inline backspace" onclick="apagarUltimo()">⌫</button>' +
        '</div>' +
        '<button class="btn-confirmar-inline" onclick="' + btnConfirmarOnclick + '">' + btnConfirmarTexto + '</button>' +
    '</div>';
}

function formatarValorDisplay(valor) {
    if (!valor) return 'R$ 0,00';
    
    // Remove tudo que nao e numero
    valor = valor.replace(/\D/g, '');
    
    // Converte para centavos
    var centavos = parseInt(valor, 10) || 0;
    var reais = centavos / 100;
    
    return formatarMoeda(reais);
}

function getValorNumerico(valorStr) {
    if (!valorStr) return 0;
    valorStr = valorStr.replace(/\D/g, '');
    return (parseInt(valorStr, 10) || 0) / 100;
}

function calcularTroco() {
    var trocoDisplay = document.getElementById('displayTroco');
    var secaoTroco = document.getElementById('secaoTroco');
    if (!trocoDisplay || !secaoTroco) return;
    
    var valor = getValorNumerico(valorAtual);
    var recebido = getValorNumerico(valorRecebidoAtual);
    var troco = recebido - valor;
    
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
    var displays = document.querySelectorAll('.valor-display');
    for (var i = 0; i < displays.length; i++) {
        displays[i].classList.remove('ativo');
    }
    
    var displayAtivo = document.getElementById(campo === 'valor' ? 'containerValor' : 'containerRecebido');
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
    var conteudo = '<div class="modal-simples">' +
        '<div class="form-group-pdv">' +
            '<label>OPERADOR</label>' +
            '<input type="text" id="inputOperador" class="form-control-pdv" placeholder="Nome do operador">' +
        '</div>' +
        '<div class="form-group-pdv">' +
            '<label class="input-valor-label">TROCO INICIAL</label>' +
            '<input type="text" id="inputValor" class="input-valor" placeholder="R$ 0,00" inputmode="numeric" pattern="[0-9]*">' +
        '</div>' +
        gerarTecladoInline('🔓 ABRIR CAIXA', 'confirmarAbrirCaixa()') +
    '</div>';
    
    abrirModalPDV('Abrir Caixa', conteudo, 'success');
    
    setTimeout(function() {
        configurarInputValor('inputValor', 'valor');
    }, 100);
}

function confirmarAbrirCaixa() {
    var operadorInput = document.getElementById('inputOperador');
    var operador = operadorInput ? operadorInput.value : '';
    var troco = getValorNumerico(valorAtual);
    
    API.abrirCaixa({
        operador: operador,
        troco_inicial: troco
    })
    .then(function(resultado) {
        if (resultado.success) {
            mostrarNotificacao('Caixa aberto com sucesso!', 'sucesso');
            fecharModalPDV();
            return verificarCaixa();
        } else {
            mostrarNotificacao(resultado.message, 'erro');
        }
    })
    .catch(function(error) {
        console.error('Erro ao abrir caixa:', error);
        mostrarNotificacao('Erro ao abrir caixa', 'erro');
    });
}

// ====================================
// MODAL VENDA
// ====================================

function modalVenda() {
    formaSelecionada = '';
    
    var formasHtml = '';
    for (var i = 0; i < formasPagamento.length; i++) {
        var forma = formasPagamento[i];
        var formaId = forma.replace(/\s/g, '');
        formasHtml += '<button class="forma-btn" onclick="selecionarForma(\'' + forma + '\')" id="forma-' + formaId + '">' +
            '<span>' + getIconeForma(forma) + ' ' + forma + '</span>' +
        '</button>';
    }
    
    var conteudo = '<div class="modal-simples">' +
        '<div class="form-group-pdv">' +
            '<label>FORMA DE PAGAMENTO</label>' +
            '<div class="formas-pagamento-grid">' + formasHtml + '</div>' +
        '</div>' +
        '<div id="areaValorVenda" style="display: none;">' +
            '<div class="form-group-pdv">' +
                '<label class="input-valor-label">VALOR DA VENDA</label>' +
                '<input type="text" id="inputValor" class="input-valor" placeholder="R$ 0,00" inputmode="numeric" pattern="[0-9]*">' +
            '</div>' +
            '<div id="areaDinheiro" style="display: none;">' +
                '<div class="form-group-pdv">' +
                    '<label class="input-valor-label">VALOR RECEBIDO</label>' +
                    '<input type="text" id="inputRecebido" class="input-valor" style="font-size: 1.2rem;" placeholder="R$ 0,00" inputmode="numeric" pattern="[0-9]*">' +
                '</div>' +
                '<div class="valores-rapidos">' +
                    '<button class="valor-rapido-btn" onclick="setarValorRapido(10)">R$10</button>' +
                    '<button class="valor-rapido-btn" onclick="setarValorRapido(20)">R$20</button>' +
                    '<button class="valor-rapido-btn" onclick="setarValorRapido(50)">R$50</button>' +
                    '<button class="valor-rapido-btn" onclick="setarValorRapido(100)">R$100</button>' +
                '</div>' +
                '<div class="secao-troco" id="secaoTroco" style="display: none;">' +
                    '<h4>TROCO</h4>' +
                    '<div class="valor-display-numero" id="displayTroco" style="font-size: 1.3rem; color: #26a269;">R$ 0,00</div>' +
                '</div>' +
            '</div>' +
        '</div>' +
        gerarTecladoInline('💳 CONFIRMAR VENDA', 'confirmarVenda()') +
    '</div>';
    
    abrirModalPDV('Nova Venda', conteudo, 'success');
    
    setTimeout(function() {
        configurarInputValor('inputValor', 'valor');
        configurarInputValor('inputRecebido', 'recebido');
    }, 100);
}

function getIconeForma(forma) {
    var icones = {
        'Dinheiro': '$',
        'PIX': 'P',
        'Cartao Credito': 'C',
        'Cartao Debito': 'D',
        'Credito': 'C',
        'Debito': 'D',
        'Transferencia': 'T',
        'Cheque': 'Q'
    };
    return icones[forma] || '$';
}

function selecionarForma(forma) {
    formaSelecionada = forma;
    
    // Atualizar visual
    var btns = document.querySelectorAll('.forma-btn');
    for (var i = 0; i < btns.length; i++) {
        btns[i].classList.remove('active');
    }
    var formaId = forma.replace(/\s/g, '');
    var btnSelecionado = document.getElementById('forma-' + formaId);
    if (btnSelecionado) {
        btnSelecionado.classList.add('active');
    }
    
    // Mostrar area de valor
    var areaValor = document.getElementById('areaValorVenda');
    if (areaValor) areaValor.style.display = 'block';
    
    // Mostrar/esconder campos especificos de dinheiro
    var areaDinheiro = document.getElementById('areaDinheiro');
    if (areaDinheiro) {
        areaDinheiro.style.display = (forma === 'Dinheiro') ? 'block' : 'none';
    }
    
    // Limpar valores
    valorAtual = '';
    valorRecebidoAtual = '';
    campoAtivo = 'valor';
    atualizarDisplayValor();
}

function confirmarVenda() {
    if (!formaSelecionada) {
        mostrarNotificacao('Selecione a forma de pagamento', 'erro');
        return;
    }
    
    var valor = getValorNumerico(valorAtual);
    
    if (valor <= 0) {
        mostrarNotificacao('Informe o valor da venda', 'erro');
        return;
    }
    
    // Validacao especifica para dinheiro
    if (formaSelecionada === 'Dinheiro') {
        var recebido = getValorNumerico(valorRecebidoAtual);
        
        if (recebido <= 0) {
            mostrarNotificacao('Informe o valor recebido', 'erro');
            return;
        }
        
        if (recebido < valor) {
            mostrarNotificacao('Valor recebido menor que o valor da venda', 'erro');
            return;
        }
    }
    
    var dados = {
        tipo: 'entrada',
        categoria: 'venda',
        forma_pagamento: formaSelecionada,
        valor: valor,
        descricao: ''
    };
    
    if (formaSelecionada === 'Dinheiro') {
        dados.valor_recebido = getValorNumerico(valorRecebidoAtual);
    }
    
    API.criarLancamento(dados)
        .then(function(resultado) {
            if (resultado.success) {
                mostrarNotificacao('Venda registrada com sucesso!', 'sucesso');
                fecharModalPDV();
                return carregarPainel()
                    .then(function() {
                        return carregarUltimosLancamentos();
                    });
            } else {
                mostrarNotificacao(resultado.message, 'erro');
            }
        })
        .catch(function(error) {
            console.error('Erro ao registrar venda:', error);
            mostrarNotificacao('Erro ao registrar venda', 'erro');
        });
}

// ====================================
// MODAL SANGRIA
// ====================================

function modalSangria() {
    var conteudo = '<div class="modal-simples">' +
        '<div class="info-message" style="margin-bottom: 0.5rem; padding: 0.5rem; font-size: 0.8rem;">' +
            'Sangria e a retirada de dinheiro do caixa' +
        '</div>' +
        '<div class="form-group-pdv">' +
            '<label class="input-valor-label">VALOR DA SANGRIA</label>' +
            '<input type="text" id="inputValor" class="input-valor" placeholder="R$ 0,00" inputmode="numeric" pattern="[0-9]*">' +
        '</div>' +
        '<div class="form-group-pdv">' +
            '<label>MOTIVO RAPIDO</label>' +
            '<div class="motivos-rapidos">' +
                '<button class="motivo-btn" onclick="setarMotivo(\'Alimentacao\')">Alimentacao</button>' +
                '<button class="motivo-btn" onclick="setarMotivo(\'Embalagem\')">Embalagem</button>' +
                '<button class="motivo-btn" onclick="setarMotivo(\'Pro-labore\')">Pro-labore</button>' +
                '<button class="motivo-btn" onclick="setarMotivo(\'Transporte\')">Transporte</button>' +
                '<button class="motivo-btn" onclick="setarMotivo(\'Pagamento\')">Pagamento</button>' +
                '<button class="motivo-btn" onclick="setarMotivo(\'Retirada banco\')">Banco</button>' +
            '</div>' +
        '</div>' +
        '<div class="form-group-pdv">' +
            '<label>MOTIVO</label>' +
            '<input type="text" id="inputMotivo" class="form-control-pdv" placeholder="Ou digite aqui...">' +
        '</div>' +
        gerarTecladoInline('💸 CONFIRMAR SANGRIA', 'confirmarSangria()') +
    '</div>';
    
    abrirModalPDV('Sangria', conteudo, 'danger');
    
    setTimeout(function() {
        configurarInputValor('inputValor', 'valor');
    }, 100);
}

function setarMotivo(motivo) {
    var input = document.getElementById('inputMotivo');
    if (input) input.value = motivo;
    
    // Atualizar visual dos botoes
    var btns = document.querySelectorAll('.motivo-btn');
    for (var i = 0; i < btns.length; i++) {
        btns[i].classList.remove('active');
    }
    if (event && event.target) {
        event.target.classList.add('active');
    }
}

function confirmarSangria() {
    var valor = getValorNumerico(valorAtual);
    var motivoInput = document.getElementById('inputMotivo');
    var motivo = motivoInput ? motivoInput.value : '';
    
    if (valor <= 0) {
        mostrarNotificacao('Informe o valor da sangria', 'erro');
        return;
    }
    
    var dados = {
        tipo: 'saida',
        categoria: 'sangria',
        valor: valor,
        descricao: motivo
    };
    
    API.criarLancamento(dados)
        .then(function(resultado) {
            if (resultado.success) {
                mostrarNotificacao('Sangria registrada com sucesso!', 'sucesso');
                fecharModalPDV();
                return carregarPainel()
                    .then(function() {
                        return carregarUltimosLancamentos();
                    });
            } else {
                mostrarNotificacao(resultado.message, 'erro');
            }
        })
        .catch(function(error) {
            console.error('Erro ao registrar sangria:', error);
            mostrarNotificacao('Erro ao registrar sangria', 'erro');
        });
}

// ====================================
// MODAL SUPRIMENTO
// ====================================

function modalSuprimento() {
    var conteudo = '<div class="modal-simples">' +
        '<div class="info-message" style="margin-bottom: 0.5rem; padding: 0.5rem; font-size: 0.8rem;">' +
            'Suprimento e a entrada de dinheiro no caixa' +
        '</div>' +
        '<div class="form-group-pdv">' +
            '<label class="input-valor-label">VALOR DO SUPRIMENTO</label>' +
            '<input type="text" id="inputValor" class="input-valor" placeholder="R$ 0,00" inputmode="numeric" pattern="[0-9]*">' +
        '</div>' +
        '<div class="form-group-pdv">' +
            '<label>MOTIVO RAPIDO</label>' +
            '<div class="motivos-rapidos">' +
                '<button class="motivo-btn" onclick="setarMotivo(\'Troco do banco\')">Troco banco</button>' +
                '<button class="motivo-btn" onclick="setarMotivo(\'Reforco de caixa\')">Reforco</button>' +
                '<button class="motivo-btn" onclick="setarMotivo(\'Devolucao\')">Devolucao</button>' +
                '<button class="motivo-btn" onclick="setarMotivo(\'Acerto\')">Acerto</button>' +
            '</div>' +
        '</div>' +
        '<div class="form-group-pdv">' +
            '<label>MOTIVO</label>' +
            '<input type="text" id="inputMotivo" class="form-control-pdv" placeholder="Ou digite aqui...">' +
        '</div>' +
        gerarTecladoInline('💰 CONFIRMAR SUPRIMENTO', 'confirmarSuprimento()') +
    '</div>';
    
    abrirModalPDV('Suprimento', conteudo, 'info');
    
    setTimeout(function() {
        configurarInputValor('inputValor', 'valor');
    }, 100);
}

function confirmarSuprimento() {
    var valor = getValorNumerico(valorAtual);
    var motivoInput = document.getElementById('inputMotivo');
    var motivo = motivoInput ? motivoInput.value : '';
    
    if (valor <= 0) {
        mostrarNotificacao('Informe o valor do suprimento', 'erro');
        return;
    }
    
    var dados = {
        tipo: 'entrada',
        categoria: 'suprimento',
        valor: valor,
        descricao: motivo
    };
    
    API.criarLancamento(dados)
        .then(function(resultado) {
            if (resultado.success) {
                mostrarNotificacao('Suprimento registrado com sucesso!', 'sucesso');
                fecharModalPDV();
                return carregarPainel()
                    .then(function() {
                        return carregarUltimosLancamentos();
                    });
            } else {
                mostrarNotificacao(resultado.message, 'erro');
            }
        })
        .catch(function(error) {
            console.error('Erro ao registrar suprimento:', error);
            mostrarNotificacao('Erro ao registrar suprimento', 'erro');
        });
}

// ====================================
// MODAL OUTROS
// ====================================

function modalOutros() {
    tipoOutros = 'entrada';
    
    var conteudo = '<div class="modal-simples">' +
        '<div class="form-group-pdv">' +
            '<label>TIPO DE LANCAMENTO</label>' +
            '<div class="tipo-toggle">' +
                '<button class="tipo-btn active entrada" onclick="setarTipoOutros(\'entrada\')" id="btnEntrada">' +
                    'ENTRADA' +
                '</button>' +
                '<button class="tipo-btn saida" onclick="setarTipoOutros(\'saida\')" id="btnSaida">' +
                    'SAIDA' +
                '</button>' +
            '</div>' +
        '</div>' +
        '<div class="form-group-pdv">' +
            '<label class="input-valor-label">VALOR</label>' +
            '<input type="text" id="inputValor" class="input-valor" placeholder="R$ 0,00" inputmode="numeric" pattern="[0-9]*">' +
        '</div>' +
        '<div class="form-group-pdv">' +
            '<label>DESCRICAO *</label>' +
            '<input type="text" id="inputDescricao" class="form-control-pdv" placeholder="Descricao do lancamento" required>' +
        '</div>' +
        gerarTecladoInline('📝 CONFIRMAR', 'confirmarOutros()') +
    '</div>';
    
    abrirModalPDV('Outros Lancamentos', conteudo, 'primary');
    
    setTimeout(function() {
        configurarInputValor('inputValor', 'valor');
    }, 100);
}

function setarTipoOutros(tipo) {
    tipoOutros = tipo;
    
    var btns = document.querySelectorAll('.tipo-btn');
    for (var i = 0; i < btns.length; i++) {
        btns[i].classList.remove('active');
    }
    var btnId = (tipo === 'entrada') ? 'btnEntrada' : 'btnSaida';
    var btn = document.getElementById(btnId);
    if (btn) btn.classList.add('active');
}

function confirmarOutros() {
    var valor = getValorNumerico(valorAtual);
    var descInput = document.getElementById('inputDescricao');
    var descricao = descInput ? descInput.value : '';
    
    if (valor <= 0) {
        mostrarNotificacao('Informe o valor', 'erro');
        return;
    }
    
    if (!descricao) {
        mostrarNotificacao('Informe a descricao', 'erro');
        return;
    }
    
    var dados = {
        tipo: tipoOutros,
        categoria: 'outros',
        valor: valor,
        descricao: descricao
    };
    
    API.criarLancamento(dados)
        .then(function(resultado) {
            if (resultado.success) {
                mostrarNotificacao('Lancamento registrado com sucesso!', 'sucesso');
                fecharModalPDV();
                return carregarPainel()
                    .then(function() {
                        return carregarUltimosLancamentos();
                    });
            } else {
                mostrarNotificacao(resultado.message, 'erro');
            }
        })
        .catch(function(error) {
            console.error('Erro ao registrar lancamento:', error);
            mostrarNotificacao('Erro ao registrar lancamento', 'erro');
        });
}

// ====================================
// MODAL FECHAR CAIXA
// ====================================

function modalFecharCaixa() {
    if (!caixaAtual) return;
    
    // Carregar resumo detalhado
    API.resumoFechamento()
        .then(function(resultado) {
            if (resultado.success) {
                resumoFechamento = resultado;
                mostrarModalFechar();
            } else {
                mostrarNotificacao('Erro ao carregar resumo', 'erro');
            }
        })
        .catch(function(error) {
            console.error('Erro ao carregar resumo:', error);
            mostrarNotificacao('Erro ao carregar resumo', 'erro');
        });
}

function mostrarModalFechar() {
    var v = resumoFechamento.vendas;
    var m = resumoFechamento.movimentacoes;
    
    var vendasHtml = '';
    if (v.dinheiro > 0) vendasHtml += '<div style="display: flex; justify-content: space-between;"><span>Dinheiro</span><span style="color: #26a269;">' + formatarMoeda(v.dinheiro) + '</span></div>';
    if (v.pix > 0) vendasHtml += '<div style="display: flex; justify-content: space-between;"><span>PIX</span><span style="color: #26a269;">' + formatarMoeda(v.pix) + '</span></div>';
    if (v.cartao_credito > 0) vendasHtml += '<div style="display: flex; justify-content: space-between;"><span>Credito</span><span style="color: #26a269;">' + formatarMoeda(v.cartao_credito) + '</span></div>';
    if (v.cartao_debito > 0) vendasHtml += '<div style="display: flex; justify-content: space-between;"><span>Debito</span><span style="color: #26a269;">' + formatarMoeda(v.cartao_debito) + '</span></div>';
    if (v.outras > 0) vendasHtml += '<div style="display: flex; justify-content: space-between;"><span>Outras</span><span style="color: #26a269;">' + formatarMoeda(v.outras) + '</span></div>';
    
    var movHtml = '<div style="display: flex; justify-content: space-between;"><span>Troco Inicial</span><span>' + formatarMoeda(resumoFechamento.troco_inicial) + '</span></div>';
    if (m.suprimentos > 0) movHtml += '<div style="display: flex; justify-content: space-between;"><span>Suprimentos</span><span style="color: #26a269;">+' + formatarMoeda(m.suprimentos) + '</span></div>';
    if (m.sangrias > 0) movHtml += '<div style="display: flex; justify-content: space-between;"><span>Sangrias</span><span style="color: #c01c28;">-' + formatarMoeda(m.sangrias) + '</span></div>';
    if (m.troco_dado > 0) movHtml += '<div style="display: flex; justify-content: space-between;"><span>Troco Dado</span><span style="color: #c01c28;">-' + formatarMoeda(m.troco_dado) + '</span></div>';
    
    var conteudo = '<div class="modal-simples">' +
        '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-bottom: 0.5rem;">' +
            '<div style="background: rgba(0,0,0,0.2); border-radius: 8px; padding: 0.5rem;">' +
                '<h4 style="color: #26a269; margin-bottom: 0.35rem; font-size: 0.7rem;">VENDAS DO DIA</h4>' +
                '<div style="display: flex; flex-direction: column; gap: 0.15rem; font-size: 0.7rem;">' +
                    vendasHtml +
                    '<div style="display: flex; justify-content: space-between; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 0.25rem; margin-top: 0.15rem; font-weight: 700;">' +
                        '<span>TOTAL</span><span style="color: #26a269;">' + formatarMoeda(v.total) + '</span>' +
                    '</div>' +
                '</div>' +
            '</div>' +
            '<div style="background: rgba(0,0,0,0.2); border-radius: 8px; padding: 0.5rem;">' +
                '<h4 style="color: #1c71d8; margin-bottom: 0.35rem; font-size: 0.7rem;">MOVIMENTACOES</h4>' +
                '<div style="display: flex; flex-direction: column; gap: 0.15rem; font-size: 0.7rem;">' +
                    movHtml +
                '</div>' +
            '</div>' +
        '</div>' +
        '<div style="background: linear-gradient(135deg, #1a5fb4, #0d4a8f); border-radius: 8px; padding: 0.6rem; margin-bottom: 0.5rem; text-align: center;">' +
            '<div style="font-size: 0.6rem; color: rgba(255,255,255,0.8);">DINHEIRO ESPERADO NO CAIXA</div>' +
            '<div style="font-size: 1.4rem; font-weight: 700; color: white;">' + formatarMoeda(resumoFechamento.dinheiro_esperado) + '</div>' +
        '</div>' +
        '<div class="form-group-pdv">' +
            '<label class="input-valor-label">VALOR CONTADO (DINHEIRO FISICO)</label>' +
            '<input type="text" id="inputValor" class="input-valor" placeholder="R$ 0,00" inputmode="numeric" pattern="[0-9]*" oninput="calcularDiferencaInput()">' +
        '</div>' +
        '<div id="diferencaInfo" class="info-message" style="display: none; padding: 0.4rem; font-size: 0.8rem;">' +
            '<strong>Diferenca:</strong> <span id="diferencaValor"></span>' +
        '</div>' +
        '<div class="form-group-pdv">' +
            '<label>OBSERVACOES</label>' +
            '<input type="text" id="inputObs" class="form-control-pdv" placeholder="Observacoes do fechamento">' +
        '</div>' +
        gerarTecladoInline('🔒 FECHAR CAIXA', 'confirmarFecharCaixa()') +
    '</div>';
    
    abrirModalPDV('Fechar Caixa', conteudo, 'danger');
    
    setTimeout(function() {
        configurarInputValor('inputValor', 'valor');
    }, 100);
}

function calcularDiferencaInput() {
    var input = document.getElementById('inputValor');
    if (input) {
        var valor = input.value.replace(/\D/g, '');
        valorAtual = valor;
        input.value = formatarValorDisplay(valorAtual);
    }
    calcularDiferenca();
}

function teclarNumeroFechar(num) {
    valorAtual += num;
    atualizarDisplayValor();
    calcularDiferenca();
}

function calcularDiferenca() {
    var valorContado = getValorNumerico(valorAtual);
    var diferencaInfo = document.getElementById('diferencaInfo');
    var diferencaValor = document.getElementById('diferencaValor');
    
    if (valorContado <= 0 || !resumoFechamento) {
        if (diferencaInfo) diferencaInfo.style.display = 'none';
        return;
    }
    
    var diferenca = valorContado - resumoFechamento.dinheiro_esperado;
    
    if (diferencaInfo) diferencaInfo.style.display = 'block';
    
    if (diferenca > 0.01) {
        if (diferencaInfo) diferencaInfo.className = 'success-message';
        if (diferencaValor) diferencaValor.innerHTML = '<span style="color: #26a269">+' + formatarMoeda(diferenca) + ' (Sobra)</span>';
    } else if (diferenca < -0.01) {
        if (diferencaInfo) diferencaInfo.className = 'error-message';
        if (diferencaValor) diferencaValor.innerHTML = '<span style="color: #c01c28">' + formatarMoeda(diferenca) + ' (Falta)</span>';
    } else {
        if (diferencaInfo) diferencaInfo.className = 'success-message';
        if (diferencaValor) diferencaValor.innerHTML = '<span style="color: #26a269">Caixa conferido!</span>';
    }
}

function confirmarFecharCaixa() {
    var valorContado = getValorNumerico(valorAtual);
    var obsInput = document.getElementById('inputObs');
    var observacao = obsInput ? obsInput.value : '';
    
    // Guardar dados temporariamente
    dadosFechamentoTemp = {
        observacao: observacao,
        valor_contado: valorContado > 0 ? valorContado : null
    };
    
    // Fechar modal atual e mostrar confirmacao
    fecharModalPDV();
    
    mostrarConfirmacao(
        '⚠️ FECHAR CAIXA',
        'Tem certeza que deseja fechar o caixa?<br><br>Esta acao NAO pode ser desfeita.',
        executarFechamentoCaixa
    );
}

function executarFechamentoCaixa() {
    if (!dadosFechamentoTemp) return;
    
    var dados = {
        observacao: dadosFechamentoTemp.observacao
    };
    
    if (dadosFechamentoTemp.valor_contado) {
        dados.valor_contado = dadosFechamentoTemp.valor_contado;
    }
    
    API.fecharCaixa(dados)
        .then(function(resultado) {
            if (resultado.success) {
                mostrarNotificacao('Caixa fechado com sucesso!', 'sucesso');
                dadosFechamentoTemp = null;
                return verificarCaixa();
            } else {
                mostrarNotificacao(resultado.message, 'erro');
            }
        })
        .catch(function(error) {
            console.error('Erro ao fechar caixa:', error);
            mostrarNotificacao('Erro ao fechar caixa', 'erro');
        });
}

// ====================================
// PAINEL E LANCAMENTOS
// ====================================

function carregarPainel() {
    return API.painelCaixa()
        .then(function(painel) {
            if (painel.success) {
                caixaAtual = painel.caixa;
                var totais = painel.totais;
                
                var trocoInicialEl = document.getElementById('trocoInicial');
                var totalEntradasEl = document.getElementById('totalEntradas');
                var totalSaidasEl = document.getElementById('totalSaidas');
                var saldoAtualEl = document.getElementById('saldoAtual');
                
                if (trocoInicialEl) trocoInicialEl.textContent = formatarMoeda(totais.troco_inicial);
                if (totalEntradasEl) totalEntradasEl.textContent = formatarMoeda(totais.total_entradas);
                if (totalSaidasEl) totalSaidasEl.textContent = formatarMoeda(totais.total_saidas);
                if (saldoAtualEl) saldoAtualEl.textContent = formatarMoeda(totais.saldo_atual);
                
                // Atualizar objeto caixaAtual com totais
                caixaAtual.total_entradas = totais.total_entradas;
                caixaAtual.total_saidas = totais.total_saidas;
                caixaAtual.saldo_atual = totais.saldo_atual;
            }
        })
        .catch(function(error) {
            console.error('Erro ao carregar painel:', error);
        });
}

function carregarUltimosLancamentos() {
    if (!caixaAtual) return Promise.resolve();
    
    return API.listarLancamentos({ caixa_id: caixaAtual.id })
        .then(function(resultado) {
            if (resultado.success) {
                var lancamentos = resultado.lancamentos.slice(0, 8); // Ultimos 8
                renderizarLancamentos(lancamentos);
            }
        })
        .catch(function(error) {
            console.error('Erro ao carregar lancamentos:', error);
        });
}

function renderizarLancamentos(lancamentos) {
    var container = document.getElementById('listaLancamentos');
    if (!container) return;
    
    if (lancamentos.length === 0) {
        container.innerHTML = '<p class="text-center" style="color: var(--text-muted);">Nenhum lancamento ainda</p>';
        return;
    }
    
    var html = '';
    for (var i = 0; i < lancamentos.length; i++) {
        var l = lancamentos[i];
        var sinal = (l.tipo === 'entrada') ? '+' : '-';
        var formaPagInfo = l.forma_pagamento ? (getIconeForma(l.forma_pagamento) + ' ' + l.forma_pagamento) : '';
        var descInfo = l.descricao ? (' - ' + l.descricao) : '';
        
        html += '<div class="lancamento-item ' + l.tipo + '">' +
            '<div class="lancamento-info">' +
                '<div class="lancamento-categoria">' + getCategoriaDisplay(l.categoria) + '</div>' +
                '<div class="lancamento-descricao">' + formaPagInfo + descInfo + '</div>' +
            '</div>' +
            '<div class="lancamento-valor ' + l.tipo + '">' +
                sinal + formatarMoeda(l.valor) +
            '</div>' +
        '</div>';
    }
    
    container.innerHTML = html;
}

function getCategoriaDisplay(categoria) {
    var map = {
        'venda': 'VENDA',
        'sangria': 'SANGRIA',
        'suprimento': 'SUPRIMENTO',
        'outros': 'OUTROS'
    };
    return map[categoria] || categoria.toUpperCase();
}
