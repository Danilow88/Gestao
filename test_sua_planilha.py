#!/usr/bin/env python3
"""
🧪 TESTE RÁPIDO DE PLANILHA GOOGLE SHEETS
Execute: python3 test_sua_planilha.py

Verifica se sua planilha está acessível publicamente
"""

import requests
import pandas as pd
import sys

def test_sheet_access(url):
    """Testa acesso à planilha"""
    print("🔍 TESTANDO PLANILHA...")
    print(f"📋 URL: {url}")
    print("-" * 60)
    
    try:
        # Fazer requisição
        response = requests.get(url, timeout=15)
        
        # Analisar resposta
        if response.status_code == 200:
            print("✅ STATUS: Planilha acessível!")
            
            # Verificar se é CSV válido
            try:
                df = pd.read_csv(url)
                print(f"📊 DADOS: {len(df)} linhas, {len(df.columns)} colunas")
                
                print("\n📋 COLUNAS ENCONTRADAS:")
                for i, col in enumerate(df.columns, 1):
                    print(f"  {i}. {col}")
                
                if len(df) > 0:
                    print(f"\n🔍 PRIMEIRA LINHA:")
                    for col in df.columns[:5]:  # Mostrar só primeiras 5 colunas
                        value = df.iloc[0][col]
                        print(f"  • {col}: {value}")
                
                print(f"\n🎉 RESULTADO: PLANILHA CONFIGURADA CORRETAMENTE!")
                return True
                
            except Exception as e:
                print(f"⚠️ AVISO: Planilha acessível, mas erro ao ler: {e}")
                return False
        
        elif response.status_code == 403:
            print("❌ ERRO 403: PLANILHA PRIVADA!")
            print("\n🔧 COMO CORRIGIR:")
            print("1. Abra a planilha no Google Sheets")
            print("2. Clique 'Compartilhar' (canto superior direito)")
            print("3. Clique 'Alterar para qualquer pessoa com o link'")
            print("4. Selecione 'Qualquer pessoa na internet'")
            print("5. Defina como 'Visualizador'")
            print("6. Clique 'Concluído'")
            return False
            
        elif response.status_code == 404:
            print("❌ ERRO 404: PLANILHA NÃO ENCONTRADA!")
            print("🔧 Verifique se a URL/ID está correto")
            return False
            
        else:
            print(f"❌ ERRO {response.status_code}: Problema de acesso")
            print("🔧 Tente tornar a planilha pública")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ ERRO: Timeout - conexão muito lenta")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ ERRO: Problema de conexão com a internet")
        return False
    except Exception as e:
        print(f"❌ ERRO INESPERADO: {e}")
        return False

def convert_url_to_csv(url):
    """Converte URL do Google Sheets para formato CSV"""
    if not url:
        return None
        
    if '/edit' in url:
        try:
            sheet_id = url.split('/d/')[1].split('/')[0]
            csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
            print(f"🔄 URL convertida para: {csv_url}")
            return csv_url
        except:
            print("❌ Erro ao extrair ID da planilha")
            return None
    
    return url

def main():
    print("🚀 TESTADOR DE PLANILHA GOOGLE SHEETS")
    print("=" * 60)
    
    # URLs de exemplo para teste
    example_urls = [
        "https://docs.google.com/spreadsheets/d/1IMcXLIyOJOANhfxKfzYlwtBqtsXJfRMhCPmoKQdCtdY/edit#gid=1546013624",
        "https://docs.google.com/spreadsheets/d/1IMcXLIyOJOANhfxKfzYlwtBqtsXJfRMhCPmoKQdCtdY/export?format=csv&gid=1546013624"
    ]
    
    if len(sys.argv) > 1:
        # URL fornecida como argumento
        sheet_url = sys.argv[1]
    else:
        # Perguntar URL
        print("\n🔗 OPÇÕES:")
        print("1. Cole a URL da sua planilha")
        print("2. Pressione ENTER para testar planilha de exemplo")
        
        user_input = input("\n📋 URL da planilha (ou ENTER): ").strip()
        
        if user_input:
            sheet_url = user_input
        else:
            sheet_url = example_urls[0]
            print(f"🧪 Testando planilha de exemplo: {sheet_url}")
    
    # Converter URL se necessário
    csv_url = convert_url_to_csv(sheet_url)
    
    if not csv_url:
        print("❌ URL inválida!")
        sys.exit(1)
    
    # Testar acesso
    success = test_sheet_access(csv_url)
    
    print("\n" + "=" * 60)
    if success:
        print("🎊 SUCESSO! Use esta URL no sistema Finance-Vibes:")
        print(f"📋 {csv_url}")
    else:
        print("❌ FALHA! Siga as instruções acima para corrigir.")
        print("📖 Consulte: GOOGLE_SHEETS_SETUP_COMPLETO.md")

if __name__ == "__main__":
    main()
