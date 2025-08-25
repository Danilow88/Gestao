#!/usr/bin/env ruby

puts '🎯 CRIANDO AGENTES MATT 2.0 - MÉTODO QUE FUNCIONA'
puts '=' * 50

user = User.first
puts "👤 Usuário: #{user.email}"

# Remover agente de teste se existe
test_agent = user.agents.find_by(name: 'Matt 2.0 Test Agent')
if test_agent
  puts "🗑️ Removendo agente de teste..."
  test_agent.destroy
end

# Configuração dos agentes
agents_to_create = [
  {
    name: 'Matt 2.0 Market Intelligence',
    schedule: 'every_2_minutes',
    description: 'Análise de mercado de gadgets',
    code: <<~JS
      function main() {
        const analysis = {
          timestamp: new Date().toISOString(),
          source: 'huginn_market_intelligence',
          market_data: {
            mouse_gaming: { 
              avg_price: 150 + Math.floor(Math.random() * 50), 
              trend: ['stable', 'increasing', 'decreasing'][Math.floor(Math.random() * 3)],
              recommendation: 'buy_now' 
            },
            teclado_mecanico: { 
              avg_price: 200 + Math.floor(Math.random() * 80), 
              trend: 'decreasing', 
              recommendation: 'wait_for_discount' 
            },
            headset_gamer: { 
              avg_price: 180 + Math.floor(Math.random() * 60), 
              trend: 'increasing', 
              recommendation: 'urgent_buy' 
            }
          },
          insights: {
            market_confidence: 0.8 + Math.random() * 0.2,
            best_deals: ['teclado_mecanico'],
            price_alerts: ['headset_gamer']
          },
          matt_recommendations: {
            priority: 'high',
            action: 'Aproveitar desconto em teclados, comprar headsets urgente',
            confidence_score: 85 + Math.floor(Math.random() * 10)
          }
        };
        this.createEvent(analysis);
        return "Market analysis completed at " + new Date().toISOString();
      }
      main();
    JS
  },
  {
    name: 'Matt 2.0 Budget Optimizer',
    schedule: 'every_5_minutes',
    description: 'Otimização de orçamento e perdas',
    code: <<~JS
      function main() {
        const spent = Math.floor(Math.random() * 20000) + 10000;
        const budget_data = {
          timestamp: new Date().toISOString(),
          source: 'huginn_budget_optimizer',
          budget_status: { 
            allocated: 50000, 
            spent: spent,
            remaining: 50000 - spent,
            efficiency: 0.75 + Math.random() * 0.2
          },
          loss_patterns: { 
            high_frequency: ['mouse', 'cabo_usb', 'fone_ouvido'],
            medium_frequency: ['teclado', 'webcam'],
            low_frequency: ['monitor', 'impressora']
          },
          recommendations: { 
            immediate_action: ['Reabastecer mouse e cabos USB'],
            cost_optimization: 'Comprar em quantidade para desconto',
            predicted_savings: Math.floor(Math.random() * 5000) + 3000
          },
          ai_insights: {
            risk_level: ['baixo', 'médio'][Math.floor(Math.random() * 2)],
            confidence: 0.85 + Math.random() * 0.1
          }
        };
        this.createEvent(budget_data);
        return "Budget analysis completed at " + new Date().toISOString();
      }
      main();
    JS
  },
  {
    name: 'Matt 2.0 Smart Recommendations',
    schedule: 'every_10_minutes',
    description: 'Recomendações inteligentes de compra',
    code: <<~JS
      function main() {
        const recommendations = {
          timestamp: new Date().toISOString(),
          source: 'huginn_smart_recommendations',
          algorithm_version: '2.1.0',
          smart_recommendations: [
            { 
              item: 'mouse_gamer', 
              quantity: 20 + Math.floor(Math.random() * 10), 
              priority: 'alta', 
              savings_potential: 1000 + Math.floor(Math.random() * 500),
              reasoning: 'Alta frequência de perda + preço favorável'
            },
            { 
              item: 'teclado_mecanico', 
              quantity: 10 + Math.floor(Math.random() * 10), 
              priority: 'média', 
              savings_potential: 700 + Math.floor(Math.random() * 300),
              reasoning: 'Oportunidade de desconto detectada'
            },
            { 
              item: 'headset_premium', 
              quantity: 5 + Math.floor(Math.random() * 10), 
              priority: 'urgente', 
              savings_potential: 1500 + Math.floor(Math.random() * 800),
              reasoning: 'Preços subindo + demanda crescente'
            }
          ],
          execution_plan: {
            total_investment: 40000 + Math.floor(Math.random() * 15000),
            expected_roi: 15 + Math.random() * 10,
            confidence_level: 0.9 + Math.random() * 0.08
          }
        };
        this.createEvent(recommendations);
        return "Smart recommendations generated at " + new Date().toISOString();
      }
      main();
    JS
  }
]

# Criar cada agente
success_count = 0
agents_to_create.each_with_index do |config, index|
  puts "\n#{index + 1}. 📊 Criando: #{config[:name]}..."
  
  agent = user.agents.build(
    name: config[:name],
    type: 'Agents::JavaScriptAgent',
    schedule: config[:schedule],
    keep_events_for: 604800, # 7 dias
    options: {
      'language' => 'javascript',
      'code' => config[:code]
    }
  )
  
  if agent.save
    puts "   ✅ Sucesso! ID: #{agent.id}"
    puts "   📅 Schedule: #{agent.schedule}"
    puts "   📝 Descrição: #{config[:description]}"
    success_count += 1
    
    # Tentar execução manual (método correto)
    begin
      # Forçar uma primeira execução
      agent.check
      puts "   🚀 Primeira execução realizada!"
    rescue => e
      puts "   ⚠️ Primeira execução: #{e.message}"
    end
    
  else
    puts "   ❌ Erro: #{agent.errors.full_messages.join(', ')}"
  end
end

# Resultado final
puts "\n" + "=" * 50
puts "🎯 RESULTADO FINAL:"
puts "✅ #{success_count}/#{agents_to_create.length} agentes criados com sucesso"

matt_agents = user.agents.where("name LIKE 'Matt 2.0%'").order(:id)
if matt_agents.any?
  puts "\n📊 AGENTES MATT 2.0 ATIVOS:"
  matt_agents.each do |agent|
    puts "• #{agent.name}"
    puts "  ID: #{agent.id} | Schedule: #{agent.schedule}"
    puts "  Eventos: #{agent.events.count} | Status: #{agent.disabled? ? 'Inativo' : 'Ativo'}"
    puts ""
  end
end

puts "🚀 CONFIGURAÇÃO COMPLETA!"
puts "🌐 Acesse: http://localhost:3000/agents"
puts "🧪 Teste Matt 2.0: Dashboard → Agente Matt → 'Testar Conexão Huginn'"

puts "\n💡 PRÓXIMOS PASSOS:"
puts "1. Vá para http://localhost:3000/agents"
puts "2. Veja se os 3 agentes Matt 2.0 estão listados"
puts "3. Clique em cada agente e vá na aba 'Events'"
puts "4. Deve haver pelo menos 1 evento em cada agente"
puts "5. Teste a conexão no Matt 2.0"
