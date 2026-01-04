# 🔔 Guia de Teste de Notificações Push

## Como Testar as Notificações

### 1. **Configurar o Navegador**

Para testar notificações push, você precisa:
- Usar um navegador moderno (Chrome, Firefox, Edge, Safari)
- Permitir notificações quando solicitado
- Estar usando HTTPS (ou localhost em desenvolvimento)

### 2. **Habilitar Notificações na Aplicação**

1. Abra o sistema no navegador: `http://localhost:5000`
2. Quando solicitado, clique em **"Permitir"** para receber notificações
3. O sistema automaticamente registrará seu dispositivo

### 3. **Testar Notificações na Interface**

#### Via Página de Configurações:

1. Acesse: **Configurações** (menu superior)
2. Role até a seção **"🔔 Teste de Notificações Push"**
3. Clique em qualquer botão de teste:
   - **🔔 Teste Geral** - Notificação básica de teste
   - **💸 Teste Sangria** - Simula notificação de sangria de R$ 150,00
   - **🔓 Teste Abertura** - Simula abertura de caixa com R$ 100,00 de troco
   - **🔒 Teste Fechamento** - Simula fechamento com R$ 1.250,50 em vendas
   - **📊 Teste Resumo** - Simula resumo diário completo

4. Observe:
   - A notificação aparecerá no sistema operacional
   - O resultado do teste será exibido na página
   - Quantidade de dispositivos que receberam

### 4. **Testar via API (Opcional)**

Você também pode testar via cURL ou Postman:

```bash
# Teste Geral
curl -X POST http://localhost:5000/api/push/test \
  -H "Content-Type: application/json" \
  -d '{"tipo": "geral"}'

# Teste de Sangria
curl -X POST http://localhost:5000/api/push/test \
  -H "Content-Type: application/json" \
  -d '{"tipo": "sangria"}'

# Teste de Abertura
curl -X POST http://localhost:5000/api/push/test \
  -H "Content-Type: application/json" \
  -d '{"tipo": "abertura"}'

# Teste de Fechamento
curl -X POST http://localhost:5000/api/push/test \
  -H "Content-Type: application/json" \
  -d '{"tipo": "fechamento"}'

# Teste de Resumo Diário
curl -X POST http://localhost:5000/api/push/test \
  -H "Content-Type: application/json" \
  -d '{"tipo": "resumo_diario"}'
```

### 5. **Tipos de Notificações**

#### **Notificação Geral (geral)**
- Mensagem simples de teste
- Útil para verificar se as notificações estão funcionando

#### **Notificação de Sangria (sangria)**
- Título: "💸 Sangria Realizada!"
- Mostra valor e motivo da sangria
- Exemplo: "Valor: R$ 150,00 | Motivo: Teste de notificação de sangria"

#### **Notificação de Abertura (abertura)**
- Título: "🔓 Caixa Aberto!"
- Mostra operador e troco inicial
- Exemplo: "Operador: Operador de Teste | Troco: R$ 100,00"

#### **Notificação de Fechamento (fechamento)**
- Título: "🔒 Caixa Fechado!"
- Mostra total de vendas e diferença (sobra/falta)
- Exemplo: "Total de Vendas: R$ 1.250,50 | ✅ Caixa conferido!"

#### **Notificação de Resumo Diário (resumo_diario)**
- Título: "📊 Resumo do Dia"
- Mostra vendas, sangrias e lucro líquido
- Exemplo: "Vendas: R$ 1.250,50 | Sangrias: R$ 150,00 | Lucro líq.: R$ 350,00"

### 6. **Verificar Subscrições**

Para ver quais dispositivos estão registrados:

```bash
curl http://localhost:5000/api/push/subscriptions
```

### 7. **Configurar Preferências de Notificações**

Cada dispositivo pode escolher quais tipos de notificações deseja receber:

1. Acesse a página de **Configurações**
2. Na seção de notificações (se disponível), marque/desmarque:
   - ☑️ Notificar sangrias
   - ☑️ Notificar abertura de caixa
   - ☑️ Notificar fechamento de caixa
   - ☑️ Notificar resumo diário

### 8. **Comportamento em Produção**

Quando as ações reais ocorrerem no sistema, as notificações serão enviadas automaticamente:

- **Sangria**: Quando registrar uma sangria no caixa
- **Abertura**: Quando abrir um novo caixa
- **Fechamento**: Quando fechar o caixa
- **Resumo**: (Se configurado) Ao final do dia

### 9. **Troubleshooting**

#### Notificações não aparecem:
- Verifique se as permissões do navegador estão corretas
- Confirme que o dispositivo está registrado (via API `/api/push/subscriptions`)
- Teste em modo anônimo para descartar problemas de cache

#### Subscrições expiradas:
- O sistema marca automaticamente subscrições expiradas
- Elas são removidas da lista de envio

#### Teste em múltiplos dispositivos:
- Abra o sistema em vários navegadores/dispositivos
- Cada um receberá uma notificação independente
- O resultado do teste mostra quantos receberam

### 10. **Chaves VAPID (Produção)**

⚠️ **IMPORTANTE**: Em produção, gere suas próprias chaves VAPID:

```bash
# Instalar vapid
npm install -g web-push

# Gerar chaves
web-push generate-vapid-keys

# Configurar no ambiente
export VAPID_PUBLIC_KEY="sua-chave-publica"
export VAPID_PRIVATE_KEY="sua-chave-privada"
export VAPID_EMAIL="mailto:seu-email@dominio.com"
```

---

## ✅ Checklist de Teste

- [ ] Permitir notificações no navegador
- [ ] Testar notificação geral
- [ ] Testar notificação de sangria
- [ ] Testar notificação de abertura
- [ ] Testar notificação de fechamento
- [ ] Testar notificação de resumo diário
- [ ] Verificar notificações em múltiplos dispositivos
- [ ] Configurar preferências de notificações
- [ ] Testar ações reais (abrir caixa, fazer sangria, etc.)
- [ ] Verificar comportamento de subscrições expiradas

---

## 📱 Testando no Celular

1. Certifique-se que o servidor está acessível na rede local
2. Acesse pelo IP: `http://SEU_IP:5000`
3. Instale como PWA (Adicionar à tela inicial)
4. Permita notificações quando solicitado
5. Teste os botões na página de configurações

**Nota**: Para receber notificações quando o app não está aberto, instale como PWA.

---

## 🔧 Dicas Avançadas

### Personalizar Notificações

Edite o arquivo `app/push_notifications.py` para personalizar:
- Ícones das notificações
- Sons de alerta
- Vibração
- Ações interativas

### Agendar Notificações

Use um scheduler (como APScheduler) para enviar notificações automáticas:
- Resumo diário às 18h
- Lembretes de fechamento de caixa
- Alertas de metas não atingidas

### Logs de Notificações

Monitore o console do servidor para ver:
- Notificações enviadas
- Subscrições expiradas
- Erros de envio

---

**Sistema testado e funcionando! 🎉**
