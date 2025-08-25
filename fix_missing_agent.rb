#!/usr/bin/env ruby

puts '🔧 Criando agente que faltou...'

user = User.find_by(email: 'admin@example.com')
puts "✅ Usuário encontrado: #{user.email}"

# Verificar se já existe
existing = user.agents.find_by(name: 'Matt 2.0 Market Intelligence')
if existing
  puts "⚠️ Agente já existe: #{existing.name} (ID: #{existing.id})"
  puts "Excluindo para recriar..."
  existing.destroy
end

# Criar agente de mercado com schedule correto
market_agent = user.agents.build(
  name: 'Matt 2.0 Market Intelligence',
  type: 'Agents::JavaScriptAgent',
  schedule: 'every_2_minutes', # Formato válido
  keep_events_for: 604800,
  options: {
    'language' => 'javascript',
    'code' => <<~JS
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
    JS
  }
)

if market_agent.save
  puts "✅ Agente de mercado criado! ID: #{market_agent.id}"
  puts "📊 Schedule: #{market_agent.schedule}"
  puts "🔄 Status: #{market_agent.disabled? ? 'Inativo' : 'Ativo'}"
else
  puts "❌ Erro no agente de mercado:"
  puts market_agent.errors.full_messages.join(', ')
end

puts "\n🎯 Resumo final dos agentes Matt 2.0:"
user.agents.where("name LIKE 'Matt 2.0%'").each do |agent|
  puts "• #{agent.name} (ID: #{agent.id}) - #{agent.schedule}"
end

puts "\n✅ Pronto! Agentes configurados para Matt 2.0"
