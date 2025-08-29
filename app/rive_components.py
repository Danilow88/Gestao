"""
Componentes Rive para o Dashboard Finance-Vibes
Integra animações interativas para melhorar a experiência visual
"""

import streamlit as st
import streamlit.components.v1 as components
import os
from pathlib import Path

def create_rive_loading_animation():
    """Cria uma animação de loading Rive para o dashboard"""
    
    rive_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://unpkg.com/@rive-app/canvas@2.31.2/dist/index.js"></script>
        <style>
            .rive-container {
                width: 100%;
                height: 200px;
                display: flex;
                justify-content: center;
                align-items: center;
                background: transparent;
            }
            .rive-canvas {
                border-radius: 10px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            }
        </style>
    </head>
    <body>
        <div class="rive-container">
            <canvas id="rive-canvas" class="rive-canvas" width="300" height="200"></canvas>
        </div>
        
        <script>
            const { Rive } = window.rive;
            
            const rive = new Rive({
                src: 'https://cdn.rive.app/animations/loading.riv',
                canvas: document.getElementById('rive-canvas'),
                autoplay: true,
                loop: true,
                onLoad: () => {
                    console.log('Rive loading animation loaded!');
                },
                onError: (error) => {
                    console.error('Rive error:', error);
                }
            });
        </script>
    </body>
    </html>
    """
    
    return components.html(rive_html, height=200)

def create_rive_success_animation():
    """Cria uma animação de sucesso Rive"""
    
    rive_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://unpkg.com/@rive-app/canvas@2.31.2/dist/index.js"></script>
        <style>
            .rive-container {
                width: 100%;
                height: 150px;
                display: flex;
                justify-content: center;
                align-items: center;
                background: transparent;
            }
            .rive-canvas {
                border-radius: 10px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            }
        </style>
    </head>
    <body>
        <div class="rive-container">
            <canvas id="rive-canvas" class="rive-canvas" width="200" height="150"></canvas>
        </div>
        
        <script>
            const { Rive } = window.rive;
            
            const rive = new Rive({
                src: 'https://cdn.rive.app/animations/success.riv',
                canvas: document.getElementById('rive-canvas'),
                autoplay: false,
                loop: false,
                onLoad: () => {
                    console.log('Rive success animation loaded!');
                },
                onError: (error) => {
                    console.error('Rive error:', error);
                }
            });
            
            // Função para reproduzir a animação
            window.playSuccessAnimation = function() {
                rive.play();
            };
        </script>
    </body>
    </html>
    """
    
    return components.html(rive_html, height=150)

def create_rive_metric_card(title, value, delta, icon="■", animation_type="loading"):
    """Cria um card de métrica com animação Rive"""
    
    if animation_type == "loading":
        rive_component = create_rive_loading_animation()
    elif animation_type == "success":
        rive_component = create_rive_success_animation()
    else:
        rive_component = create_rive_loading_animation()
    
    with st.container():
        st.markdown(f"""
        <div class="metric-card-with-rive">
            <div class="metric-header">
                <div class="metric-icon">{icon}</div>
                <div class="metric-title">{title}</div>
            </div>
            <div class="metric-value">{value}</div>
            <div class="metric-delta {'positive' if delta.startswith('+') else 'negative'}">{delta}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Componente Rive abaixo do card
        rive_component

def create_rive_chart_enhancement(chart_type="pie"):
    """Cria um componente Rive para melhorar gráficos"""
    
    if chart_type == "pie":
        rive_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://unpkg.com/@rive-app/canvas@2.31.2/dist/index.js"></script>
            <style>
                .rive-chart-enhancement {
                    width: 100%;
                    height: 100px;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 10px;
                    margin: 10px 0;
                }
                .rive-canvas {
                    border-radius: 8px;
                }
            </style>
        </head>
        <body>
            <div class="rive-chart-enhancement">
                <canvas id="rive-canvas" class="rive-canvas" width="200" height="80"></canvas>
            </div>
            
            <script>
                const { Rive } = window.rive;
                
                const rive = new Rive({
                    src: 'https://cdn.rive.app/animations/icon.riv',
                    canvas: document.getElementById('rive-canvas'),
                    autoplay: true,
                    loop: true,
                    onLoad: () => {
                        console.log('Rive chart enhancement loaded!');
                    },
                    onError: (error) => {
                        console.error('Rive error:', error);
                    }
                });
            </script>
        </body>
        </html>
        """
    else:
        rive_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://unpkg.com/@rive-app/canvas@2.31.2/dist/index.js"></script>
            <style>
                .rive-chart-enhancement {
                    width: 100%;
                    height: 100px;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    background: linear-gradient(135deg, #06B6D4 0%, #3B82F6 100%);
                    border-radius: 10px;
                    margin: 10px 0;
                }
                .rive-canvas {
                    border-radius: 8px;
                }
            </style>
        </head>
        <body>
            <div class="rive-chart-enhancement">
                <canvas id="rive-canvas" class="rive-canvas" width="200" height="80"></canvas>
            </div>
            
            <script>
                const { Rive } = window.rive;
                
                const rive = new Rive({
                    src: 'https://cdn.rive.app/animations/button.riv',
                    canvas: document.getElementById('rive-canvas'),
                    autoplay: true,
                    loop: true,
                    onLoad: () => {
                        console.log('Rive chart enhancement loaded!');
                    },
                    onError: (error) => {
                        console.error('Rive error:', error);
                    }
                });
            </script>
        </body>
        </html>
        """
    
    return components.html(rive_html, height=100)

def create_rive_navigation_indicator(current_page):
    """Cria um indicador de navegação animado com Rive"""
    
    rive_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://unpkg.com/@rive-app/canvas@2.31.2/dist/index.js"></script>
        <style>
            .rive-nav-indicator {{
                width: 100%;
                height: 60px;
                display: flex;
                justify-content: center;
                align-items: center;
                background: rgba(147, 51, 234, 0.1);
                border-radius: 10px;
                border: 2px solid rgba(147, 51, 234, 0.3);
                margin: 10px 0;
            }}
            .rive-canvas {{
                border-radius: 8px;
            }}
            .nav-text {{
                color: #9333EA;
                font-weight: bold;
                margin-left: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="rive-nav-indicator">
            <canvas id="rive-canvas" class="rive-canvas" width="40" height="40"></canvas>
            <div class="nav-text">Página Atual: {current_page.title()}</div>
        </div>
        
        <script>
            const {{ Rive }} = window.rive;
            
            const rive = new Rive({{
                src: 'https://cdn.rive.app/animations/icon.riv',
                canvas: document.getElementById('rive-canvas'),
                autoplay: true,
                loop: true,
                onLoad: () => {{
                    console.log('Rive navigation indicator loaded!');
                }},
                onError: (error) => {{
                    console.error('Rive error:', error);
                }}
            }});
        </script>
    </body>
    </html>
    """
    
    return components.html(rive_html, height=60)

def create_rive_data_flow_animation():
    """Cria uma animação de fluxo de dados para o dashboard"""
    
    rive_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://unpkg.com/@rive-app/canvas@2.31.2/dist/index.js"></script>
        <style>
            .rive-data-flow {
                width: 100%;
                height: 120px;
                display: flex;
                justify-content: center;
                align-items: center;
                background: transparent;
                border-radius: 15px;
                margin: 15px 0;
                border: 2px solid rgba(139, 92, 246, 0.3);
                box-shadow: 0 8px 25px rgba(139, 92, 246, 0.2);
            }
            .rive-canvas {
                border-radius: 10px;
            }
            .flow-text {
                color: #9333EA;
                font-weight: bold;
                margin-left: 15px;
                font-size: 1.1rem;
            }
        </style>
    </head>
    <body>
        <div class="rive-data-flow">
            <canvas id="rive-canvas" class="rive-canvas" width="80" height="80"></canvas>
            <div class="flow-text">Fluxo de Dados Ativo</div>
        </div>
        
        <script>
            const { Rive } = window.rive;
            
            const rive = new Rive({
                src: 'https://cdn.rive.app/animations/loading.riv',
                canvas: document.getElementById('rive-canvas'),
                autoplay: true,
                loop: true,
                onLoad: () => {
                    console.log('Rive data flow animation loaded!');
                },
                onError: (error) => {
                    console.error('Rive error:', error);
                }
            });
        </script>
    </body>
    </html>
    """
    
    return components.html(rive_html, height=120)

def create_rive_interactive_widget(widget_type="button"):
    """Cria um widget interativo com Rive"""
    
    if widget_type == "button":
        rive_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://unpkg.com/@rive-app/canvas@2.31.2/dist/index.js"></script>
            <style>
                .rive-interactive-widget {
                    width: 100%;
                    height: 80px;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    background: rgba(59, 130, 246, 0.1);
                    border-radius: 10px;
                    border: 2px solid rgba(59, 130, 246, 0.3);
                    cursor: pointer;
                    transition: all 0.3s ease;
                }
                .rive-interactive-widget:hover {
                    background: rgba(59, 130, 246, 0.2);
                    transform: translateY(-2px);
                    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
                }
                .rive-canvas {
                    border-radius: 8px;
                }
                .widget-text {
                    color: #3B82F6;
                    font-weight: bold;
                    margin-left: 10px;
                }
            </style>
        </head>
        <body>
            <div class="rive-interactive-widget" onclick="interactWithWidget()">
                <canvas id="rive-canvas" class="rive-canvas" width="50" height="50"></canvas>
                <div class="widget-text">Clique para Interagir</div>
            </div>
            
            <script>
                const { Rive } = window.rive;
                
                const rive = new Rive({
                    src: 'https://cdn.rive.app/animations/button.riv',
                    canvas: document.getElementById('rive-canvas'),
                    autoplay: false,
                    loop: false,
                    onLoad: () => {
                        console.log('Rive interactive widget loaded!');
                    },
                    onError: (error) => {
                        console.error('Rive error:', error);
                    }
                });
                
                function interactWithWidget() {
                    rive.play();
                    // Adicionar lógica de interação aqui
                    console.log('Widget clicked!');
                }
            </script>
        </body>
        </html>
        """
    
    return components.html(rive_html, height=80)

# Função principal para aplicar estilos Rive
def apply_rive_styles():
    """Aplica estilos CSS para componentes Rive"""
    
    st.markdown("""
    <style>
    .metric-card-with-rive {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    
    .metric-card-with-rive:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
    }
    
    .metric-header {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .metric-icon {
        font-size: 1.5rem;
        margin-right: 0.5rem;
        color: #9333EA;
    }
    
    .metric-title {
        font-size: 1rem;
        color: #666;
        font-weight: 500;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #333;
        margin-bottom: 0.5rem;
    }
    
    .metric-delta {
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .metric-delta.positive {
        color: #10B981;
    }
    
    .metric-delta.negative {
        color: #EF4444;
    }
    </style>
    """, unsafe_allow_html=True)
