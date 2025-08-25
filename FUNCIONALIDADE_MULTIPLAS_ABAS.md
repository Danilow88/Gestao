# 📋 Funcionalidade: Seleção de Múltiplas Abas do Excel

## 🎯 Descrição
Implementação de funcionalidade que permite ao usuário escolher quais abas de uma planilha Excel processar durante o upload de dados no sistema finance-vibes.

## ✨ Funcionalidades Implementadas

### 1. **Detecção Automática de Abas**
- O sistema detecta automaticamente todas as abas disponíveis em arquivos Excel (.xlsx, .xls)
- Exibe uma lista com todas as abas encontradas
- Mostra preview básico de cada aba (número de linhas e colunas)

### 2. **Interface de Seleção**
- **Opção "Selecionar todas as abas"**: Marca automaticamente todas as abas para processamento
- **Seleção individual**: Permite escolher abas específicas através de checkboxes
- **Preview das abas**: Mostra informações básicas sobre cada aba (linhas e colunas)

### 3. **Processamento Inteligente**
- **Múltiplas abas**: Processa cada aba selecionada individualmente
- **Identificação da origem**: Adiciona coluna `aba_origem` para identificar de qual aba cada registro veio
- **Combinação automática**: Combina dados de todas as abas selecionadas em um único dataset
- **Barra de progresso**: Mostra progresso do processamento de cada aba

### 4. **Validação e Limpeza**
- Cada aba é validada e limpa individualmente
- Erros em uma aba não impedem o processamento das outras
- Relatório de erros específico por aba

### 5. **Estatísticas Detalhadas**
- Mostra quantas abas foram processadas
- Exibe número de registros por aba
- Estatísticas consolidadas dos dados finais
- Informações sobre duplicatas removidas

## 🔧 Como Usar

### Passo 1: Upload do Arquivo Excel
1. Acesse a seção "Upload Inteligente de Dados"
2. Faça upload de um arquivo Excel (.xlsx ou .xls)

### Passo 2: Seleção de Abas
1. O sistema detecta automaticamente as abas disponíveis
2. Escolha uma das opções:
   - **"Selecionar todas as abas"**: Processa todas as abas
   - **Seleção manual**: Marque apenas as abas desejadas

### Passo 3: Configuração e Importação
1. Configure o mapeamento de colunas (se necessário)
2. Escolha o destino dos dados
3. Clique em "🚀 IMPORTAR DADOS"

### Passo 4: Visualização dos Resultados
- Veja quantas abas foram processadas
- Confira o número de registros por aba
- Visualize estatísticas consolidadas

## 📊 Exemplo de Uso

```
Arquivo: inventario_2024.xlsx
Abas detectadas:
- HQ1_Equipamentos (150 registros)
- SPARK_Gadgets (75 registros)  
- TVs_Monitores (45 registros)

Resultado:
✅ 3 abas processadas
✅ 270 registros importados
✅ Coluna 'aba_origem' adicionada para rastreamento
```

## 🔄 Compatibilidade

### Formatos Suportados
- Excel 2007+ (.xlsx)
- Excel 97-2003 (.xls)

### Tipos de Dados Compatíveis
- Inventário Unificado
- Estoque HQ1/SPARK
- Gadgets e Equipamentos
- TVs e Monitores
- Movimentações
- Todos os formatos já suportados pelo sistema

## ⚠️ Considerações Importantes

1. **Estrutura das Abas**: Recomenda-se que todas as abas tenham estrutura similar para melhor mapeamento
2. **Tamanho do Arquivo**: Arquivos muito grandes com muitas abas podem demorar mais para processar
3. **Memória**: O processamento de múltiplas abas grandes pode consumir mais memória
4. **Duplicatas**: O sistema remove duplicatas considerando dados de todas as abas combinadas

## 🐛 Tratamento de Erros

- Erros em abas individuais não impedem o processamento das outras
- Abas vazias são ignoradas automaticamente
- Abas com estrutura incompatível geram avisos mas não param o processo
- Log detalhado de erros por aba

## 🔮 Próximas Melhorias

- [ ] Preview mais detalhado dos dados de cada aba
- [ ] Mapeamento de colunas específico por aba
- [ ] Processamento em lote otimizado
- [ ] Suporte a fórmulas do Excel
- [ ] Exportação dos resultados por aba

---

**Desenvolvido para finance-vibes v2024**  
**Data de implementação:** Janeiro 2025
