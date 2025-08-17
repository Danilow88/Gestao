#!/bin/bash
# Script para preparar o projeto para deploy

echo "🚀 PREPARANDO PROJETO PARA DEPLOY..."

# Criar arquivo .streamlit/config.toml
mkdir -p .streamlit
cat > .streamlit/config.toml << EOF
[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
EOF

# Criar Procfile para Heroku
cat > Procfile << EOF
web: streamlit run app/dashboard.py --server.headless true --server.port \$PORT --server.address 0.0.0.0
EOF

# Criar arquivo runtime.txt
echo "python-3.13.5" > runtime.txt

# Criar .gitignore
cat > .gitignore << EOF
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
.venv/
venv/
.env
*.log
.DS_Store
*.sqlite
*.db
EOF

echo "✅ Projeto preparado para deploy!"
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo "1. Criar repositório no GitHub"
echo "2. Fazer push do código"
echo "3. Escolher plataforma de deploy"
echo ""
echo "🌟 RECOMENDADO: Streamlit Community Cloud (https://share.streamlit.io)"
