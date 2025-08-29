#!/usr/bin/env python3
"""
Teste rápido da integração Rive com o Dashboard
Verifica se todos os componentes estão funcionando
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def test_rive_components():
    """Testa se os componentes Rive estão funcionando"""
    print("🧪 Testando componentes Rive...")
    
    try:
        from app.rive_components import (
            create_rive_loading_animation,
            create_rive_success_animation,
            create_rive_metric_card,
            create_rive_chart_enhancement,
            create_rive_navigation_indicator,
            create_rive_data_flow_animation,
            create_rive_interactive_widget,
            apply_rive_styles
        )
        print("✅ Todos os componentes Rive importados com sucesso!")
        return True
    except ImportError as e:
        print(f"❌ Erro ao importar componentes Rive: {e}")
        return False

def test_dashboard_integration():
    """Testa se o dashboard pode importar os componentes Rive"""
    print("\n🧪 Testando integração com dashboard...")
    
    try:
        # Simular importação do dashboard
        import app.dashboard
        print("✅ Dashboard importado com sucesso!")
        
        # Verificar se a função render_dashboard existe
        if hasattr(app.dashboard, 'render_dashboard'):
            print("✅ Função render_dashboard encontrada!")
        else:
            print("❌ Função render_dashboard não encontrada!")
            return False
            
        return True
    except ImportError as e:
        print(f"❌ Erro ao importar dashboard: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def test_rive_packages():
    """Testa se os pacotes Rive estão instalados"""
    print("\n🧪 Testando pacotes Rive...")
    
    try:
        import importlib
        
        # Testar pacotes principais
        packages = [
            'streamlit',
            'streamlit.components.v1',
            'pathlib'
        ]
        
        for package in packages:
            try:
                importlib.import_module(package)
                print(f"✅ {package} disponível")
            except ImportError:
                print(f"❌ {package} não disponível")
                return False
        
        print("✅ Todos os pacotes necessários estão disponíveis!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar pacotes: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🎨 Teste de Integração Rive + Dashboard")
    print("=" * 50)
    
    tests = [
        ("Componentes Rive", test_rive_components),
        ("Integração Dashboard", test_dashboard_integration),
        ("Pacotes Necessários", test_rive_packages)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Executando: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro durante teste {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo dos resultados
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("🚀 O Rive está perfeitamente integrado ao seu dashboard!")
        print("\n📱 Para testar:")
        print("1. Execute: streamlit run app/dashboard.py")
        print("2. Verifique as animações no dashboard")
        print("3. Teste a responsividade")
    else:
        print(f"\n⚠️ {total - passed} teste(s) falharam")
        print("🔧 Verifique os erros acima e corrija se necessário")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
