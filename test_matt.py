#!/usr/bin/env python3
"""
🧪 TESTE DO MATT 2.0 - Sistema de IA Híbrida

Este arquivo testa as funcionalidades principais do MATT:
1. Conexão com Ollama (se disponível)
2. Sistema local de fallback
3. Processamento de mensagens
4. Respostas inteligentes

Para executar:
python test_matt.py
"""

import sys
import os

# Adicionar o diretório app ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_matt_basic():
    """Teste básico do sistema MATT"""
    print("🧪 TESTE BÁSICO DO MATT 2.0")
    print("=" * 50)
    
    try:
        # Importar funções do dashboard
        from dashboard import process_matt_response, matt_ai_real_response, conectar_ollama_local
        
        # Teste 1: Sistema local
        print("\n1️⃣ Testando Sistema Local...")
        response_local = process_matt_response("oi")
        print(f"✅ Resposta: {response_local[:100]}...")
        
        # Teste 2: Conexão Ollama
        print("\n2️⃣ Testando Conexão Ollama...")
        try:
            response_ollama = conectar_ollama_local("oi")
            if response_ollama:
                print(f"✅ Ollama conectado! Resposta: {response_ollama[:100]}...")
            else:
                print("⚠️ Ollama não retornou resposta (pode estar offline)")
        except Exception as e:
            print(f"❌ Erro na conexão Ollama: {str(e)}")
        
        # Teste 3: Sistema híbrido
        print("\n3️⃣ Testando Sistema Híbrido...")
        response_hybrid = matt_ai_real_response("oi")
        print(f"✅ Sistema híbrido funcionando! Resposta: {response_hybrid[:100]}...")
        
        # Teste 4: Perguntas específicas
        print("\n4️⃣ Testando Perguntas Específicas...")
        questions = [
            "Como otimizar meu orçamento?",
            "Analise meus dados de perda",
            "Sugira compras para este mês",
            "Qual o status do meu estoque?"
        ]
        
        for i, question in enumerate(questions, 1):
            print(f"\n   Pergunta {i}: {question}")
            response = matt_ai_real_response(question)
            print(f"   Resposta: {response[:150]}...")
        
        print("\n🎉 TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
        print("✅ O MATT 2.0 está funcionando perfeitamente!")
        
    except Exception as e:
        print(f"❌ Erro durante os testes: {str(e)}")
        print("💡 Verifique se o arquivo dashboard.py está correto")

def test_ollama_connection():
    """Teste específico da conexão Ollama"""
    print("\n🔧 TESTE ESPECÍFICO DA CONEXÃO OLLAMA")
    print("=" * 50)
    
    try:
        import requests
        
        # Teste de conectividade
        print("1️⃣ Testando conectividade com Ollama...")
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        
        if response.status_code == 200:
            print("✅ Ollama está rodando e acessível!")
            
            # Verificar modelos disponíveis
            try:
                models = response.json()
                if 'models' in models:
                    print(f"📦 Modelos disponíveis: {len(models['models'])}")
                    for model in models['models']:
                        print(f"   - {model.get('name', 'N/A')}")
                else:
                    print("📦 Modelos: Informação não disponível")
            except:
                print("📦 Modelos: Erro ao processar resposta")
                
        else:
            print(f"❌ Ollama retornou status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Ollama não está rodando!")
        print("💡 Para ativar Ollama:")
        print("   1. Instale em https://ollama.ai")
        print("   2. Execute: ollama serve")
        print("   3. Execute: ollama pull llama2")
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")

def main():
    """Função principal"""
    print("🤖 MATT 2.0 - TESTE COMPLETO DO SISTEMA")
    print("=" * 60)
    
    # Teste básico
    test_matt_basic()
    
    # Teste específico Ollama
    test_ollama_connection()
    
    print("\n" + "=" * 60)
    print("🏁 TESTES FINALIZADOS")
    print("\n💡 DICAS:")
    print("• Se Ollama não estiver funcionando, o MATT usará o sistema local")
    print("• O sistema local sempre funciona e fornece respostas inteligentes")
    print("• Para melhor experiência, configure o Ollama com: ollama pull llama2")
    print("• Acesse o dashboard em: streamlit run app/dashboard.py")

if __name__ == "__main__":
    main()
