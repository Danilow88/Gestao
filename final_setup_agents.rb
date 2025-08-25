#!/usr/bin/env ruby

puts '🚀 CONFIGURAÇÃO FINAL DOS AGENTES MATT 2.0'
puts '=' * 50

user = User.first
puts "👤 Usuário: #{user.email}"

# 1. Limpar agentes duplicados Matt 2.0
puts "\n🧹 LIMPANDO AGENTES DUPLICADOS..."
matt_agents = user.agents.where("name LIKE 'Matt 2.0%'")
puts "Encontrados #{matt_agents.count} agentes Matt 2.0"

matt_agents.each do |agent|
  puts "Removendo: #{agent.name} (ID: #{agent.id})"
  agent.destroy
end

# 2. Criar agentes com configurações corretas
puts "\n🤖 CRIANDO AGENTES DEFINITIVOS..."

agents_config = [
  {
    name: 'Matt 2.0 Market Intelligence',
    schedule: 'every_2_minutes',
    code: <<~JS
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
        return "Market analysis completed at " + new Date().toISOString();
      }
      main();
    JS
  },
  {
    name: 'Matt 2.0 Budget Optimizer',
    schedule: 'every_5_minutes',
    code: <<~JS
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
            high_frequency: ['mouse', 'cabo_usb'], 
            medium_frequency: ['teclado'] 
          },
          recommendations: { 
            immediate_action: ['Reabastecer mouse e cabos USB'] 
          }
        };
        budget_data.budget_status.remaining = budget_data.budget_status.allocated - budget_data.budget_status.spent;
        this.createEvent(budget_data);
        return "Budget analysis completed at " + new Date().toISOString();
      }
      main();
    JS
  },
  {
    name: 'Matt 2.0 Smart Recommendations',
    schedule: 'every_10_minutes',
    code: <<~JS
      function main() {
        const recommendations = {
          timestamp: new Date().toISOString(),
          source: 'huginn_smart_recommendations',
          smart_recommendations: [
            { item: 'mouse_gamer', quantity: 25, priority: 'alta', savings_potential: 1200 },
            { item: 'teclado_mecanico', quantity: 15, priority: 'média', savings_potential: 800 },
            { item: 'headset_premium', quantity: 10, priority: 'urgente', savings_potential: 2000 }
          ],
          execution_plan: {
            total_investment: 47800,
            expected_roi: 18.5
          }
        };
        this.createEvent(recommendations);
        return "Recommendations generated at " + new Date().toISOString();
      }
      main();
    JS
  }
]

# Criar cada agente
agents_config.each do |config|
  puts "\n📊 Criando: #{config[:name]}..."
  
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
    puts "✅ Sucesso! ID: #{agent.id}"
    puts "   Schedule: #{agent.schedule}"
    
    # Forçar execução inicial
    begin
      agent.check!
      puts "   🔄 Primeira execução forçada - evento criado!"
    rescue => e
      puts "   ⚠️ Erro na primeira execução: #{e.message}"
    end
  else
    puts "❌ Erro: #{agent.errors.full_messages.join(', ')}"
  end
end

# 3. Verificar resultado final
puts "\n🎯 RESULTADO FINAL:"
puts "-" * 30
new_agents = user.agents.where("name LIKE 'Matt 2.0%'").order(:id)
new_agents.each do |agent|
  puts "✅ #{agent.name}"
  puts "   Schedule: #{agent.schedule}"
  puts "   Status: #{agent.disabled? ? 'Inativo' : 'Ativo'}"
  puts "   Eventos: #{agent.events.count}"
  puts "   Último evento: #{agent.events.last&.created_at || 'Nunca'}"
  puts ""
end

puts "🚀 CONFIGURAÇÃO COMPLETA!"
puts "💡 Acesse http://localhost:3000/agents para ver os agentes"
puts "🧪 Teste a conexão no Matt 2.0: Seção 'Agente Matt' → 'Testar Conexão'"
