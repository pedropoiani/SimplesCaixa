# Sistema PDV-MF

Sistema completo de Ponto de Venda com Controle de Caixa desenvolvido em Python.

## 📋 Características

- ✅ **Interface gráfica** com Tkinter (nativa do Python)
- ✅ **Banco de dados local** SQLite (arquivo único, totalmente offline)
- ✅ **Controle completo de caixa** (abertura, lançamentos e fechamento)
- ✅ **Cálculo automático de troco** para vendas em dinheiro
- ✅ **Múltiplas formas de pagamento** (Dinheiro, PIX, Cartão)
- ✅ **Histórico completo** com filtros e relatórios
- ✅ **Exportação para CSV** (compatível com LibreOffice)
- ✅ **Backup e restauração** de dados
- ✅ **Painel em tempo real** com resumo financeiro
- ✅ **Sistema de logs** para auditoria

## 🚀 Instalação e Execução

### Requisitos

- Python 3.6 ou superior (já vem instalado no Linux Mint)
- Tkinter (geralmente já está instalado com Python)

### Instalação

```bash
# Navegue até a pasta do projeto
cd ~/Downloads/pdvMF

# Torne o script executável (opcional)
chmod +x main.py
chmod +x pdv.sh
```

### Executar o Sistema

**Opção 1: Via script shell**
```bash
./pdv.sh
```

**Opção 2: Via Python diretamente**
```bash
python3 main.py
```

**Opção 3: Clique duplo**
- Abra o gerenciador de arquivos
- Navegue até a pasta do projeto
- Dê clique duplo no arquivo `pdv.sh`
- Se perguntar, escolha "Executar"

## 📖 Como Usar

### 1. Primeira Execução

Na primeira vez que executar:
1. Configure o nome da loja e responsável
2. Configure as formas de pagamento que deseja usar
3. Salve as configurações

### 2. Abertura de Caixa

1. Clique em "Abrir Caixa"
2. Informe o operador (opcional)
3. Informe o troco inicial (dinheiro no caixa)
4. Confirme a abertura

### 3. Lançamentos

**Venda em Dinheiro:**
- Informe o valor da compra
- Informe o valor recebido
- O sistema calcula o troco automaticamente

**Outras Vendas (PIX/Cartão):**
- Selecione a forma de pagamento
- Informe o valor
- Adicione observações se necessário

**Sangria:**
- Use quando retirar dinheiro do caixa
- Informe o valor retirado

**Suprimento:**
- Use quando adicionar dinheiro ao caixa
- Informe o valor adicionado

**Outros Lançamentos:**
- Para despesas ou outros tipos de movimento
- Escolha o tipo (Entrada/Saída)
- Escolha a categoria
- Informe o valor

### 4. Painel do Caixa

O painel mostra em tempo real:
- **Saldo Atual**: Total disponível no caixa
- **Troco Inicial**: Valor inicial do caixa
- **Entradas**: Total de vendas e suprimentos
- **Saídas**: Total de sangrias e despesas

Clique em "🔄 Atualizar" para atualizar os valores.

### 5. Fechamento de Caixa

1. Clique em "🔒 Fechar Caixa"
2. Confira o resumo do dia
3. **(Opcional)** Conte o dinheiro e informe o valor contado
4. O sistema calcula automaticamente se há sobra ou falta
5. Adicione observações se necessário
6. Confirme o fechamento
7. Salve o relatório se desejar

### 6. Histórico e Relatórios

**Consultar Lançamentos:**
- Filtre por período (hoje, 7 dias, 30 dias ou personalizado)
- Filtre por tipo (Entrada/Saída)
- Filtre por categoria
- Exporte para CSV

**Consultar Caixas:**
- Veja todos os caixas (abertos e fechados)
- Clique duas vezes para ver detalhes completos
- Exporte para CSV

### 7. Backup

1. Acesse "Histórico"
2. Clique em "💾 Fazer Backup"
3. O backup será salvo automaticamente

**Para Restaurar:**
```bash
# Os backups ficam salvos em:
~/.pdvmf/backups/
```

## 📁 Estrutura de Arquivos

```
pdvMF/
├── main.py                  # Aplicação principal
├── database.py              # Gerenciamento do banco de dados
├── utils.py                 # Funções utilitárias
├── view_configuracao.py     # Tela de configurações
├── view_caixa.py           # Telas de abertura/fechamento
├── view_principal.py        # Tela principal de lançamentos
├── view_historico.py        # Tela de histórico e relatórios
├── pdv.sh                  # Script de execução
└── README.md               # Este arquivo
```

## 🗂️ Localização dos Dados

- **Banco de dados**: `~/.pdvmf/pdvmf.db`
- **Backups**: `~/.pdvmf/backups/`
- **Exportações CSV**: `~/Downloads/` (padrão)

## 🎨 Funcionalidades Detalhadas

### Tipos de Lançamento

| Tipo | Categoria | Descrição |
|------|-----------|-----------|
| Entrada | Venda | Vendas realizadas |
| Entrada | Suprimento | Dinheiro adicionado ao caixa |
| Saída | Sangria | Dinheiro retirado do caixa |
| Saída | Despesa | Pagamentos e despesas |
| Entrada/Saída | Outros | Outros movimentos |

### Formas de Pagamento

- **Dinheiro**: Para vendas com troco
- **PIX**: Pagamentos via PIX
- **Cartão Débito**: Pagamentos no débito
- **Cartão Crédito**: Pagamentos no crédito
- **Outras**: Você pode adicionar mais formas

### Relatórios

- Resumo de fechamento com totais
- Detalhamento por forma de pagamento
- Detalhamento por categoria
- Lista completa de lançamentos
- Diferenças (sobra/falta) no fechamento

## 🔒 Segurança

- Todos os dados são armazenados localmente
- Não há conexão com internet
- Sistema de logs para auditoria
- Backup manual para segurança dos dados

## ⚙️ Configurações

Acesse as configurações a qualquer momento clicando no botão "⚙️ Config" na tela principal.

Você pode:
- Alterar nome da loja e responsável
- Adicionar novas formas de pagamento
- Ativar/desativar formas de pagamento

## 🐛 Resolução de Problemas

**Erro: "tkinter não encontrado"**
```bash
sudo apt-get install python3-tk
```

**Erro: "permission denied" ao executar**
```bash
chmod +x main.py
chmod +x pdv.sh
```

**Banco de dados corrompido**
- Restaure um backup da pasta `~/.pdvmf/backups/`
- Copie o arquivo de backup para `~/.pdvmf/pdvmf.db`

## 📝 Dicas de Uso

1. **Faça backups regulares** - especialmente antes de fechamentos importantes
2. **Confira o valor contado** no fechamento para detectar diferenças
3. **Use sangrias** regularmente para evitar muito dinheiro no caixa
4. **Adicione observações** nos lançamentos para facilitar a auditoria
5. **Exporte relatórios** mensalmente para análise no LibreOffice

## 📞 Suporte

Para problemas ou dúvidas:
1. Consulte este README
2. Verifique os logs do sistema
3. Restaure um backup se necessário

## 📄 Licença

Este software é fornecido "como está", sem garantias de qualquer tipo.

---

**PDV-MF** - Sistema de Controle de Caixa Simples e Eficiente
