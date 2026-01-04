# 🧪 Exemplos de Uso da API

Exemplos práticos de como usar a API do PDV-MF.

## 🔧 Ferramentas para Testar

### cURL (Terminal)
```bash
curl http://localhost:5000/api/caixa/status
```

### HTTPie (Terminal, mais amigável)
```bash
http GET localhost:5000/api/caixa/status
```

### Postman / Insomnia
Interface gráfica para testar APIs

### JavaScript (Frontend)
```javascript
fetch('/api/caixa/status')
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## 📋 Exemplos

### 1. Verificar Status do Caixa

**Request:**
```bash
GET /api/caixa/status
```

**Response (Caixa Fechado):**
```json
{
  "aberto": false
}
```

**Response (Caixa Aberto):**
```json
{
  "aberto": true,
  "caixa": {
    "id": 1,
    "data_abertura": "2026-01-04T08:00:00",
    "data_fechamento": null,
    "operador": "João Silva",
    "troco_inicial": 100.00,
    "valor_contado": null,
    "diferenca": null,
    "observacao": null,
    "status": "aberto",
    "total_entradas": 450.00,
    "total_saidas": 50.00,
    "saldo_atual": 500.00
  }
}
```

### 2. Abrir Caixa

**Request:**
```bash
POST /api/caixa/abrir
Content-Type: application/json

{
  "operador": "João Silva",
  "troco_inicial": 100.00
}
```

**cURL:**
```bash
curl -X POST http://localhost:5000/api/caixa/abrir \
  -H "Content-Type: application/json" \
  -d '{"operador":"João Silva","troco_inicial":100.00}'
```

**Response:**
```json
{
  "success": true,
  "message": "Caixa aberto com sucesso",
  "caixa": {
    "id": 1,
    "data_abertura": "2026-01-04T08:00:00",
    "operador": "João Silva",
    "troco_inicial": 100.00,
    "status": "aberto",
    "saldo_atual": 100.00
  }
}
```

### 3. Registrar Venda em Dinheiro (com troco)

**Request:**
```bash
POST /api/lancamento
Content-Type: application/json

{
  "tipo": "entrada",
  "categoria": "venda",
  "forma_pagamento": "Dinheiro",
  "valor": 45.00,
  "valor_recebido": 50.00,
  "descricao": "Venda de produtos"
}
```

**cURL:**
```bash
curl -X POST http://localhost:5000/api/lancamento \
  -H "Content-Type: application/json" \
  -d '{
    "tipo":"entrada",
    "categoria":"venda",
    "forma_pagamento":"Dinheiro",
    "valor":45.00,
    "valor_recebido":50.00,
    "descricao":"Venda de produtos"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Lançamento criado com sucesso",
  "lancamento": {
    "id": 1,
    "caixa_id": 1,
    "data_hora": "2026-01-04T10:30:00",
    "tipo": "entrada",
    "categoria": "venda",
    "forma_pagamento": "Dinheiro",
    "valor": 45.00,
    "valor_recebido": 50.00,
    "troco": 5.00,
    "descricao": "Venda de produtos"
  }
}
```

### 4. Registrar Venda em PIX

**Request:**
```bash
POST /api/lancamento
Content-Type: application/json

{
  "tipo": "entrada",
  "categoria": "venda",
  "forma_pagamento": "PIX",
  "valor": 75.50,
  "descricao": "Venda via PIX"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Lançamento criado com sucesso",
  "lancamento": {
    "id": 2,
    "tipo": "entrada",
    "categoria": "venda",
    "forma_pagamento": "PIX",
    "valor": 75.50
  }
}
```

### 5. Registrar Sangria

**Request:**
```bash
POST /api/lancamento
Content-Type: application/json

{
  "tipo": "saida",
  "categoria": "sangria",
  "valor": 200.00,
  "descricao": "Retirada para banco"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Lançamento criado com sucesso"
}
```

### 6. Registrar Suprimento

**Request:**
```bash
POST /api/lancamento
Content-Type: application/json

{
  "tipo": "entrada",
  "categoria": "suprimento",
  "valor": 150.00,
  "descricao": "Dinheiro do banco"
}
```

### 7. Obter Painel do Caixa

**Request:**
```bash
GET /api/caixa/painel
```

**Response:**
```json
{
  "success": true,
  "caixa": {
    "id": 1,
    "operador": "João Silva",
    "status": "aberto",
    "saldo_atual": 575.50
  },
  "totais": {
    "troco_inicial": 100.00,
    "total_entradas": 670.50,
    "total_saidas": 200.00,
    "saldo_atual": 570.50
  },
  "resumo_pagamentos": {
    "Dinheiro": 345.00,
    "PIX": 225.50,
    "Cartão Débito": 100.00
  },
  "resumo_categorias": {
    "venda": 670.50,
    "sangria": 200.00
  }
}
```

### 8. Fechar Caixa (sem conferência)

**Request:**
```bash
POST /api/caixa/fechar
Content-Type: application/json

{
  "observacao": "Fechamento normal"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Caixa fechado com sucesso",
  "caixa": {
    "id": 1,
    "data_fechamento": "2026-01-04T18:00:00",
    "status": "fechado",
    "saldo_atual": 570.50
  }
}
```

### 9. Fechar Caixa (com conferência)

**Request:**
```bash
POST /api/caixa/fechar
Content-Type: application/json

{
  "valor_contado": 575.00,
  "observacao": "Pequena sobra de R$ 4,50"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Caixa fechado com sucesso",
  "caixa": {
    "id": 1,
    "data_fechamento": "2026-01-04T18:00:00",
    "status": "fechado",
    "saldo_atual": 570.50,
    "valor_contado": 575.00,
    "diferenca": 4.50
  }
}
```

### 10. Listar Lançamentos (com filtros)

**Request:**
```bash
GET /api/lancamentos?data_inicio=2026-01-04T00:00:00&data_fim=2026-01-04T23:59:59&tipo=entrada
```

**cURL:**
```bash
curl "http://localhost:5000/api/lancamentos?data_inicio=2026-01-04T00:00:00&data_fim=2026-01-04T23:59:59&tipo=entrada"
```

**Response:**
```json
{
  "success": true,
  "lancamentos": [
    {
      "id": 1,
      "data_hora": "2026-01-04T10:30:00",
      "tipo": "entrada",
      "categoria": "venda",
      "forma_pagamento": "Dinheiro",
      "valor": 45.00,
      "troco": 5.00
    },
    {
      "id": 2,
      "data_hora": "2026-01-04T11:15:00",
      "tipo": "entrada",
      "categoria": "venda",
      "forma_pagamento": "PIX",
      "valor": 75.50
    }
  ]
}
```

### 11. Listar Caixas

**Request:**
```bash
GET /api/caixas?status=fechado
```

**Response:**
```json
{
  "success": true,
  "caixas": [
    {
      "id": 1,
      "data_abertura": "2026-01-04T08:00:00",
      "data_fechamento": "2026-01-04T18:00:00",
      "operador": "João Silva",
      "status": "fechado",
      "troco_inicial": 100.00,
      "saldo_atual": 570.50,
      "diferenca": 4.50
    }
  ]
}
```

### 12. Detalhes de um Caixa

**Request:**
```bash
GET /api/caixa/1
```

**Response:**
```json
{
  "success": true,
  "caixa": {
    "id": 1,
    "data_abertura": "2026-01-04T08:00:00",
    "data_fechamento": "2026-01-04T18:00:00",
    "operador": "João Silva",
    "status": "fechado",
    "troco_inicial": 100.00,
    "total_entradas": 670.50,
    "total_saidas": 200.00,
    "saldo_atual": 570.50
  },
  "lancamentos": [
    {
      "id": 1,
      "tipo": "entrada",
      "categoria": "venda",
      "valor": 45.00
    },
    {
      "id": 2,
      "tipo": "saida",
      "categoria": "sangria",
      "valor": 200.00
    }
  ]
}
```

### 13. Relatório Resumido

**Request:**
```bash
GET /api/relatorio/resumo?data_inicio=2026-01-01&data_fim=2026-01-31
```

**Response:**
```json
{
  "success": true,
  "periodo": {
    "inicio": "2026-01-01",
    "fim": "2026-01-31"
  },
  "totais": {
    "entradas": 5420.50,
    "saidas": 1200.00,
    "saldo": 4220.50
  },
  "categorias": [
    {
      "categoria": "venda",
      "tipo": "entrada",
      "total": 5420.50
    },
    {
      "categoria": "sangria",
      "tipo": "saida",
      "total": 800.00
    },
    {
      "categoria": "despesa",
      "tipo": "saida",
      "total": 400.00
    }
  ],
  "pagamentos": [
    {
      "forma": "Dinheiro",
      "total": 2150.00
    },
    {
      "forma": "PIX",
      "total": 1870.50
    },
    {
      "forma": "Cartão Débito",
      "total": 800.00
    },
    {
      "forma": "Cartão Crédito",
      "total": 600.00
    }
  ]
}
```

### 14. Obter Configurações

**Request:**
```bash
GET /api/configuracao
```

**Response:**
```json
{
  "nome_loja": "Minha Loja",
  "responsavel": "João Silva",
  "formas_pagamento": [
    "Dinheiro",
    "PIX",
    "Cartão Débito",
    "Cartão Crédito"
  ]
}
```

### 15. Atualizar Configurações

**Request:**
```bash
PUT /api/configuracao
Content-Type: application/json

{
  "nome_loja": "Loja Exemplo LTDA",
  "responsavel": "Maria Santos",
  "formas_pagamento": [
    "Dinheiro",
    "PIX",
    "Cartão Débito",
    "Cartão Crédito",
    "Boleto"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Configurações atualizadas"
}
```

### 16. Deletar Lançamento

**Request:**
```bash
DELETE /api/lancamento/5
```

**cURL:**
```bash
curl -X DELETE http://localhost:5000/api/lancamento/5
```

**Response:**
```json
{
  "success": true,
  "message": "Lançamento deletado com sucesso"
}
```

**Erro (caixa fechado):**
```json
{
  "success": false,
  "message": "Não é possível deletar lançamento de caixa fechado"
}
```

---

## 🔴 Tratamento de Erros

### Erro: Caixa já aberto
```json
{
  "success": false,
  "message": "Já existe um caixa aberto"
}
```

### Erro: Não há caixa aberto
```json
{
  "success": false,
  "message": "Não há caixa aberto"
}
```

### Erro: Dados incompletos
```json
{
  "success": false,
  "message": "Dados incompletos"
}
```

### Erro: Não encontrado (404)
```json
{
  "success": false,
  "message": "Caixa não encontrado"
}
```

---

## 🧪 Script de Teste Completo

Salve como `test_api.sh`:

```bash
#!/bin/bash

API="http://localhost:5000/api"

echo "1. Verificar status..."
curl -s "$API/caixa/status" | json_pp

echo -e "\n2. Abrir caixa..."
curl -s -X POST "$API/caixa/abrir" \
  -H "Content-Type: application/json" \
  -d '{"operador":"Teste","troco_inicial":100}' | json_pp

echo -e "\n3. Venda em dinheiro..."
curl -s -X POST "$API/lancamento" \
  -H "Content-Type: application/json" \
  -d '{"tipo":"entrada","categoria":"venda","forma_pagamento":"Dinheiro","valor":45,"valor_recebido":50}' | json_pp

echo -e "\n4. Venda PIX..."
curl -s -X POST "$API/lancamento" \
  -H "Content-Type: application/json" \
  -d '{"tipo":"entrada","categoria":"venda","forma_pagamento":"PIX","valor":75.50}' | json_pp

echo -e "\n5. Sangria..."
curl -s -X POST "$API/lancamento" \
  -H "Content-Type: application/json" \
  -d '{"tipo":"saida","categoria":"sangria","valor":50}' | json_pp

echo -e "\n6. Ver painel..."
curl -s "$API/caixa/painel" | json_pp

echo -e "\n7. Fechar caixa..."
curl -s -X POST "$API/caixa/fechar" \
  -H "Content-Type: application/json" \
  -d '{"valor_contado":170.50}' | json_pp

echo -e "\nTeste concluído!"
```

Execute:
```bash
chmod +x test_api.sh
./test_api.sh
```

---

## 📦 Coleção Postman/Insomnia

Importe este JSON no Postman ou Insomnia:

```json
{
  "name": "PDV-MF API",
  "requests": [
    {
      "name": "Status do Caixa",
      "method": "GET",
      "url": "{{base_url}}/api/caixa/status"
    },
    {
      "name": "Abrir Caixa",
      "method": "POST",
      "url": "{{base_url}}/api/caixa/abrir",
      "body": {
        "operador": "João",
        "troco_inicial": 100
      }
    },
    {
      "name": "Venda Dinheiro",
      "method": "POST",
      "url": "{{base_url}}/api/lancamento",
      "body": {
        "tipo": "entrada",
        "categoria": "venda",
        "forma_pagamento": "Dinheiro",
        "valor": 45,
        "valor_recebido": 50
      }
    }
  ],
  "environment": {
    "base_url": "http://localhost:5000"
  }
}
```

---

## 🎯 Dicas

1. **Use JSON formatter** para visualizar responses
2. **Teste em ordem** (abrir caixa antes de lançar)
3. **Verifique erros** antes de continuar
4. **Use variáveis** para IDs dinâmicos
5. **Salve exemplos** que funcionam

---

**Agora você pode testar toda a API do PDV-MF! 🚀**
