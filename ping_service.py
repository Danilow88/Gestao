#!/usr/bin/env python3
"""
Serviço Local de Ping para Impressoras
Roda na máquina do usuário para fazer ping real nas impressoras da rede Nubank
"""

import subprocess
import platform
import time
import json
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading

app = Flask(__name__)
CORS(app)  # Permite acesso do Streamlit Cloud

# Cache de resultados
ping_cache = {}
cache_timestamp = {}
CACHE_DURATION = 30  # segundos

def ping_ip_real(ip_address):
    """Faz ping real no IP - só roda localmente"""
    try:
        system = platform.system().lower()
        
        if system == "windows":
            cmd = ["ping", "-n", "1", "-w", "1000", ip_address]
        else:
            cmd = ["ping", "-c", "1", "-W", "1", ip_address]
        
        result = subprocess.run(cmd, capture_output=True, timeout=3)
        return {
            "ip": ip_address,
            "online": result.returncode == 0,
            "timestamp": datetime.now().isoformat(),
            "response_time": time.time()
        }
    except Exception as e:
        return {
            "ip": ip_address,
            "online": False,
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

def is_cache_valid(ip):
    """Verifica se o cache ainda é válido"""
    if ip not in cache_timestamp:
        return False
    
    elapsed = time.time() - cache_timestamp[ip]
    return elapsed < CACHE_DURATION

@app.route('/ping/<ip>')
def ping_single(ip):
    """Ping em um IP específico"""
    
    # Verificar cache
    if is_cache_valid(ip):
        return jsonify(ping_cache[ip])
    
    # Fazer ping real
    result = ping_ip_real(ip)
    
    # Atualizar cache
    ping_cache[ip] = result
    cache_timestamp[ip] = time.time()
    
    return jsonify(result)

@app.route('/ping/batch', methods=['POST'])
def ping_batch():
    """Ping em múltiplos IPs"""
    data = request.get_json()
    
    if not data or 'ips' not in data:
        return jsonify({"error": "Lista de IPs necessária"}), 400
    
    ips = data['ips']
    results = {}
    
    for ip in ips:
        # Verificar cache primeiro
        if is_cache_valid(ip):
            results[ip] = ping_cache[ip]
        else:
            # Fazer ping real
            result = ping_ip_real(ip)
            
            # Atualizar cache
            ping_cache[ip] = result
            cache_timestamp[ip] = time.time()
            
            results[ip] = result
    
    return jsonify({
        "results": results,
        "total": len(results),
        "online_count": sum(1 for r in results.values() if r['online']),
        "cache_info": f"Cache válido por {CACHE_DURATION}s"
    })

@app.route('/status')
def status():
    """Status do serviço"""
    return jsonify({
        "service": "Ping Service Local",
        "status": "running",
        "cache_size": len(ping_cache),
        "platform": platform.system(),
        "uptime": time.time() - start_time,
        "cache_duration": CACHE_DURATION
    })

@app.route('/clear-cache')
def clear_cache():
    """Limpa o cache"""
    global ping_cache, cache_timestamp
    ping_cache.clear()
    cache_timestamp.clear()
    
    return jsonify({
        "message": "Cache limpo com sucesso",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    start_time = time.time()
    
    print("🏢 Iniciando Serviço Local de Ping para Impressoras Nubank")
    print("=" * 60)
    print("📍 Serviço: http://localhost:5000")
    print("📊 Status: http://localhost:5000/status")
    print("🔄 Limpar Cache: http://localhost:5000/clear-cache")
    print("=" * 60)
    print("💡 Mantenha este serviço rodando para ping real das impressoras")
    print("🌐 O Streamlit Cloud irá se conectar neste serviço")
    print("=" * 60)
    
    # Rodar em thread separada para não bloquear
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
