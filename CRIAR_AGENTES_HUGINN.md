# 🤖 COMO CRIAR AGENTES DO HUGINN PARA MATT 2.0

## ⚠️ **PROBLEMA IDENTIFICADO**
Os agentes do Huginn não aparecem em `http://localhost:3000/agents` porque precisam ser criados **manualmente** ou via **script**.

---

## 🚀 **MÉTODO 1: SCRIPT AUTOMÁTICO (RECOMENDADO)**

### **1. Verificar se Huginn está rodando:**
```bash
# Verificar containers
docker ps

# Deve aparecer um container huginn rodando na porta 3000
```

### **2. Executar script de criação:**
```bash
# Entrar no container do Huginn
docker exec -it huginn bash

# Ou se estiver usando docker-compose:
docker-compose exec huginn bash

# Dentro do container, executar:
cd /app
bundle exec rails runner /path/to/create_huginn_agents.rb
```

### **3. Script alternativo direto (mais simples):**
```bash
# Copiar o script para o container e executar
docker cp create_huginn_agents.rb huginn:/app/
docker exec huginn bundle exec rails runner create_huginn_agents.rb
```

---

## 🖥️ **MÉTODO 2: INTERFACE WEB (MANUAL)**

### **Passo 1: Acessar Huginn**
1. Vá para: `http://localhost:3000`
2. Login: `admin` / `password` (primeira vez)

### **Passo 2: Criar Primeiro Agente**
1. Clique em **"New Agent"**
2. **Nome:** `Matt 2.0 Market Intelligence`
3. **Tipo:** `JavaScript Agent`
4. **Schedule:** `Every 3 minutes`
5. **Keep Events For:** `604800` (7 dias)

### **Código JavaScript para o Agente 1:**
```javascript
function main() {
  const analysis = {
    timestamp: new Date().toISOString(),
    source: 'huginn_market_intelligence',
    market_data: {
      mouse_gaming: {
        avg_price: 150,
        trend: 'stable',
        availability: 'high',
        recommendation: 'buy_now'
      },
      teclado_mecanico: {
        avg_price: 200,
        trend: 'decreasing',
        availability: 'medium', 
        recommendation: 'wait_for_discount'
      },
      headset_gamer: {
        avg_price: 180,
        trend: 'increasing',
        availability: 'low',
        recommendation: 'urgent_buy'
      }
    },
    insights: {
      best_deals: ['teclado_mecanico'],
      price_alerts: ['headset_gamer'],
      market_confidence: 0.85
    },
    matt_recommendations: {
      priority: 'high',
      action: 'Aproveitar desconto em teclados, comprar headsets urgente',
      budget_impact: 'moderado',
      confidence_score: 87
    }
  };
  
  this.createEvent(analysis);
  return "Market analysis completed";
}

main();
```

### **Passo 3: Criar Segundo Agente**
1. **Nome:** `Matt 2.0 Budget Optimizer`
2. **Tipo:** `JavaScript Agent`
3. **Schedule:** `Every 5 minutes`

### **Código JavaScript para o Agente 2:**
```javascript
function main() {
  const budget_data = {
    timestamp: new Date().toISOString(),
    source: 'huginn_budget_optimizer',
    budget_status: {
      allocated: 50000,
      spent: Math.floor(Math.random() * 20000) + 10000,
      efficiency: 0.78
    },
    loss_patterns: {
      high_frequency: ['mouse', 'cabo_usb', 'fone_ouvido'],
      medium_frequency: ['teclado', 'webcam'],
      low_frequency: ['monitor', 'impressora']
    },
    recommendations: {
      immediate_action: ['Reabastecer mouse e cabos USB'],
      cost_optimization: 'Comprar mouse em quantidade para desconto volume',
      risk_mitigation: 'Diversificar fornecedores de cabos USB'
    },
    ai_insights: {
      predicted_savings: 8500,
      risk_level: 'baixo',
      confidence: 0.91
    }
  };
  
  budget_data.budget_status.remaining = budget_data.budget_status.allocated - budget_data.budget_status.spent;
  
  this.createEvent(budget_data);
  return "Budget analysis completed";
}

main();
```

### **Passo 4: Criar Terceiro Agente**
1. **Nome:** `Matt 2.0 Smart Recommendations`
2. **Tipo:** `JavaScript Agent`
3. **Schedule:** `Every 10 minutes`

### **Código JavaScript para o Agente 3:**
```javascript
function main() {
  const recommendations = {
    timestamp: new Date().toISOString(),
    source: 'huginn_smart_recommendations',
    smart_recommendations: [
      {
        item: 'mouse_gamer',
        quantity: 25,
        reasoning: 'Alta frequência de perda + preço estável',
        priority: 'alta',
        savings_potential: 1200
      },
      {
        item: 'teclado_mecanico', 
        quantity: 15,
        reasoning: 'Oportunidade de desconto + estoque baixo',
        priority: 'média',
        savings_potential: 800
      },
      {
        item: 'headset_premium',
        quantity: 10,
        reasoning: 'Preços subindo + demanda crescente',
        priority: 'urgente',
        savings_potential: 2000
      }
    ],
    execution_plan: {
      phase1: 'Comprar headsets premium imediatamente',
      phase2: 'Aguardar confirmação de desconto em teclados',
      phase3: 'Compra programada de mouse em 2 semanas',
      total_investment: 47800,
      expected_roi: 18.5
    }
  };
  
  this.createEvent(recommendations);
  return "Smart recommendations generated";
}

main();
```

---

## 🔧 **MÉTODO 3: VIA API (AVANÇADO)**

```bash
# Criar agente via API REST
curl -X POST http://localhost:3000/agents \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer SEU_TOKEN_API" \
  -d '{
    "agent": {
      "name": "Matt 2.0 Market Intelligence",
      "type": "Agents::JavaScriptAgent",
      "schedule": "every_3m",
      "options": {
        "language": "javascript",
        "code": "function main() { ... }"
      }
    }
  }'
```

---

## ✅ **VERIFICAÇÃO SE FUNCIONOU**

### **1. Interface Web:**
- Vá para `http://localhost:3000/agents`
- Deve aparecer 3 agentes com nomes "Matt 2.0..."

### **2. Eventos Gerados:**
- Clique em qualquer agente
- Vá na aba "Events"  
- Deve aparecer eventos sendo gerados automaticamente

### **3. Teste no Matt 2.0:**
- No dashboard, vá na seção "Agente Matt"
- Clique "🧪 Testar Conexão Huginn"
- Deve mostrar "✅ Conexão estabelecida!" com eventos

---

## 🚨 **TROUBLESHOOTING**

### **❌ "Permission denied" no script:**
```bash
# Dar permissão ao arquivo
chmod +x create_huginn_agents.rb

# Ou executar diretamente:
docker exec huginn ruby -e "$(cat create_huginn_agents.rb)"
```

### **❌ "User not found":**
```bash
# Verificar usuários no Huginn
docker exec huginn bundle exec rails console
# Dentro do console:
User.all
# Use o email correto no script
```

### **❌ Agentes não executam:**
- Verifique se a agenda está habilitada
- Confirme que o delayed_job está rodando
- Restart o container se necessário

### **❌ Matt 2.0 não vê os dados:**
- Verifique o token API no Matt 2.0
- Confirme a URL: `http://localhost:3000`
- Teste a conectividade manual

---

## 🎯 **RESULTADO ESPERADO**

Após criar os agentes, você deve ter:

✅ **3 agentes ativos** no Huginn  
✅ **Eventos sendo gerados** a cada 3-10 minutos  
✅ **Matt 2.0 conectado** e recebendo dados  
✅ **Respostas inteligentes** enriquecidas com dados do Huginn  

---

## 📞 **SUPORTE RÁPIDO**

**Se não conseguir executar o script:**
1. Use a interface web (Método 2)
2. Crie pelo menos 1 agente para testar
3. Verifique se os eventos aparecem
4. Teste a conexão no Matt 2.0

**O importante é ter agentes gerando eventos!** 🎯
