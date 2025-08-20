#!/usr/bin/env python3
"""
🖨️ SCRIPT SIMPLES PARA PING DE IMPRESSORAS
============================================

Este script executa ping local para verificar conectividade das impressoras da sua rede.
É um script simples que pode ser executado diretamente no terminal.

COMO USAR:
1. Salve este arquivo na sua máquina
2. Abra o terminal/prompt de comando
3. Navegue até a pasta onde salvou o arquivo
4. Execute: python dashboard_local_impressoras.py

REQUISITOS:
- Python 3.6+
- Acesso à rede local
- Permissões para executar ping

AUTOR: Sistema Finance Vibes
VERSÃO: 1.0
"""

import subprocess
import platform
import time
import json
from datetime import datetime
import os

def print_banner():
    """Exibe banner do sistema"""
    print("=" * 70)
    print("🖨️  SCRIPT DE PING PARA IMPRESSORAS - FINANCE VIBES")
    print("=" * 70)
    print("Sistema simples para verificar conectividade das impressoras")
    print("Execute localmente para ping real da sua rede")
    print("=" * 70)

def get_system_info():
    """Obtém informações do sistema"""
    print("💻 Informações do Sistema:")
    print(f"   Sistema: {platform.system()} {platform.release()}")
    print(f"   Python: {platform.python_version()}")
    print(f"   Arquitetura: {platform.machine()}")
    print()

def execute_ping(ip):
    """Executa ping para um IP específico"""
    try:
        if platform.system().lower() == "windows":
            # Windows
            result = subprocess.run(
                ["ping", "-n", "1", "-w", "1000", ip],
                capture_output=True,
                text=True,
                timeout=5
            )
        else:
            # Linux/Mac
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "1", ip],
                capture_output=True,
                text=True,
                timeout=5
            )
        
        # Verificar se o ping foi bem-sucedido
        if result.returncode == 0:
            # Extrair latência
            output = result.stdout
            if platform.system().lower() == "windows":
                # Windows: time=XXms
                import re
                match = re.search(r'tempo[=<](\d+)ms', output, re.IGNORECASE)
                latency = int(match.group(1)) if match else None
            else:
                # Linux/Mac: time=XX.X ms
                import re
                match = re.search(r'time=(\d+\.?\d*) ms', output)
                latency = float(match.group(1)) if match else None
            
            return {
                "online": True,
                "latency": latency,
                "method": "ping_command",
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "online": False,
                "latency": None,
                "method": "ping_failed",
                "error": result.stderr,
                "timestamp": datetime.now().isoformat()
            }
            
    except subprocess.TimeoutExpired:
        return {
            "online": False,
            "latency": None,
            "method": "timeout",
            "error": "Timeout ao executar ping",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "online": False,
            "latency": None,
            "method": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def get_printer_ips():
    """Obtém lista de IPs das impressoras"""
    print("📋 CONFIGURAÇÃO DAS IMPRESSORAS")
    print("=" * 50)
    
    # Dados de exemplo - MODIFIQUE AQUI COM OS IPs REAIS
    sample_printers = {
        "172.25.61.53": {"local": "Sede", "modelo": "HP LaserJet", "serial": "ABC123"},
        "172.25.61.54": {"local": "Sede", "modelo": "HP LaserJet", "serial": "DEF456"},
        "192.168.1.100": {"local": "Filial", "modelo": "Canon", "serial": "GHI789"},
        "10.0.0.50": {"local": "Escritório", "modelo": "Brother", "serial": "XYZ789"},
    }
    
    print("📊 Impressoras configuradas:")
    for ip, details in sample_printers.items():
        print(f"   • {ip} - {details['local']} - {details['modelo']}")
    
    print()
    print("💡 MODIFIQUE OS IPs ACIMA COM OS ENDEREÇOS REAIS DAS SUAS IMPRESSORAS!")
    print("   Edite o arquivo e altere a variável 'sample_printers'")
    print()
    
    return sample_printers

def run_ping_test(printers):
    """Executa teste de ping para todas as impressoras"""
    print("🚀 INICIANDO TESTE DE PING")
    print("=" * 50)
    
    results = {}
    total = len(printers)
    
    for i, (ip, details) in enumerate(printers.items(), 1):
        print(f"🏓 [{i}/{total}] Pingando {ip}...", end=" ")
        
        # Executar ping
        result = execute_ping(ip)
        results[ip] = result
        
        # Mostrar resultado
        if result["online"]:
            latency = result["latency"] or "N/A"
            print(f"✅ ONLINE ({latency}ms)")
        else:
            error = result.get("error", "Desconhecido")
            print(f"❌ OFFLINE - {error}")
        
        # Pequeno delay
        time.sleep(0.5)
    
    print()
    return results

def show_results(printers, results):
    """Exibe resultados do teste"""
    print("📊 RESULTADOS DO TESTE")
    print("=" * 50)
    
    # Estatísticas
    total = len(results)
    online = sum(1 for r in results.values() if r["online"])
    offline = total - online
    success_rate = (online / total * 100) if total > 0 else 0
    
    print(f"📈 ESTATÍSTICAS:")
    print(f"   Total de impressoras: {total}")
    print(f"   Online: {online} ✅")
    print(f"   Offline: {offline} ❌")
    print(f"   Taxa de sucesso: {success_rate:.1f}%")
    print()
    
    # Detalhes por impressora
    print("🖨️ STATUS DETALHADO:")
    print("-" * 50)
    
    for ip, result in results.items():
        details = printers[ip]
        status_icon = "✅" if result["online"] else "❌"
        status_text = "ONLINE" if result["online"] else "OFFLINE"
        latency_text = f"({result['latency']}ms)" if result["latency"] else ""
        
        print(f"{status_icon} {ip} - {status_text} {latency_text}")
        print(f"   Local: {details['local']}")
        print(f"   Modelo: {details['modelo']}")
        print(f"   Serial: {details['serial']}")
        print(f"   Método: {result['method']}")
        print(f"   Timestamp: {result['timestamp']}")
        
        if result.get('error'):
            print(f"   ❌ Erro: {result['error']}")
        
        print()

def save_results(printers, results):
    """Salva resultados em arquivo JSON"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ping_results_{timestamp}.json"
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {
                "platform": platform.system(),
                "release": platform.release(),
                "python_version": platform.python_version()
            },
            "printers": printers,
            "results": results,
            "summary": {
                "total": len(results),
                "online": sum(1 for r in results.values() if r["online"]),
                "offline": sum(1 for r in results.values() if not r["online"]),
                "success_rate": (sum(1 for r in results.values() if r["online"]) / len(results) * 100) if results else 0
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Resultados salvos em: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Erro ao salvar resultados: {e}")
        return None

def show_instructions():
    """Exibe instruções de uso"""
    print("📖 INSTRUÇÕES DE USO")
    print("=" * 70)
    print("1. 📁 SALVAR:")
    print("   - Salve este arquivo na sua máquina")
    print("   - Use um nome como 'ping_impressoras.py'")
    print()
    print("2. ⚙️ CONFIGURAR:")
    print("   - Abra o arquivo em um editor de texto")
    print("   - Modifique a variável 'sample_printers' com os IPs reais")
    print("   - Salve o arquivo")
    print()
    print("3. 🚀 EXECUTAR:")
    print("   - Abra o terminal/prompt de comando")
    print("   - Navegue até a pasta do arquivo")
    print("   - Execute: python ping_impressoras.py")
    print()
    print("4. 📊 RESULTADOS:")
    print("   - Os resultados aparecerão no terminal")
    print("   - Um arquivo JSON será criado com os dados")
    print()
    print("💡 DICAS:")
    print("   - Execute na máquina que tem acesso à rede das impressoras")
    print("   - Verifique se o firewall permite ping")
    print("   - Para Windows, execute como administrador se necessário")
    print("   - Os resultados são salvos automaticamente")
    print()

def main():
    """Função principal"""
    print_banner()
    get_system_info()
    
    # Mostrar instruções
    show_instructions()
    
    # Perguntar se quer continuar
    print("🎯 Deseja executar o teste de ping agora?")
    response = input("Digite 's' para sim ou Enter para não: ").lower()
    
    if response in ['s', 'sim', 'y', 'yes']:
        print()
        
        # Obter configuração das impressoras
        printers = get_printer_ips()
        
        # Executar teste
        results = run_ping_test(printers)
        
        # Mostrar resultados
        show_results(printers, results)
        
        # Salvar resultados
        filename = save_results(printers, results)
        
        print("🎉 TESTE CONCLUÍDO!")
        print("=" * 50)
        if filename:
            print(f"📁 Resultados salvos em: {filename}")
        print("💡 Use os resultados para verificar a conectividade das impressoras")
        
    else:
        print()
        print("ℹ️ Teste não executado.")
        print("💡 Execute o script quando quiser fazer o teste de ping")
        print("📖 Leia as instruções acima para saber como usar")
    
    print()
    print("=" * 70)
    print("🖨️ Script de Ping para Impressoras - Finance Vibes")
    print("Obrigado por usar nosso sistema!")
    print("=" * 70)

if __name__ == "__main__":
    main()
