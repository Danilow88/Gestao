#!/usr/bin/env python3
"""
Script de Setup para Dashboard Local de Impressoras
Facilita a instalação e execução do sistema de monitoramento local
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path

def print_banner():
    """Exibe banner do sistema"""
    print("=" * 70)
    print("🖨️  DASHBOARD LOCAL DE IMPRESSORAS - SETUP AUTOMÁTICO")
    print("=" * 70)
    print("Sistema de monitoramento local para verificação de conectividade")
    print("Desenvolvido para execução local e sincronização com dashboard na nuvem")
    print("=" * 70)

def check_python_version():
    """Verifica se a versão do Python é compatível"""
    print("🐍 Verificando versão do Python...")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ é necessário!")
        print(f"   Versão atual: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} - Compatível!")
    return True

def check_pip():
    """Verifica se o pip está disponível"""
    print("📦 Verificando pip...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      capture_output=True, check=True)
        print("✅ pip disponível!")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ pip não encontrado!")
        return False

def install_requirements():
    """Instala as dependências necessárias"""
    print("📥 Instalando dependências...")
    
    requirements = [
        "streamlit>=1.28.0",
        "pandas>=1.5.0",
        "requests>=2.28.0"
    ]
    
    for package in requirements:
        print(f"   Instalando {package}...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], check=True, capture_output=True)
            print(f"   ✅ {package} instalado!")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Erro ao instalar {package}: {e}")
            return False
    
    return True

def create_requirements_file():
    """Cria arquivo requirements.txt"""
    print("📝 Criando requirements.txt...")
    
    requirements_content = """# Dashboard Local de Impressoras - Dependências
streamlit>=1.28.0
pandas>=1.5.0
requests>=2.28.0
"""
    
    try:
        with open("requirements_local.txt", "w") as f:
            f.write(requirements_content)
        print("✅ requirements_local.txt criado!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar requirements.txt: {e}")
        return False

def create_run_script():
    """Cria script de execução para diferentes sistemas"""
    print("🚀 Criando scripts de execução...")
    
    # Script para Windows
    if platform.system().lower() == "windows":
        batch_content = """@echo off
echo 🖨️ Iniciando Dashboard Local de Impressoras...
echo.
echo 📋 Instruções:
echo 1. Aguarde o dashboard abrir no navegador
echo 2. Configure os dados das impressoras
echo 3. Execute o ping local
echo 4. Envie resultados para a nuvem
echo.
echo 🔧 Para parar: Ctrl+C
echo.
pause
streamlit run app/dashboard_local_impressoras.py
pause
"""
        
        try:
            with open("executar_dashboard_local.bat", "w", encoding="utf-8") as f:
                f.write(batch_content)
            print("✅ executar_dashboard_local.bat criado!")
        except Exception as e:
            print(f"❌ Erro ao criar .bat: {e}")
    
    # Script para Linux/Mac
    else:
        shell_content = """#!/bin/bash
echo "🖨️ Iniciando Dashboard Local de Impressoras..."
echo ""
echo "📋 Instruções:"
echo "1. Aguarde o dashboard abrir no navegador"
echo "2. Configure os dados das impressoras"
echo "3. Execute o ping local"
echo "4. Envie resultados para a nuvem"
echo ""
echo "🔧 Para parar: Ctrl+C"
echo ""
read -p "Pressione Enter para continuar..."
streamlit run app/dashboard_local_impressoras.py
"""
        
        try:
            with open("executar_dashboard_local.sh", "w") as f:
                f.write(shell_content)
            
            # Tornar executável
            os.chmod("executar_dashboard_local.sh", 0o755)
            print("✅ executar_dashboard_local.sh criado!")
        except Exception as e:
            print(f"❌ Erro ao criar .sh: {e}")

def create_config_file():
    """Cria arquivo de configuração"""
    print("⚙️ Criando arquivo de configuração...")
    
    config = {
        "cloud_dashboard_url": "https://your-streamlit-app.onrender.com",
        "ping_timeout": 5,
        "batch_delay": 0.2,
        "auto_save": True,
        "auto_cloud_sync": False
    }
    
    try:
        with open("config_local.json", "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print("✅ config_local.json criado!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar config: {e}")
        return False

def create_sample_csv():
    """Cria arquivo CSV de exemplo"""
    print("📊 Criando CSV de exemplo...")
    
    sample_data = """IP,local,modelo,serial,status_manual
172.25.61.53,Sede,HP LaserJet Pro M404n,ABC123456,Ativo
172.25.61.54,Sede,HP LaserJet Pro M404n,DEF789012,Ativo
192.168.1.100,Filial,Canon ImageRunner ADVANCE 6575i,GHI345678,Ativo
10.0.0.50,Escritório,Brother HL-L2350DW,XYZ901234,Ativo
192.168.1.101,Almoxarifado,Epson WorkForce Pro WF-3720,JKL567890,Ativo"""
    
    try:
        with open("impressoras_exemplo.csv", "w", encoding="utf-8") as f:
            f.write(sample_data)
        print("✅ impressoras_exemplo.csv criado!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar CSV: {e}")
        return False

def create_readme():
    """Cria arquivo README com instruções"""
    print("📖 Criando README...")
    
    readme_content = """# 🖨️ Dashboard Local de Impressoras

## 📋 Descrição
Sistema de monitoramento local para verificação de conectividade das impressoras da sua rede. 
Permite executar ping local e sincronizar resultados com dashboard na nuvem.

## 🚀 Como Usar

### 1. Instalação
```bash
# Instalar dependências
pip install -r requirements_local.txt

# Ou usar o script de setup
python setup_dashboard_local.py
```

### 2. Execução
```bash
# Windows
executar_dashboard_local.bat

# Linux/Mac
./executar_dashboard_local.sh

# Ou manualmente
streamlit run app/dashboard_local_impressoras.py
```

### 3. Configuração
1. Abra o dashboard no navegador
2. Configure a URL do dashboard na nuvem
3. Carregue dados das impressoras (CSV, manual ou exemplo)
4. Execute o ping local
5. Visualize resultados e envie para a nuvem

## 📁 Arquivos Criados
- `app/dashboard_local_impressoras.py` - Dashboard principal
- `requirements_local.txt` - Dependências Python
- `config_local.json` - Configurações
- `impressoras_exemplo.csv` - Dados de exemplo
- `executar_dashboard_local.bat/.sh` - Scripts de execução

## 🔧 Funcionalidades
- ✅ Ping local real para impressoras
- ✅ Upload de arquivo CSV
- ✅ Entrada manual de dados
- ✅ Dados de exemplo para teste
- ✅ Salvamento local de resultados
- ✅ Envio para dashboard na nuvem
- ✅ Interface responsiva e intuitiva
- ✅ Suporte Windows/Linux/Mac

## 📞 Suporte
Para dúvidas ou problemas, consulte a documentação ou entre em contato com o suporte.

---
Desenvolvido para execução local e sincronização com dashboard na nuvem
"""
    
    try:
        with open("README_LOCAL.md", "w", encoding="utf-8") as f:
            f.write(readme_content)
        print("✅ README_LOCAL.md criado!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar README: {e}")
        return False

def run_dashboard():
    """Executa o dashboard diretamente"""
    print("🎯 Deseja executar o dashboard agora?")
    
    if platform.system().lower() == "windows":
        response = input("Digite 's' para sim ou Enter para não: ").lower()
    else:
        response = input("Digite 's' para sim ou Enter para não: ").lower()
    
    if response in ['s', 'sim', 'y', 'yes']:
        print("🚀 Iniciando dashboard...")
        print("📋 Abrindo no navegador...")
        print("🔧 Para parar: Ctrl+C")
        print("-" * 50)
        
        try:
            subprocess.run([
                sys.executable, "-m", "streamlit", "run", 
                "app/dashboard_local_impressoras.py"
            ])
        except KeyboardInterrupt:
            print("\n👋 Dashboard encerrado pelo usuário")
        except Exception as e:
            print(f"❌ Erro ao executar dashboard: {e}")
    else:
        print("ℹ️ Dashboard não executado. Use um dos scripts criados para executar depois.")

def main():
    """Função principal"""
    print_banner()
    
    # Verificações iniciais
    if not check_python_version():
        return
    
    if not check_pip():
        print("❌ pip é necessário para continuar!")
        return
    
    print("\n🔧 Iniciando setup...")
    
    # Instalar dependências
    if not install_requirements():
        print("❌ Falha na instalação das dependências!")
        return
    
    # Criar arquivos necessários
    create_requirements_file()
    create_config_file()
    create_sample_csv()
    create_readme()
    create_run_script()
    
    print("\n✅ Setup concluído com sucesso!")
    print("\n📁 Arquivos criados:")
    print("   - requirements_local.txt")
    print("   - config_local.json")
    print("   - impressoras_exemplo.csv")
    print("   - README_LOCAL.md")
    
    if platform.system().lower() == "windows":
        print("   - executar_dashboard_local.bat")
    else:
        print("   - executar_dashboard_local.sh")
    
    print("\n🚀 Para executar o dashboard:")
    if platform.system().lower() == "windows":
        print("   - Duplo clique em: executar_dashboard_local.bat")
    else:
        print("   - Execute: ./executar_dashboard_local.sh")
    
    print("\n💡 Ou execute manualmente:")
    print("   streamlit run app/dashboard_local_impressoras.py")
    
    # Perguntar se quer executar agora
    print("\n" + "=" * 50)
    run_dashboard()

if __name__ == "__main__":
    main()
