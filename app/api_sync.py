import streamlit as st
import json
import pandas as pd
from datetime import datetime
import os
from pathlib import Path

# Configuração da API
API_VERSION = "1.0"
SYNC_DATA_FILE = "sync_data.json"

def init_sync_data():
    """Inicializa dados de sincronização"""
    if not os.path.exists(SYNC_DATA_FILE):
        default_data = {
            "version": API_VERSION,
            "last_sync": None,
            "local_dashboards": {},
            "ping_results": {},
            "printer_details": {},
            "sync_status": "waiting"
        }
        
        with open(SYNC_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, indent=2, ensure_ascii=False)
        
        return default_data
    
    with open(SYNC_DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_sync_data(data):
    """Salva dados de sincronização"""
    with open(SYNC_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def update_sync_status(status):
    """Atualiza status de sincronização"""
    data = init_sync_data()
    data["sync_status"] = status
    data["last_sync"] = datetime.now().isoformat()
    save_sync_data(data)

def receive_ping_results(results_data):
    """Recebe resultados de ping do dashboard local"""
    try:
        data = init_sync_data()
        
        # Atualizar dados
        data["ping_results"] = results_data.get("results", {})
        data["printer_details"] = results_data.get("printer_details", {})
        data["last_sync"] = datetime.now().isoformat()
        data["sync_status"] = "synced"
        
        # Adicionar informações do dashboard local
        local_dashboard_info = {
            "timestamp": results_data.get("timestamp"),
            "source": results_data.get("source"),
            "version": results_data.get("version")
        }
        
        data["local_dashboards"][datetime.now().isoformat()] = local_dashboard_info
        
        # Salvar dados
        save_sync_data(data)
        
        return True, "✅ Dados sincronizados com sucesso!"
        
    except Exception as e:
        return False, f"❌ Erro na sincronização: {str(e)}"

def get_sync_status():
    """Retorna status atual da sincronização"""
    try:
        data = init_sync_data()
        return data
    except Exception as e:
        return {"error": str(e)}

def get_ping_results():
    """Retorna resultados de ping sincronizados"""
    try:
        data = init_sync_data()
        return data.get("ping_results", {})
    except Exception as e:
        return {}

def get_printer_details():
    """Retorna detalhes das impressoras sincronizados"""
    try:
        data = init_sync_data()
        return data.get("printer_details", {})
    except Exception as e:
        return {}

def clear_sync_data():
    """Limpa dados de sincronização"""
    try:
        if os.path.exists(SYNC_DATA_FILE):
            os.remove(SYNC_DATA_FILE)
        return True, "✅ Dados de sincronização limpos!"
    except Exception as e:
        return False, f"❌ Erro ao limpar dados: {str(e)}"

def export_sync_data():
    """Exporta dados de sincronização"""
    try:
        data = init_sync_data()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sync_export_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True, f"✅ Dados exportados para: {filename}"
        
    except Exception as e:
        return False, f"❌ Erro ao exportar: {str(e)}"

# Interface da API
def render_api_interface():
    """Renderiza interface da API de sincronização"""
    st.header("🔌 API de Sincronização")
    st.markdown("**Interface para sincronização com dashboard local**")
    
    # Status atual
    st.subheader("📊 Status Atual")
    
    try:
        sync_data = get_sync_status()
        
        if "error" in sync_data:
            st.error(f"❌ Erro ao carregar status: {sync_data['error']}")
        else:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                status = sync_data.get("sync_status", "unknown")
                if status == "synced":
                    st.success("🟢 Sincronizado")
                elif status == "waiting":
                    st.warning("🟡 Aguardando")
                else:
                    st.error("🔴 Desconectado")
                
                st.metric("Status", status.title())
            
            with col2:
                last_sync = sync_data.get("last_sync")
                if last_sync:
                    st.metric("Última Sincronização", "Sim")
                    st.caption(f"📅 {last_sync}")
                else:
                    st.metric("Última Sincronização", "Nunca")
            
            with col3:
                ping_count = len(sync_data.get("ping_results", {}))
                st.metric("Resultados de Ping", ping_count)
            
            # Detalhes da sincronização
            with st.expander("📋 Detalhes da Sincronização", expanded=False):
                st.json(sync_data)
    
    except Exception as e:
        st.error(f"❌ Erro: {str(e)}")
    
    # Controles da API
    st.subheader("🎛️ Controles da API")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Atualizar Status", use_container_width=True):
            st.rerun()
    
    with col2:
        if st.button("🧹 Limpar Dados", use_container_width=True):
            success, message = clear_sync_data()
            if success:
                st.success(message)
            else:
                st.error(message)
            st.rerun()
    
    with col3:
        if st.button("📤 Exportar Dados", use_container_width=True):
            success, message = export_sync_data()
            if success:
                st.success(message)
            else:
                st.error(message)
    
    # Simulação de recebimento de dados
    st.subheader("🧪 Simular Recebimento de Dados")
    
    if st.button("📥 Simular Dados do Dashboard Local"):
        # Dados simulados
        simulated_data = {
            "timestamp": datetime.now().isoformat(),
            "results": {
                "172.25.61.53": {
                    "online": True,
                    "latency": 15,
                    "method": "ping_command",
                    "timestamp": datetime.now().isoformat()
                },
                "172.25.61.54": {
                    "online": False,
                    "latency": None,
                    "method": "ping_failed",
                    "error": "Host unreachable",
                    "timestamp": datetime.now().isoformat()
                }
            },
            "printer_details": {
                "172.25.61.53": {
                    "local": "Sede",
                    "modelo": "HP LaserJet",
                    "serial": "ABC123",
                    "status_manual": "Ativo"
                },
                "172.25.61.54": {
                    "local": "Sede",
                    "modelo": "HP LaserJet",
                    "serial": "DEF456",
                    "status_manual": "Ativo"
                }
            },
            "source": "local_dashboard",
            "version": "1.0"
        }
        
        success, message = receive_ping_results(simulated_data)
        if success:
            st.success(message)
            st.info("🔄 Atualizando interface...")
            st.rerun()
        else:
            st.error(message)
    
    # Resultados sincronizados
    st.subheader("📊 Resultados Sincronizados")
    
    ping_results = get_ping_results()
    printer_details = get_printer_details()
    
    if ping_results and printer_details:
        # Estatísticas
        total = len(ping_results)
        online = sum(1 for r in ping_results.values() if r.get("online"))
        offline = total - online
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total", total)
        with col2:
            st.metric("Online", online, delta=f"+{online}")
        with col3:
            st.metric("Offline", offline, delta=f"-{offline}")
        with col4:
            success_rate = (online / total * 100) if total > 0 else 0
            st.metric("Taxa de Sucesso", f"{success_rate:.1f}%")
        
        # Detalhes das impressoras
        st.subheader("🖨️ Status das Impressoras")
        
        for ip, result in ping_results.items():
            details = printer_details.get(ip, {})
            status_icon = "✅" if result.get("online") else "❌"
            status_text = "ONLINE" if result.get("online") else "OFFLINE"
            latency_text = f"({result['latency']}ms)" if result.get("latency") else ""
            
            with st.expander(f"{status_icon} {ip} - {status_text} {latency_text}", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Local:** {details.get('local', 'N/A')}")
                    st.write(f"**Modelo:** {details.get('modelo', 'N/A')}")
                    st.write(f"**Serial:** {details.get('serial', 'N/A')}")
                
                with col2:
                    st.write(f"**Status:** {status_text}")
                    st.write(f"**Método:** {result.get('method', 'N/A')}")
                    st.write(f"**Timestamp:** {result.get('timestamp', 'N/A')}")
                    
                    if result.get('error'):
                        st.error(f"**Erro:** {result['error']}")
                
                # Barra de status visual
                if result.get("online"):
                    st.progress(1.0, text="🟢 Online")
                else:
                    st.progress(0.0, text="🔴 Offline")
        
        # Tabela resumo
        st.subheader("📋 Resumo em Tabela")
        
        summary_data = []
        for ip, result in ping_results.items():
            details = printer_details.get(ip, {})
            summary_data.append({
                "IP": ip,
                "Local": details.get('local', 'N/A'),
                "Modelo": details.get('modelo', 'N/A'),
                "Status": "ONLINE" if result.get("online") else "OFFLINE",
                "Latência": f"{result['latency']}ms" if result.get("latency") else "N/A",
                "Método": result.get('method', 'N/A'),
                "Timestamp": result.get('timestamp', 'N/A')
            })
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)
        
    else:
        st.info("📋 Nenhum resultado sincronizado disponível")
        st.info("💡 Execute o dashboard local para sincronizar dados")

# Função principal
def main():
    """Função principal da API de sincronização"""
    st.set_page_config(
        page_title="🔌 API de Sincronização",
        page_icon="🔌",
        layout="wide"
    )
    
    st.title("🔌 API de Sincronização")
    st.markdown("**Interface para sincronização entre dashboard local e nuvem**")
    
    render_api_interface()
    
    # Informações da API
    st.sidebar.header("ℹ️ Informações da API")
    st.sidebar.write(f"**Versão:** {API_VERSION}")
    st.sidebar.write(f"**Arquivo de dados:** {SYNC_DATA_FILE}")
    
    st.sidebar.header("📖 Como Usar")
    st.sidebar.markdown("""
    1. **Configure** o dashboard local
    2. **Execute** o ping local
    3. **Sincronize** automaticamente
    4. **Visualize** resultados aqui
    
    **💡 Dica:** Use esta API para receber dados do dashboard local!
    """)

if __name__ == "__main__":
    main()
