# 📊 CONFIGURAÇÃO GOOGLE SHEETS - GUIA COMPLETO

## 🎯 OBJETIVO
Conectar o sistema Finance-Vibes com sua planilha do Google Sheets para sincronização automática de dados.

---

## 🔓 MÉTODO 1: PLANILHA TOTALMENTE PÚBLICA (RECOMENDADO)

### ✅ **PASSO A PASSO VISUAL:**

1. **Abra sua planilha** no Google Sheets
2. **Clique no botão "Compartilhar"** no canto superior direito
3. **Clique em "Alterar para qualquer pessoa com o link"**
4. **Selecione "Qualquer pessoa na internet"**
5. **Defina permissão como "Visualizador"**
6. **Clique "Concluído"**

### 🧪 **TESTE RÁPIDO:**
```bash
# No terminal, execute:
python3 test_planilha_publica.py
```

---

## 🔗 MÉTODO 2: COMPARTILHAMENTO POR LINK

### Para contas que não permitem acesso público:

1. **Clique "Compartilhar"** na planilha
2. **Em "Acesso geral", selecione "Qualquer pessoa com o link"**
3. **Defina como "Visualizador"**
4. **Copie o link gerado**
5. **Use este link no sistema**

---

## 🛠️ MÉTODO 3: SERVICE ACCOUNT (AVANÇADO)

### Para organizações com restrições:

```python
# 1. Vá ao Google Cloud Console
# 2. Crie um projeto
# 3. Ative Google Sheets API
# 4. Crie uma Service Account
# 5. Baixe o arquivo credentials.json
# 6. Configure no código:

import gspread
from google.oauth2.service_account import Credentials

scopes = [
    'https://www.googleapis.com/auth/spreadsheets.readonly'
]

credentials = Credentials.from_service_account_file(
    'credentials.json', 
    scopes=scopes
)
gc = gspread.authorize(credentials)
```

---

## 📥 MÉTODO 4: EXPORTAÇÃO CSV LOCAL

### Se nenhum método online funcionar:

1. **Na planilha:** Arquivo → Download → Valores separados por vírgula (.csv)
2. **Salve o arquivo** na pasta do projeto como `inventory.csv`
3. **Use o sistema** em modo offline

---

## 🔍 DIAGNÓSTICO DE PROBLEMAS

### ❌ **ERRO 403 - Forbidden**
**Problema:** Planilha está privada
**Solução:** Siga o Método 1 ou 2 acima

### ❌ **ERRO 404 - Not Found**
**Problema:** URL incorreta ou planilha deletada
**Solução:** Verifique a URL e permissões

### ❌ **ERRO 429 - Too Many Requests**
**Problema:** Muitas tentativas de acesso
**Solução:** Aguarde alguns minutos e tente novamente

### ❌ **ERRO de Parsing**
**Problema:** Formato de dados inválido
**Solução:** Verifique se os cabeçalhos estão corretos

---

## 📋 FORMATO ESPERADO DA PLANILHA

### **Colunas obrigatórias para Inventário:**
- `name` ou `item` - Nome do gadget
- `quantidade` ou `quantity` - Quantidade em estoque
- `preco_unitario` ou `price` - Preço por unidade
- `categoria` ou `category` - Categoria do item

### **Colunas opcionais:**
- `local` - Local de armazenamento
- `fornecedor` - Fornecedor do item
- `data_compra` - Data de aquisição
- `garantia` - Período de garantia

### **Exemplo de estrutura:**
```
name          | quantidade | preco_unitario | categoria | local
Mouse Gamer   | 25         | 89.99          | Mouse     | Almoxarifado
Teclado USB   | 12         | 45.50          | Teclado   | Sala TI
Headset       | 8          | 120.00         | Audio     | Almoxarifado
```

---

## 🧪 SCRIPTS DE TESTE

### **Teste Simples (Terminal):**
```bash
curl "https://docs.google.com/spreadsheets/d/SEU_SHEET_ID/export?format=csv&gid=0"
```

### **Teste Completo (Python):**
```python
import requests
import pandas as pd

# Substitua pela sua URL
sheet_url = "https://docs.google.com/spreadsheets/d/SEU_ID/edit#gid=0"

# Converter para CSV
sheet_id = sheet_url.split('/d/')[1].split('/')[0]
csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"

# Testar conexão
response = requests.get(csv_url)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    df = pd.read_csv(csv_url)
    print(f"✅ Sucesso! {len(df)} linhas, {len(df.columns)} colunas")
    print("Colunas:", list(df.columns))
else:
    print("❌ Falhou! Verifique se a planilha está pública")
```

---

## 🚨 TROUBLESHOOTING COMUM

### **"Não consigo tornar pública"**
- Verifique se é conta pessoal (não corporativa)
- Admin da organização pode ter bloqueado
- Use Método 2 (compartilhamento por link)

### **"Dados não aparecem no sistema"**
- Confirme os nomes das colunas
- Verifique se há linhas vazias no topo
- Teste a URL diretamente no navegador

### **"Conexão lenta/instável"**
- Use cache local (CSV)
- Configure sincronização agendada
- Considere Service Account

---

## 📞 SUPORTE

Se nenhum método funcionar:
1. ✅ Execute o script de teste
2. ✅ Verifique os logs de erro
3. ✅ Exporte para CSV como backup
4. ✅ Configure sincronização manual

**Status da conexão aparece no dashboard na seção "Integração Google Sheets"** 📊
