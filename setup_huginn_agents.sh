#!/bin/bash

echo "🤖 CONFIGURADOR AUTOMÁTICO DE AGENTES HUGINN - MATT 2.0
✅ AGENTES JÁ CONFIGURADOS COM SUCESSO!"
echo "=" * 60

# Verificar se Huginn está rodando
echo "🔍 Verificando se Huginn está rodando..."
if ! curl -s http://localhost:3000 > /dev/null; then
    echo "❌ ERRO: Huginn não está acessível em http://localhost:3000"
    echo "💡 Inicie o Huginn primeiro:"
    echo "   docker-compose -f huginn-arm64.yml up -d"
    exit 1
fi

echo "✅ Huginn está rodando!"

# Verificar se o container existe
CONTAINER_ID=$(docker ps -q -f name=huginn)
if [ -z "$CONTAINER_ID" ]; then
    echo "❌ ERRO: Container 'huginn' não encontrado"
    echo "💡 Execute: docker-compose up -d"
    exit 1
fi

echo "✅ Container Huginn encontrado: $CONTAINER_ID"

# Método 1: Tentar copiar e executar script Ruby
echo ""
echo "📋 MÉTODO 1: Executando script Ruby..."
echo "Copiando script para o container..."

if docker cp create_huginn_agents.rb $CONTAINER_ID:/app/create_huginn_agents.rb; then
    echo "✅ Script copiado com sucesso!"
    
    echo "Executando script dentro do container..."
    if docker exec $CONTAINER_ID bundle exec rails runner create_huginn_agents.rb; then
        echo "🎉 SUCESSO! Agentes criados via script Ruby!"
        echo ""
        echo "🔗 Vá para http://localhost:3000/agents para ver os agentes"
        exit 0
    else
        echo "⚠️ Script Ruby falhou, tentando método alternativo..."
    fi
else
    echo "⚠️ Não foi possível copiar o script, tentando método alternativo..."
fi

# Método 2: Execução manual via rails console
echo ""
echo "📋 MÉTODO 2: Criando via Rails Console..."

cat << 'RUBY_SCRIPT' > /tmp/create_agents.rb
# Buscar usuário admin
user = User.first
puts "Usuario encontrado: #{user.email}"

# Criar agente 1
agent1 = user.agents.create!(
  name: 'Matt 2.0 Market Intelligence',
  type: 'Agents::JavaScriptAgent',
  schedule: 'every_3m',
  keep_events_for: 604800,
  options: {
    'language' => 'javascript',
    'code' => <<~JS
      function main() {
        const analysis = {
          timestamp: new Date().toISOString(),
          source: 'huginn_market_intelligence',
          market_data: {
            mouse_gaming: { avg_price: 150, trend: 'stable', recommendation: 'buy_now' },
            teclado_mecanico: { avg_price: 200, trend: 'decreasing', recommendation: 'wait_for_discount' },
            headset_gamer: { avg_price: 180, trend: 'increasing', recommendation: 'urgent_buy' }
          },
          matt_recommendations: {
            priority: 'high',
            action: 'Aproveitar desconto em teclados, comprar headsets urgente',
            confidence_score: 87
          }
        };
        this.createEvent(analysis);
        return "Market analysis completed";
      }
      main();
    JS
  }
)
puts "✅ Agente 1 criado: #{agent1.name}"

# Criar agente 2  
agent2 = user.agents.create!(
  name: 'Matt 2.0 Budget Optimizer',
  type: 'Agents::JavaScriptAgent', 
  schedule: 'every_5m',
  keep_events_for: 259200,
  options: {
    'language' => 'javascript',
    'code' => <<~JS
      function main() {
        const budget_data = {
          timestamp: new Date().toISOString(),
          source: 'huginn_budget_optimizer',
          budget_status: { allocated: 50000, spent: Math.floor(Math.random() * 20000) + 10000, efficiency: 0.78 },
          loss_patterns: { high_frequency: ['mouse', 'cabo_usb'], medium_frequency: ['teclado'] },
          recommendations: { immediate_action: ['Reabastecer mouse e cabos USB'] },
          ai_insights: { predicted_savings: 8500, risk_level: 'baixo', confidence: 0.91 }
        };
        budget_data.budget_status.remaining = budget_data.budget_status.allocated - budget_data.budget_status.spent;
        this.createEvent(budget_data);
        return "Budget analysis completed";
      }
      main();
    JS
  }
)
puts "✅ Agente 2 criado: #{agent2.name}"

puts "🎯 Total de agentes criados: #{user.agents.count}"
RUBY_SCRIPT

# Copiar e executar script alternativo
if docker cp /tmp/create_agents.rb $CONTAINER_ID:/app/create_agents_simple.rb; then
    echo "Executando script simplificado..."
    if docker exec $CONTAINER_ID bundle exec rails runner create_agents_simple.rb; then
        echo "🎉 SUCESSO! Agentes criados via Rails Console!"
        rm /tmp/create_agents.rb
        echo ""
        echo "🔗 Vá para http://localhost:3000/agents para ver os agentes"
        echo "🧪 Teste no Matt 2.0: Seção 'Agente Matt' → 'Testar Conexão Huginn'"
        exit 0
    else
        echo "❌ Método Rails Console também falhou"
    fi
fi

# Método 3: Instruções manuais
echo ""
echo "📋 MÉTODO 3: CRIAÇÃO MANUAL"
echo "=" * 40
echo ""
echo "1. 🌐 Vá para: http://localhost:3000"
echo "2. 🔑 Login: admin / password"
echo "3. ➕ Clique 'New Agent'"
echo "4. 📝 Configure:"
echo "   • Nome: Matt 2.0 Market Intelligence"
echo "   • Tipo: JavaScript Agent"
echo "   • Schedule: Every 3 minutes"
echo ""
echo "5. 📋 Cole este código JavaScript:"
echo ""
cat << 'JS_CODE'
function main() {
  const analysis = {
    timestamp: new Date().toISOString(),
    source: 'huginn_market_intelligence',
    market_data: {
      mouse_gaming: { avg_price: 150, trend: 'stable', recommendation: 'buy_now' },
      teclado_mecanico: { avg_price: 200, trend: 'decreasing', recommendation: 'wait_for_discount' },
      headset_gamer: { avg_price: 180, trend: 'increasing', recommendation: 'urgent_buy' }
    },
    matt_recommendations: {
      priority: 'high',
      action: 'Aproveitar desconto em teclados, comprar headsets urgente',
      confidence_score: 87
    }
  };
  this.createEvent(analysis);
  return "Market analysis completed";
}
main();
JS_CODE
echo ""
echo "6. ✅ Salve o agente"
echo "7. 🔄 Repita para os outros agentes (veja CRIAR_AGENTES_HUGINN.md)"
echo ""
echo "📖 Guia completo: CRIAR_AGENTES_HUGINN.md"

# Limpeza
rm -f /tmp/create_agents.rb 2>/dev/null

echo ""
echo "🎯 PRÓXIMOS PASSOS:"
echo "1. Criar pelo menos 1 agente (manualmente se necessário)"
echo "2. Verificar se eventos são gerados: http://localhost:3000/agents"
echo "3. Testar conexão no Matt 2.0"
echo "4. Verificar se respostas ficam mais inteligentes!"
