#!/usr/bin/env ruby

puts '🛠️ CRIANDO AGENTE SIMPLES PARA TESTE'
puts '=' * 40

user = User.first
puts "👤 Usuário: #{user.email}"

# Criar agente com schedule 'never' primeiro
puts "\n📊 Criando agente básico..."

agent = user.agents.build(
  name: 'Matt 2.0 Test Agent',
  type: 'Agents::JavaScriptAgent',
  schedule: 'never', # Começar sem schedule
  keep_events_for: 86400,
  options: {
    'language' => 'javascript',
    'code' => <<~JS
      function main() {
        const data = {
          timestamp: new Date().toISOString(),
          source: 'huginn_test',
          message: 'Hello from Matt 2.0 Test Agent!',
          random_value: Math.floor(Math.random() * 100)
        };
        this.createEvent(data);
        return "Test completed at " + new Date().toISOString();
      }
      main();
    JS
  }
)

if agent.save
  puts "✅ Agente básico criado! ID: #{agent.id}"
  
  # Agora tentar mudar o schedule
  puts "🔄 Alterando schedule para 'every_5_minutes'..."
  if agent.update(schedule: 'every_5_minutes')
    puts "✅ Schedule atualizado com sucesso!"
  else
    puts "❌ Erro ao atualizar schedule: #{agent.errors.full_messages.join(', ')}"
  end
  
  # Testar execução manual
  puts "🧪 Testando execução manual..."
  begin
    result = agent.check!
    puts "✅ Execução manual bem-sucedida!"
    puts "📊 Eventos: #{agent.events.count}"
    
    if agent.events.any?
      latest_event = agent.events.last
      puts "📅 Último evento: #{latest_event.created_at}"
      puts "📄 Payload: #{latest_event.payload.inspect}"
    end
  rescue => e
    puts "❌ Erro na execução: #{e.message}"
  end
  
else
  puts "❌ Erro ao criar agente: #{agent.errors.full_messages.join(', ')}"
end

puts "\n🎯 Status final do agente:"
if agent.persisted?
  puts "• Nome: #{agent.name}"
  puts "• ID: #{agent.id}"
  puts "• Schedule: #{agent.schedule}"
  puts "• Status: #{agent.disabled? ? 'Inativo' : 'Ativo'}"
  puts "• Eventos: #{agent.events.count}"
end

puts "\n✅ Teste concluído!"
