# 🤖 Matt 2.0 - Comandos Inteligentes de Orçamento

## 🎯 Descrição
O Matt 2.0 agora possui capacidade de processamento de linguagem natural avançada, permitindo configurar orçamentos, limites e prioridades através de comandos simples em linguagem natural.

## ✨ Novas Funcionalidades

### 1. **Processamento Inteligente de Comandos**
- Extração automática de valores de orçamento
- Identificação de gadgets prioritários
- Configuração de limites gerais e específicos
- Análise automática completa

### 2. **Controle Manual Mantido**
- Interface visual para configuração manual
- Controle individual de quantidades por gadget
- Cálculo em tempo real de custos
- Verificação automática de orçamento

### 3. **Dupla Funcionalidade**
- **Via Prompt:** Comandos em linguagem natural
- **Via Interface:** Controles manuais tradicionais
- **Híbrido:** Combinação de ambos os métodos

## 🗣️ Exemplos de Comandos Suportados

### Comandos Básicos
```
"Me dê um orçamento para R$ 80.000"
"Budget de 50 mil para gadgets"
"Orçamento para R$ 100.000"
```

### Comandos com Limites
```
"Orçamento de R$ 80.000 limitando a quantidade para 15"
"Budget para 100k limitando quantidade para 20"
"Me dê um orçamento de 60 mil com limite de 25 unidades"
```

### Comandos com Priorização
```
"Orçamento de R$ 50.000 priorizando mouse e headset"
"Budget para 80k dando ênfase a adaptador e teclado"
"Me dê um orçamento priorizando headset"
```

### Comandos Completos (Recomendado)
```
"Me dê um orçamento para R$ 80.000 limitando a quantidade dos gadgets para 15 e dando ênfase a mouse e headset"

"Orçamento de 100 mil limitando quantidade para 20 e priorizando adaptador e teclado"

"Budget para R$ 50.000 com limite de 25 unidades dando ênfase a headset"
```

## 🧠 Inteligência de Extração

### O que o Matt 2.0 Extrai Automaticamente:

#### 💰 **Valores de Orçamento:**
- `R$ 80.000`, `80.000`, `80k`, `80 mil`
- `50.000 reais`, `100k`, `60 mil`
- Suporte a formatos brasileiros

#### 📊 **Limites de Quantidade:**
- `limitando quantidade para 15`
- `limite de 20 unidades`
- `limitando para 25`

#### 🎯 **Gadgets Prioritários:**
- `mouse`, `teclado`, `adaptador`, `headset`
- `mouse e headset`, `adaptador e teclado`
- `priorizando mouse`, `dando ênfase a teclado`

#### 🔥 **Limites Específicos:**
- `limitando quantidade para 25 no orçamento` (para prioritários)
- Calcula automaticamente percentual extra

## 📈 Fluxo de Processamento

```
1. 🗣️ Usuário envia comando
   ↓
2. 🧠 Matt extrai informações
   ↓
3. ⚙️ Configurações aplicadas automaticamente
   ↓
4. 📊 Análise automática executada
   ↓
5. 💰 Resultado detalhado apresentado
```

## 🔧 Configurações Automáticas

### Quando você usa um comando inteligente, o Matt:

1. **Configura o Budget** → `st.session_state.matt_budget`
2. **Define Limite Geral** → `st.session_state.matt_limite_qty`
3. **Seleciona Prioritários** → `st.session_state.gadgets_preferidos`
4. **Calcula % Extra** → `st.session_state.matt_percentual_extra`
5. **Executa Análise** → Otimização automática completa

## 💡 Exemplos Práticos

### Exemplo 1: Orçamento Simples
**Comando:** `"Orçamento de R$ 50.000"`
**Resultado:**
- Budget configurado: R$ 50.000
- Análise automática executada
- Recomendações apresentadas

### Exemplo 2: Com Priorização
**Comando:** `"Budget de 80k priorizando mouse e headset"`
**Resultado:**
- Budget: R$ 80.000
- Prioritários: Mouse, Headset
- Análise com ênfase nos itens escolhidos

### Exemplo 3: Comando Completo
**Comando:** `"Me dê um orçamento para R$ 100.000 limitando a quantidade para 20 e dando ênfase a adaptador"`
**Resultado:**
- Budget: R$ 100.000
- Limite geral: 20 unidades
- Prioritário: Adaptador USB-C
- Análise completa automatizada

## 🎯 Interface Híbrida

### Controles Manuais Disponíveis:
- **Budget Total:** Slider de R$ 1.000 a R$ 500.000
- **Gadgets Prioritários:** Seleção múltipla
- **Limite por Item:** 1 a 100 unidades
- **% Extra Prioritário:** 0% a 50%
- **Quantidades Individuais:** Mouse, Teclado, Adaptador, Headset

### Botões de Sugestão Rápida:
- 📊 **Analise meus dados**
- 💰 **Otimizar orçamento**
- 🔥 **Calcular orçamento**
- 🛒 **Sugerir compras**
- 🎯 **Comando inteligente**
- 📦 **Status do estoque**

## 🚀 Casos de Uso

### 1. **Planejamento Trimestral**
```
"Budget de R$ 150.000 para o trimestre limitando quantidade para 30 e priorizando mouse e teclado"
```

### 2. **Compra Emergencial**
```
"Orçamento de 25 mil dando ênfase a headset"
```

### 3. **Análise Rápida**
```
"Me dê um orçamento para R$ 60.000"
```

### 4. **Planejamento Específico**
```
"100k limitando para 15 unidades priorizando adaptador e mouse"
```

## 🔮 Benefícios

### ✅ **Rapidez**
- Configuração instantânea via comando
- Não precisa navegar por interfaces

### ✅ **Flexibilidade**
- Linguagem natural intuitiva
- Múltiplos formatos aceitos

### ✅ **Precisão**
- Extração inteligente de dados
- Configurações automáticas

### ✅ **Completude**
- Análise automática completa
- Resultados detalhados instantâneos

## 📋 Resumo de Comandos

| Tipo | Exemplo | Resultado |
|------|---------|-----------|
| **Básico** | `"Orçamento de R$ 50.000"` | Configuração de budget + análise |
| **Com Limite** | `"Budget de 80k limitando para 20"` | Budget + limite geral |
| **Com Prioridade** | `"50 mil priorizando mouse"` | Budget + gadget prioritário |
| **Completo** | `"100k limitando para 15 dando ênfase a headset"` | Configuração completa |

---

**Desenvolvido para finance-vibes v2024**  
**Matt 2.0 - Comandos Inteligentes**  
**Data de implementação:** Janeiro 2025
