# 🚀 Sistema de Estoque Integrado - Finance Vibes

## 📋 Visão Geral

Sistema completo de gestão de estoque integrado ao app finance-vibes, com funcionalidades avançadas para controle total de inventário, notas fiscais, movimentações e prateleiras.

## ✨ Funcionalidades Integradas

### 1. 📄 **ENTRADA DE NF ESTOQUE**
- Cadastro completo de notas fiscais
- Integração automática com fornecedores
- Rastreamento de valores, fretes e impostos
- Histórico completo de entradas

### 2. 🏷️ **CONTROLE POR N/S E ATIVO**
- Controle por número de série
- Rastreamento de ativos individuais
- Busca avançada por identificadores únicos
- Status de ativos (ativo/inativo)

### 3. 🏷️ **CONTROLE POR SKU E QUANTIDADE**
- Sistema de SKUs únicos para cada produto
- Controle de quantidade em tempo real
- Rastreamento de localização por SKU
- Histórico de movimentações por produto

### 4. 📦 **MOVIMENTAÇÃO DO ESTOQUE**
- Entrada de materiais
- Saída de materiais
- Transferências entre locais
- Rastreamento de motivos e usuários
- Histórico completo de movimentações

### 5. 📊 **MAPEAMENTO DE PRATELEIRAS NO ESTOQUE**
- Sistema de prateleiras organizadas
- Controle de capacidade por prateleira
- Localização por prédio, andar e setor
- Status de ocupação em tempo real

### 6. 📦 **ESTOQUE ITENS POR PRATELEIRA**
- Visualização detalhada por prateleira
- Controle de posicionamento
- Capacidade utilizada vs. disponível
- Rastreamento de itens específicos

### 7. 📝 **ENTRADA E SAÍDA DE MATERIAIS**
- **Motivo**: Rastreamento completo de justificativas
- **Quantidade**: Controle preciso de volumes
- **Data**: Histórico temporal completo
- **Usuário**: Auditoria de responsáveis

### 8. 🏢 **CADASTRO DE FORNECEDORES**
- Informações completas de fornecedores
- CNPJ, endereço, contatos
- Status de ativação
- Histórico de relacionamento

### 9. 👥 **CADASTRO DE UTILIZADORES**
- Sistema de usuários integrado
- Controle de acesso por perfil
- Histórico de ações
- Auditoria completa

### 10. 📋 **CADASTRO DE PRODUTOS**
- Catálogo completo de produtos
- Categorização inteligente
- Especificações técnicas
- Relacionamento com fornecedores

### 11. 🔗 **FORNECEDOR-PRODUTO**
- Mapeamento de fornecedores por produto
- Histórico de compras
- Análise de fornecedores preferenciais
- Controle de qualidade

## 🗄️ Estrutura de Dados

### Arquivos CSV Integrados

```
data/
├── fornecedores.csv          # Cadastro de fornecedores
├── produtos.csv              # Catálogo de produtos
├── notas_fiscais.csv         # Histórico de NFs
├── movimentacoes.csv         # Movimentações de estoque
├── prateleiras.csv           # Mapeamento de prateleiras
└── estoque_prateleiras.csv   # Estoque por prateleira
```

### Relacionamentos

```
Fornecedores ←→ Produtos ←→ Estoque ←→ Prateleiras
     ↓              ↓           ↓           ↓
Notas Fiscais → Movimentações → Estoque_Atual
```

## 🔧 Como Usar

### 1. **Acesso ao Sistema**
- Login: `danilo.fukuyama.digisystem@nubank.com.br`
- Senha: `admin123`

### 2. **Navegação Principal**
- **📄 NFs**: Gestão de notas fiscais
- **📦 Mov**: Movimentações de estoque
- **🏷️ Serial**: Controle por número de série
- **📊 Prateleiras**: Mapeamento de prateleiras
- **🏢 Forn**: Cadastro de fornecedores
- **📋 Prod**: Cadastro de produtos
- **📤 Exp**: Exportação de dados

### 3. **Fluxo de Trabalho**

#### **Entrada de Material:**
1. Cadastrar fornecedor (se não existir)
2. Cadastrar produto (se não existir)
3. Registrar nota fiscal
4. Sistema automaticamente atualiza estoque
5. Material disponível para uso

#### **Saída de Material:**
1. Selecionar produto por SKU
2. Informar quantidade e motivo
3. Sistema atualiza estoque automaticamente
4. Registro de movimentação criado

#### **Transferência:**
1. Selecionar produto e quantidade
2. Definir local de origem e destino
3. Sistema atualiza ambas as prateleiras
4. Histórico de transferência registrado

## 📊 Relatórios Disponíveis

### **Métricas em Tempo Real:**
- Total de itens em estoque
- Valor total do inventário
- Distribuição por categoria
- Ocupação de prateleiras

### **Relatórios por Período:**
- Movimentações (7, 30, 90 dias, 1 ano)
- Valor por categoria
- Estoque por local
- Histórico de fornecedores

### **Exportação:**
- CSV em arquivo ZIP
- Excel com múltiplas abas
- Dados completos do sistema

## 🔒 Segurança e Auditoria

### **Controle de Acesso:**
- Usuários com perfis específicos
- Administradores com acesso total
- Usuários com acesso limitado
- Histórico de todas as ações

### **Rastreabilidade:**
- Todas as movimentações registradas
- Usuário responsável por cada ação
- Timestamp de todas as operações
- Histórico completo de alterações

## 🚀 Benefícios do Sistema Integrado

### **1. Visibilidade Total:**
- Estoque em tempo real
- Localização precisa de cada item
- Histórico completo de movimentações
- Rastreamento de fornecedores

### **2. Controle Automatizado:**
- Atualização automática de estoque
- Cálculo automático de valores
- Controle de capacidade de prateleiras
- Alertas de estoque baixo

### **3. Eficiência Operacional:**
- Redução de erros manuais
- Processos padronizados
- Relatórios automáticos
- Exportação facilitada

### **4. Tomada de Decisão:**
- Dados em tempo real
- Análise de tendências
- Otimização de estoque
- Planejamento de compras

## 🔧 Configuração Técnica

### **Dependências:**
```bash
pip install -r requirements.txt
```

### **Execução:**
```bash
streamlit run app/dashboard.py
```

### **Acesso:**
- URL: `http://localhost:8501`
- Navegador: Chrome, Firefox, Safari

## 📈 Próximas Funcionalidades

### **Fase 2:**
- Integração com APIs de fornecedores
- Sistema de alertas automáticos
- Dashboard executivo
- Relatórios avançados

### **Fase 3:**
- Integração com sistemas ERP
- Controle de qualidade
- Gestão de garantias
- Sistema de manutenção

## 🆘 Suporte

### **Problemas Comuns:**
1. **Dados não carregam**: Verificar arquivos CSV na pasta `data/`
2. **Erro de permissão**: Verificar acesso à pasta do projeto
3. **Sistema lento**: Verificar tamanho dos arquivos CSV

### **Contato:**
- **Desenvolvedor**: Danilo Fukuyama
- **Email**: danilo.fukuyama.digisystem@nubank.com.br
- **Sistema**: Finance Vibes - Gestão de Estoque

---

## 🎯 **Status do Sistema: ✅ ATIVO E FUNCIONAL**

**Última Atualização**: Janeiro 2025  
**Versão**: 2.0 - Sistema Integrado Completo  
**Status**: 🟢 Produção  
**Performance**: ⚡ Otimizado  
**Segurança**: �� Nível Empresarial
