#!/usr/bin/env ruby

puts '🔍 VERIFICANDO STATUS DOS AGENTES HUGINN'
puts '=' * 50

user = User.first
puts "👤 Usuário: #{user.email}"

puts "\n📊 TODOS OS AGENTES:"
puts "-" * 30
user.agents.order(:id).each do |agent|
  status = agent.disabled? ? "❌ Inativo" : "✅ Ativo"
  puts "• #{agent.name} (ID: #{agent.id})"
  puts "  Tipo: #{agent.type}"
  puts "  Schedule: '#{agent.schedule}'"
  puts "  Status: #{status}"
  puts "  Eventos: #{agent.events.count}"
  puts ""
end

puts "\n🎯 AGENTES MATT 2.0:"
puts "-" * 30
matt_agents = user.agents.where("name LIKE 'Matt 2.0%'")
if matt_agents.any?
  matt_agents.each do |agent|
    puts "✅ #{agent.name}"
    puts "   Schedule: #{agent.schedule}"
    puts "   Eventos: #{agent.events.count}"
    puts "   Último evento: #{agent.events.last&.created_at || 'Nunca'}"
  end
else
  puts "⚠️ Nenhum agente Matt 2.0 encontrado"
end

puts "\n🕒 SCHEDULES VÁLIDOS:"
puts ['never', 'every_1_minute', 'every_2_minutes', 'every_5_minutes', 'every_10_minutes', 'every_30_minutes', 'every_1_hour'].join(', ')

puts "\n🔧 CORRIGINDO SCHEDULES INVÁLIDOS..."
matt_agents.each do |agent|
  case agent.schedule
  when 'every_3m'
    agent.update(schedule: 'every_2_minutes')
    puts "• #{agent.name}: 'every_3m' → 'every_2_minutes'"
  when 'every_5m' 
    agent.update(schedule: 'every_5_minutes')
    puts "• #{agent.name}: 'every_5m' → 'every_5_minutes'"
  when 'every_10m'
    agent.update(schedule: 'every_10_minutes') 
    puts "• #{agent.name}: 'every_10m' → 'every_10_minutes'"
  else
    puts "• #{agent.name}: Schedule OK (#{agent.schedule})"
  end
end

puts "\n🎯 STATUS FINAL:"
matt_agents.reload.each do |agent|
  puts "• #{agent.name}: #{agent.schedule} (#{agent.disabled? ? 'Inativo' : 'Ativo'})"
end

puts "\n✅ Verificação completa!"
