# CÓDIGO PARA RODAR NO GOOGLE COLAB
# Cole este código em uma célula do Google Colab

!pip install streamlit pyngrok openpyxl plotly pandas

# Fazer upload dos arquivos para o Colab
from google.colab import files
import os

# Criar estrutura de diretórios
os.makedirs('app', exist_ok=True)
os.makedirs('data', exist_ok=True)

# Fazer upload do dashboard.py para a pasta app/
print("📁 Faça upload do arquivo dashboard.py para a pasta app/")
uploaded = files.upload()

# Instalar ngrok para acesso público
!pip install pyngrok
from pyngrok import ngrok

# Autenticar ngrok (você precisa criar conta gratuita em ngrok.com)
ngrok.set_auth_token("SEU_TOKEN_NGROK_AQUI")

# Rodar Streamlit
!streamlit run app/dashboard.py &

# Criar túnel público
public_url = ngrok.connect(8501)
print(f"🌐 Sua aplicação está disponível em: {public_url}")
