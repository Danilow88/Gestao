# 🐳 HUGINN DOCKER - ATUALIZAÇÃO IMPORTANTE

## ⚠️ **MUDANÇA CRÍTICA - JANEIRO 2025**

As imagens Docker oficiais do Huginn foram movidas para o GitHub Container Registry (GHCR).

---

## 🔄 **MUDANÇAS NAS IMAGENS**

### **❌ IMAGENS ANTIGAS (Descontinuadas)**
```bash
# NÃO USE MAIS ESTAS IMAGENS:
huginn/huginn
huginn/huginn-single-process
```

### **✅ NOVAS IMAGENS (Atuais)**
```bash
# USE SEMPRE ESTAS IMAGENS:
ghcr.io/huginn/huginn
ghcr.io/huginn/huginn-single-process
```

---

## 🛠️ **COMO ATUALIZAR SEUS CONTAINERS**

### **1. Parar Containers Existentes**
```bash
docker stop huginn
docker rm huginn
```

### **2. Baixar Nova Imagem**
```bash
# Para versão multi-processo
docker pull ghcr.io/huginn/huginn:latest

# Para versão single-process
docker pull ghcr.io/huginn/huginn-single-process:latest
```

### **3. Executar com Nova Imagem**
```bash
# Multi-processo
docker run -d --name huginn \
  -p 3000:3000 \
  -e APP_SECRET_TOKEN=your-secret-token \
  ghcr.io/huginn/huginn

# Single-process  
docker run -d --name huginn \
  -p 3000:3000 \
  -e APP_SECRET_TOKEN=your-secret-token \
  ghcr.io/huginn/huginn-single-process
```

---

## 📝 **DOCKER COMPOSE ATUALIZADO**

### **Antes (huginn-arm64.yml):**
```yaml
services:
  huginn:
    image: huginn/huginn:latest  # ❌ ANTIGO
    ports:
      - "3000:3000"
```

### **Depois (huginn-arm64.yml):**
```yaml
services:
  huginn:
    image: ghcr.io/huginn/huginn:latest  # ✅ NOVO
    ports:
      - "3000:3000"
```

---

## ⚡ **ARQUIVOS ATUALIZADOS NESTE PROJETO**

### **✅ Atualizados:**
- `huginn-arm64.yml` - Configuração Docker Compose
- `MATT_2.0_HUGINN_INTEGRATION.md` - Documentação de integração
- `HUGINN_DOCKER_UPDATE.md` - Este arquivo de atualização

### **📋 Comandos de Verificação:**
```bash
# Verificar se estou usando imagem correta
docker images | grep huginn

# Se aparecer 'huginn/huginn', precisa atualizar!
# Se aparecer 'ghcr.io/huginn/huginn', está correto!
```

---

## 🎯 **PARA USUÁRIOS DO MATT 2.0**

### **Atualizar Huginn Existente:**
1. ⏹️ Parar Huginn atual: `docker-compose down`
2. 🔄 Atualizar docker-compose.yml com novas imagens
3. 🚀 Reiniciar: `docker-compose up -d`
4. ✅ Testar conexão no Matt 2.0

### **Nova Instalação:**
```bash
# Use sempre as novas imagens:
docker-compose -f huginn-arm64.yml up -d

# Ou para instalação rápida:
docker run -d --name huginn \
  -p 3000:3000 \
  -e APP_SECRET_TOKEN=$(openssl rand -hex 64) \
  ghcr.io/huginn/huginn
```

---

## 🔍 **TROUBLESHOOTING**

### **❌ Erro: "manifest unknown"**
**Problema:** Tentando usar imagem antiga
**Solução:** Use `ghcr.io/huginn/huginn` em vez de `huginn/huginn`

### **❌ Erro: "pull access denied"**
**Problema:** Possível cache de imagem antiga
**Solução:**
```bash
docker system prune -a  # Remove caches
docker pull ghcr.io/huginn/huginn:latest
```

### **❌ Container não inicia**
**Problema:** Volumes ou dados corrompidos
**Solução:**
```bash
docker volume prune  # Remove volumes órfãos
docker-compose up -d --force-recreate
```

---

## 📞 **SUPORTE E LINKS ÚTEIS**

### **🔗 Links Oficiais:**
- [GitHub Huginn](https://github.com/huginn/huginn)
- [GHCR Huginn](https://github.com/huginn/huginn/pkgs/container/huginn)
- [Documentação Docker](https://github.com/huginn/huginn/tree/master/docker)

### **🛠️ Comandos Úteis:**
```bash
# Ver logs do container
docker logs huginn

# Entrar no container
docker exec -it huginn bash

# Verificar saúde do container
docker inspect huginn | grep Health
```

---

## 📊 **BENEFÍCIOS DA NOVA LOCALIZAÇÃO**

### **✅ GitHub Container Registry (GHCR)**
- ⚡ **Performance:** Download mais rápido
- 🔒 **Segurança:** Melhor controle de acesso
- 🔄 **Integração:** Sincronizado com releases GitHub
- 📈 **Confiabilidade:** Infraestrutura GitHub

### **vs Docker Hub (Antigo)**
- 📦 Docker Hub ainda funciona, mas pode ser descontinuado
- 🎯 GHCR é a localização oficial recomendada
- 🚀 Melhor performance para usuários globais

---

## 🎉 **RESUMO DA MUDANÇA**

**ANTES:**
```bash
docker run -d huginn/huginn
```

**DEPOIS:**  
```bash
docker run -d ghcr.io/huginn/huginn
```

**É só isso! Simples e rápido! 🚀**

---

**Atualizado em:** Janeiro 2025  
**Projeto:** finance-vibes  
**Sistema:** Matt 2.0 + Huginn Integration
