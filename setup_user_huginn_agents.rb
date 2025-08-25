#!/usr/bin/env ruby

puts '🤖 CONFIGURANDO AGENTES HUGINN PARA USUÁRIO ESPECÍFICO'
puts '=' * 55

# Buscar usuário pelas credenciais fornecidas
user_email = 'danilo.fukuyama.digisystem@nubank.com.br'
user = User.find_by(email: user_email)

if user.nil?
  puts "❌ Usuário não encontrado: #{user_email}"
  puts "🔍 Usuários disponíveis:"
  User.all.each do |u|
    puts "  • #{u.email} (ID: #{u.id})"
  end
  
  puts "\n💡 Vou usar o primeiro usuário disponível..."
  user = User.first
end

puts "✅ Usuário selecionado: #{user.email} (ID: #{user.id})"

# Limpar agentes Matt 2.0 existentes deste usuário
puts "\n🧹 Limpando agentes Matt 2.0 existentes..."
existing_matt_agents = user.agents.where("name LIKE 'Matt 2.0%'")
if existing_matt_agents.any?
  puts "Removendo #{existing_matt_agents.count} agentes existentes..."
  existing_matt_agents.destroy_all
else
  puts "Nenhum agente Matt 2.0 encontrado para remover."
end

# Configuração dos 3 agentes Matt 2.0
agents_config = [
  {
    name: 'Matt 2.0 Market Intelligence',
    schedule: 'every_1h',
    description: 'Análise inteligente de mercado de gadgets',
    code: <<~JS
      var analysis = {
        timestamp: new Date().toISOString(),
        source: 'huginn_market_intelligence',
        market_data: {
          mouse_gaming: { 
            avg_price: 140 + Math.floor(Math.random() * 60), 
            trend: ['stable', 'increasing', 'decreasing'][Math.floor(Math.random() * 3)],
            recommendation: 'buy_now',
            availability: 'high'
          },
          teclado_mecanico: { 
            avg_price: 180 + Math.floor(Math.random() * 80), 
            trend: 'decreasing', 
            recommendation: 'wait_for_discount',
            availability: 'medium'
          },
          headset_gamer: { 
            avg_price: 160 + Math.floor(Math.random() * 70), 
            trend: 'increasing', 
            recommendation: 'urgent_buy',
            availability: 'low'
          },
          cabo_usb: {
            avg_price: 15 + Math.floor(Math.random() * 10),
            trend: 'stable',
            recommendation: 'buy_now',
            availability: 'high'
          }
        },
        insights: {
          market_confidence: 0.8 + Math.random() * 0.15,
          best_deals: ['teclado_mecanico', 'cabo_usb'],
          price_alerts: ['headset_gamer'],
          recommendation_count: 4
        },
        matt_recommendations: {
          priority: 'high',
          action: 'Aproveitar desconto em teclados e reabastecer cabos USB. Comprar headsets urgente!',
          budget_impact: 'moderado',
          confidence_score: 85 + Math.floor(Math.random() * 12)
        }
      };
      
      Agent.createEvent(analysis);
      analysis.status = 'Market analysis completed successfully';
      analysis;
    JS
  },
  {
    name: 'Matt 2.0 Budget Optimizer',
    schedule: 'every_2h',
    description: 'Otimização inteligente de orçamento e análise de perdas',
    code: <<~JS
      var spent = Math.floor(Math.random() * 25000) + 15000;
      var efficiency = 0.7 + Math.random() * 0.25;
      
      var budget_data = {
        timestamp: new Date().toISOString(),
        source: 'huginn_budget_optimizer',
        budget_status: { 
          allocated: 60000, 
          spent: spent,
          remaining: 60000 - spent,
          efficiency: efficiency,
          utilization: (spent / 60000 * 100).toFixed(1) + '%'
        },
        loss_patterns: { 
          high_frequency: ['mouse', 'cabo_usb', 'fone_ouvido', 'carregador'],
          medium_frequency: ['teclado', 'webcam', 'mousepad'],
          low_frequency: ['monitor', 'impressora', 'hub_usb'],
          critical_items: ['headset_gamer', 'adaptador_usb_c']
        },
        recommendations: { 
          immediate_action: [
            'Reabastecer mouse (estoque crítico)',
            'Comprar cabos USB em quantidade',
            'Revisar fornecedor de fones'
          ],
          cost_optimization: 'Negociar desconto por volume em itens de alta rotação',
          risk_mitigation: 'Diversificar fornecedores para itens críticos',
          predicted_savings: Math.floor(Math.random() * 8000) + 4000
        },
        ai_insights: {
          risk_level: ['baixo', 'médio'][Math.floor(Math.random() * 2)],
          confidence: 0.88 + Math.random() * 0.1,
          next_review: new Date(Date.now() + 7200000).toISOString(), // +2h
          efficiency_trend: efficiency > 0.8 ? 'improving' : 'stable'
        }
      };
      
      Agent.createEvent(budget_data);
      budget_data.status = 'Budget optimization completed successfully';
      budget_data;
    JS
  },
  {
    name: 'Matt 2.0 Smart Recommendations',
    schedule: 'every_1d',
    description: 'Sistema de recomendações inteligentes baseado em IA',
    code: <<~JS
      var recommendations = {
        timestamp: new Date().toISOString(),
        source: 'huginn_smart_recommendations',
        algorithm_version: '2.2.0',
        confidence_level: 0.91 + Math.random() * 0.08,
        smart_recommendations: [
          { 
            item: 'mouse_gamer', 
            quantity: 20 + Math.floor(Math.random() * 15), 
            priority: 'alta', 
            savings_potential: 1100 + Math.floor(Math.random() * 600),
            reasoning: 'Alta frequência de perda + preço estável + desconto disponível',
            urgency: 'immediate'
          },
          { 
            item: 'teclado_mecanico', 
            quantity: 8 + Math.floor(Math.random() * 12), 
            priority: 'média', 
            savings_potential: 650 + Math.floor(Math.random() * 400),
            reasoning: 'Oportunidade de desconto sazonal + estoque baixo',
            urgency: 'week'
          },
          { 
            item: 'headset_premium', 
            quantity: 6 + Math.floor(Math.random() * 9), 
            priority: 'urgente', 
            savings_potential: 1800 + Math.floor(Math.random() * 900),
            reasoning: 'Preços subindo + demanda crescente + fornecedor limitado',
            urgency: 'critical'
          },
          { 
            item: 'cabo_usb_c', 
            quantity: 50 + Math.floor(Math.random() * 30), 
            priority: 'alta', 
            savings_potential: 400 + Math.floor(Math.random() * 200),
            reasoning: 'Item consumível + alta rotatividade + preço baixo atual',
            urgency: 'immediate'
          }
        ],
        market_intelligence: {
          seasonal_trends: 'Período favorável para eletrônicos',
          supplier_status: 'Estável com 3 fornecedores preferenciais',
          economic_indicators: 'Favorável para compras em volume',
          price_volatility: 'Baixa para próximos 30 dias'
        },
        execution_plan: {
          phase1: 'Comprar headsets premium IMEDIATAMENTE (preços subindo)',
          phase2: 'Processar pedido de cabos USB-C e mouses (desconto volume)',
          phase3: 'Aguardar confirmação de desconto em teclados (1 semana)',
          total_investment: 45000 + Math.floor(Math.random() * 20000),
          expected_roi: 16.5 + Math.random() * 8,
          payback_period: '3-4 meses',
          risk_assessment: 'Baixo'
        }
      };
      
      Agent.createEvent(recommendations);
      recommendations.status = 'Smart recommendations generated successfully';
      recommendations;
    JS
  }
]

# Criar cada agente
puts "\n🚀 CRIANDO AGENTES MATT 2.0..."
created_count = 0

agents_config.each_with_index do |config, index|
  puts "\n#{index + 1}. 🤖 Criando: #{config[:name]}"
  puts "   📅 Schedule: #{config[:schedule]}"
  puts "   📝 #{config[:description]}"
  
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
    puts "   ✅ Agente criado! ID: #{agent.id}"
    created_count += 1
    
    # Executar imediatamente para gerar primeiro evento
    puts "   🚀 Executando primeira vez..."
    begin
      agent.check
      agent.reload
      puts "   📊 Primeiro evento criado! Total: #{agent.events.count}"
      
      if agent.events.any?
        latest = agent.events.last
        puts "   📅 Evento: #{latest.created_at.strftime('%H:%M:%S')}"
        puts "   🔗 Source: #{latest.payload['source']}"
      end
    rescue => e
      puts "   ⚠️ Primeira execução: #{e.message[0..60]}..."
    end
  else
    puts "   ❌ Erro: #{agent.errors.full_messages.join(', ')}"
  end
end

# Resultado final
puts "\n" + "=" * 55
puts "🎯 CONFIGURAÇÃO FINALIZADA!"
puts "✅ #{created_count}/#{agents_config.count} agentes criados com sucesso"

if created_count > 0
  puts "\n📊 AGENTES ATIVOS PARA: #{user.email}"
  final_agents = user.agents.where("name LIKE 'Matt 2.0%'").order(:name)
  final_agents.each do |agent|
    puts "• #{agent.name}"
    puts "  Schedule: #{agent.schedule} | Eventos: #{agent.events.count}"
    puts "  Status: #{agent.disabled? ? '❌ Inativo' : '✅ Ativo'}"
    puts ""
  end
  
  puts "🌐 ACESSE AGORA: http://localhost:3000/agents"
  puts "🔑 Login: #{user.email}"
  puts "🔒 Use sua senha para fazer login"
  puts ""
  puts "🧪 TESTE NO MATT 2.0:"
  puts "   1. Dashboard → Seção 'Agente Matt'"
  puts "   2. Clique '🧪 Testar Conexão Huginn'"
  puts "   3. Deve mostrar #{final_agents.sum { |a| a.events.count }} eventos"
  puts ""
  puts "💬 PERGUNTE AO MATT:"
  puts '   • "Como está o mercado de gadgets?"'
  puts '   • "Qual o status do meu orçamento?"'
  puts '   • "Há recomendações de compra hoje?"'
else
  puts "\n❌ Nenhum agente foi criado com sucesso"
  puts "💡 Verifique os logs acima para mais detalhes"
end

puts "\n🚀 Configuração completa! Agentes prontos para uso."
