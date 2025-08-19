# 🏢 Serviço Local de Ping para Impressoras

Este serviço permite que o dashboard no Streamlit Cloud faça ping real nas impressoras da rede interna da Nubank.

## 📋 Como Usar

### 1. Executar o Serviço Localmente

Na sua máquina conectada à rede Nubank (ou VPN):

```bash
# Navegar para o diretório do projeto
cd /Users/danilo.fukuyama.digisystem/Downloads/finance-vibes

# Ativar ambiente virtual (se necessário)
source .venv/bin/activate

# Instalar dependência (primeira vez)
pip install flask flask-cors

# Executar o serviço
python ping_service.py
```

### 2. Verificar se Está Funcionando

O serviço estará disponível em:
- **API**: http://localhost:5000
- **Status**: http://localhost:5000/status
- **Limpar Cache**: http://localhost:5000/clear-cache

### 3. Usar no Dashboard

- **Streamlit Cloud**: Detecta automaticamente o serviço local e usa ping real
- **Local**: Funciona tanto com serviço quanto com ping direto

## 🔧 Funcionalidades

### 🎯 Ping Individual
```bash
curl http://localhost:5000/ping/172.30.139.35
```

### 📊 Ping em Lote
```bash
curl -X POST http://localhost:5000/ping/batch \
  -H "Content-Type: application/json" \
  -d '{"ips": ["172.30.139.35", "172.30.139.36", "172.30.139.37"]}'
```

### ⚡ Cache Inteligente
- **Cache**: 30 segundos por IP
- **Performance**: Respostas instantâneas dentro do cache
- **Renovação**: Automática após expiração

## 🏗️ Arquitetura

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Streamlit Cloud   │    │  Serviço Local      │    │   Rede Nubank       │
│   (Dashboard)       │◄──►│  (ping_service.py)  │◄──►│   (Impressoras)     │
│   Qualquer lugar    │    │  Na sua máquina     │    │   IPs internos      │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

## 🔍 Detecção Automática

O dashboard detecta automaticamente:

1. **🏢 Modo Local**: Ping direto se API não estiver disponível
2. **🎯 Serviço Local**: Ping via API se disponível (ideal)
3. **🌐 Streamlit Cloud**: Simulação se nenhum dos anteriores

## 🚀 Vantagens do Serviço Local

### ✅ Performance
- Cache de 30s reduz latência
- Ping em lote mais eficiente
- Interface mais responsiva

### ✅ Flexibilidade
- Funciona com Streamlit Cloud
- Mantém acesso à rede interna
- API RESTful padrão

### ✅ Monitoramento
- Status em tempo real
- Métricas de cache
- Logs de atividade

## 🛠️ Solução de Problemas

### Erro "Connection refused"
```bash
# Verificar se o serviço está rodando
ps aux | grep ping_service

# Reiniciar o serviço
python ping_service.py
```

### Firewall/Rede
```bash
# Verificar conectividade
curl http://localhost:5000/status

# Testar ping manualmente
ping 172.30.139.35
```

### Cache Antigo
```bash
# Limpar cache via API
curl http://localhost:5000/clear-cache

# Ou reiniciar o serviço
```

## 📊 Monitoramento

### Status do Serviço
- **Online**: ✅ Serviço Local Ativo (verde)
- **Fallback**: 🏢 Modo Local Direto (azul)
- **Simulação**: 🌐 Modo Streamlit Cloud (laranja)

### Indicadores no Dashboard
- **Header**: Mostra ambiente atual
- **Impressoras**: Aviso sobre método de ping
- **Resultados**: Indicam se são reais ou simulados

## 🔄 Integração

O dashboard prioriza automaticamente:

1. **🎯 API Local** (melhor opção)
2. **🏢 Ping Direto** (fallback local)  
3. **🌐 Simulação** (Streamlit Cloud)

Não é necessário configurar nada - tudo é automático!

## 📞 Suporte

Se o serviço não funcionar:

1. Verificar conexão VPN/rede Nubank
2. Confirmar que Flask está instalado
3. Testar ping manual nas impressoras
4. Verificar logs do serviço

O dashboard sempre funcionará, mas com simulação se o serviço local não estiver disponível.
