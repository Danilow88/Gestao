"""
Editor Visual Rive para Finance-Vibes
Permite editar e personalizar animações diretamente no dashboard
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import os
from pathlib import Path
import uuid

class RiveVisualEditor:
    def __init__(self):
        self.editor_config = self.load_editor_config()
        self.animations = self.load_animations()
    
    def load_editor_config(self):
        """Carrega configuração do editor"""
        return {
            'theme_colors': {
                'primary': '#9333EA',
                'secondary': '#06B6D4',
                'success': '#10B981',
                'warning': '#F59E0B',
                'error': '#EF4444',
                'background': '#1F2937',
                'text': '#FFFFFF'
            },
            'animation_types': [
                'loading', 'success', 'error', 'hover', 'click', 'entrance', 'exit'
            ],
            'easing_functions': [
                'linear', 'ease-in', 'ease-out', 'ease-in-out', 'bounce'
            ],
            'default_duration': 1.0,
            'default_fps': 60
        }
    
    def load_animations(self):
        """Carrega animações existentes"""
        return {
            'metric_card': {
                'type': 'entrance',
                'duration': 0.5,
                'easing': 'ease-out',
                'properties': ['scale', 'opacity', 'y']
            },
            'loading_spinner': {
                'type': 'loading',
                'duration': 2.0,
                'easing': 'linear',
                'properties': ['rotation'],
                'loop': True
            },
            'success_check': {
                'type': 'success',
                'duration': 0.8,
                'easing': 'ease-out',
                'properties': ['scale', 'opacity']
            }
        }
    
    def render_editor_interface(self):
        """Renderiza a interface principal do editor"""
        st.markdown("""
        <div style="text-align: center; margin: 2rem 0;">
            <h1 style="color: #9333EA; font-size: 2.5rem;">🎨 Editor Visual Rive</h1>
            <p style="color: #666; font-size: 1.2rem;">Personalize as animações do seu app Finance-Vibes</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Tabs para diferentes seções
        tab1, tab2, tab3, tab4 = st.tabs([
            "🎭 Editor de Animações", 
            "🎨 Personalização de Tema", 
            "📱 Preview em Tempo Real",
            "💾 Gerenciamento"
        ])
        
        with tab1:
            self.render_animation_editor()
        
        with tab2:
            self.render_theme_customization()
        
        with tab3:
            self.render_live_preview()
        
        with tab4:
            self.render_management()
    
    def render_animation_editor(self):
        """Editor de animações"""
        st.subheader("🎭 Editor de Animações")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### Elementos Disponíveis")
            
            # Seleção de elemento
            selected_element = st.selectbox(
                "Escolha o elemento para animar:",
                list(self.animations.keys()),
                format_func=lambda x: x.replace('_', ' ').title()
            )
            
            if selected_element:
                animation = self.animations[selected_element]
                
                st.markdown("#### Configurações Atuais")
                st.json(animation)
                
                # Editor de propriedades
                st.markdown("#### Editar Propriedades")
                
                # Tipo de animação
                new_type = st.selectbox(
                    "Tipo de animação:",
                    self.editor_config['animation_types'],
                    index=self.editor_config['animation_types'].index(animation.get('type', 'entrance'))
                )
                
                # Duração
                new_duration = st.slider(
                    "Duração (segundos):",
                    min_value=0.1,
                    max_value=5.0,
                    value=animation.get('duration', 1.0),
                    step=0.1
                )
                
                # Easing
                new_easing = st.selectbox(
                    "Função de easing:",
                    self.editor_config['easing_functions'],
                    index=self.editor_config['easing_functions'].index(animation.get('easing', 'ease-out'))
                )
                
                # Loop
                new_loop = st.checkbox(
                    "Loop infinito",
                    value=animation.get('loop', False)
                )
                
                # Propriedades
                available_properties = ['scale', 'opacity', 'rotation', 'x', 'y', 'color']
                selected_properties = st.multiselect(
                    "Propriedades a animar:",
                    available_properties,
                    default=animation.get('properties', [])
                )
                
                # Botão de aplicação
                if st.button("💾 Aplicar Mudanças", type="primary"):
                    self.update_animation(selected_element, {
                        'type': new_type,
                        'duration': new_duration,
                        'easing': new_easing,
                        'loop': new_loop,
                        'properties': selected_properties
                    })
                    st.success("✅ Animação atualizada com sucesso!")
        
        with col2:
            st.markdown("### Preview da Animação")
            
            # Canvas para preview
            preview_canvas = self.create_preview_canvas(selected_element if 'selected_element' in locals() else 'metric_card')
            st.components.v1.html(preview_canvas, height=300)
            
            # Controles de preview
            st.markdown("#### Controles de Preview")
            
            col_preview1, col_preview2, col_preview3 = st.columns(3)
            
            with col_preview1:
                if st.button("▶️ Play"):
                    st.info("🎬 Reproduzindo animação...")
            
            with col_preview2:
                if st.button("⏸️ Pause"):
                    st.info("⏸️ Animação pausada")
            
            with col_preview3:
                if st.button("⏹️ Stop"):
                    st.info("⏹️ Animação parada")
            
            # Configurações de preview
            st.markdown("#### Configurações de Preview")
            
            preview_fps = st.slider("FPS:", 30, 120, 60)
            preview_scale = st.slider("Escala:", 0.5, 2.0, 1.0, 0.1)
            
            st.info(f"🎯 Preview configurado: {preview_fps} FPS, Escala: {preview_scale}x")
    
    def render_theme_customization(self):
        """Personalização de tema"""
        st.subheader("🎨 Personalização de Tema")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### Cores do Tema")
            
            # Editor de cores
            new_colors = {}
            for color_name, current_color in self.editor_config['theme_colors'].items():
                new_colors[color_name] = st.color_picker(
                    f"{color_name.replace('_', ' ').title()}:",
                    current_color,
                    key=f"color_{color_name}"
                )
            
            # Aplicar mudanças de cor
            if st.button("🎨 Aplicar Novas Cores", type="primary"):
                self.editor_config['theme_colors'] = new_colors
                st.success("✅ Cores atualizadas com sucesso!")
        
        with col2:
            st.markdown("### Paleta de Cores Atual")
            
            # Visualização da paleta
            color_palette = ""
            for color_name, color_value in self.editor_config['theme_colors'].items():
                color_palette += f"""
                <div style="display: flex; align-items: center; margin: 10px 0;">
                    <div style="width: 30px; height: 30px; background-color: {color_value}; border-radius: 5px; margin-right: 10px;"></div>
                    <span style="color: #333; font-weight: bold;">{color_name.replace('_', ' ').title()}</span>
                    <span style="color: #666; margin-left: 10px;">{color_value}</span>
                </div>
                """
            
            st.markdown(f"""
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px;">
                {color_palette}
            </div>
            """, unsafe_allow_html=True)
        
        # Configurações avançadas
        st.markdown("### ⚙️ Configurações Avançadas")
        
        col_adv1, col_adv2, col_adv3 = st.columns(3)
        
        with col_adv1:
            new_fps = st.number_input(
                "FPS Padrão:",
                min_value=24,
                max_value=120,
                value=self.editor_config['default_fps']
            )
        
        with col_adv2:
            new_duration = st.number_input(
                "Duração Padrão (s):",
                min_value=0.1,
                max_value=10.0,
                value=self.editor_config['default_duration'],
                step=0.1
            )
        
        with col_adv3:
            st.markdown("#### Acessibilidade")
            reduce_motion = st.checkbox("Suporte a reduce-motion")
            high_contrast = st.checkbox("Modo alto contraste")
        
        if st.button("⚙️ Aplicar Configurações Avançadas", type="primary"):
            self.editor_config['default_fps'] = new_fps
            self.editor_config['default_duration'] = new_duration
            st.success("✅ Configurações avançadas aplicadas!")
    
    def render_live_preview(self):
        """Preview em tempo real"""
        st.subheader("📱 Preview em Tempo Real")
        
        # Seleção de cena
        scene_options = ["Dashboard Principal", "Cards de Métricas", "Gráficos", "Navegação"]
        selected_scene = st.selectbox("Escolha a cena para preview:", scene_options)
        
        # Canvas de preview
        preview_html = self.create_scene_preview(selected_scene)
        st.components.v1.html(preview_html, height=400)
        
        # Controles de preview
        st.markdown("#### 🎮 Controles de Preview")
        
        col_control1, col_control2, col_control3, col_control4 = st.columns(4)
        
        with col_control1:
            if st.button("🔄 Reset"):
                st.info("🔄 Cena resetada")
        
        with col_control2:
            if st.button("⏭️ Próxima Cena"):
                st.info("⏭️ Carregando próxima cena...")
        
        with col_control3:
            if st.button("📱 Mobile View"):
                st.info("📱 Modo mobile ativado")
        
        with col_control4:
            if st.button("💻 Desktop View"):
                st.info("💻 Modo desktop ativado")
        
        # Configurações de preview
        st.markdown("#### ⚙️ Configurações de Preview")
        
        col_config1, col_config2, col_config3 = st.columns(3)
        
        with col_config1:
            preview_quality = st.selectbox("Qualidade:", ["Baixa", "Média", "Alta"])
        
        with col_config2:
            preview_theme = st.selectbox("Tema:", ["Claro", "Escuro", "Auto"])
        
        with col_config3:
            preview_language = st.selectbox("Idioma:", ["Português", "English", "Español"])
        
        st.info(f"🎯 Preview configurado: {preview_quality} qualidade, Tema {preview_theme}, {preview_language}")
    
    def render_management(self):
        """Gerenciamento de animações"""
        st.subheader("💾 Gerenciamento")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("### 📁 Salvar/Carregar")
            
            # Nome do projeto
            project_name = st.text_input("Nome do projeto:", "Finance-Vibes-Theme")
            
            # Salvar projeto
            if st.button("💾 Salvar Projeto", type="primary"):
                self.save_project(project_name)
                st.success(f"✅ Projeto '{project_name}' salvo com sucesso!")
            
            # Carregar projeto
            uploaded_file = st.file_uploader("Carregar projeto (.json):", type=['json'])
            if uploaded_file is not None:
                if st.button("📂 Carregar Projeto"):
                    self.load_project(uploaded_file)
                    st.success("✅ Projeto carregado com sucesso!")
        
        with col2:
            st.markdown("### 🔄 Importar/Exportar")
            
            # Exportar configuração
            if st.button("📤 Exportar Configuração"):
                config_data = self.export_configuration()
                st.download_button(
                    label="💾 Baixar Configuração",
                    data=json.dumps(config_data, indent=2),
                    file_name=f"{project_name}_config.json",
                    mime="application/json"
                )
            
            # Exportar para Rive
            if st.button("🎨 Exportar para Rive"):
                rive_data = self.export_to_rive()
                st.download_button(
                    label="🎨 Baixar Arquivo Rive",
                    data=rive_data,
                    file_name=f"{project_name}.riv",
                    mime="application/octet-stream"
                )
        
        # Lista de projetos salvos
        st.markdown("### 📋 Projetos Salvos")
        
        saved_projects = self.get_saved_projects()
        if saved_projects:
            for project in saved_projects:
                col_project1, col_project2, col_project3 = st.columns([3, 1, 1])
                
                with col_project1:
                    st.markdown(f"**{project['name']}** - {project['date']}")
                
                with col_project2:
                    if st.button(f"📂 Carregar", key=f"load_{project['id']}"):
                        self.load_project_by_id(project['id'])
                        st.success(f"✅ Projeto '{project['name']}' carregado!")
                
                with col_project3:
                    if st.button(f"🗑️ Excluir", key=f"delete_{project['id']}"):
                        self.delete_project(project['id'])
                        st.success(f"🗑️ Projeto '{project['name']}' excluído!")
                        st.rerun()
        else:
            st.info("📁 Nenhum projeto salvo ainda")
        
        # Backup e restauração
        st.markdown("### 🔒 Backup e Restauração")
        
        col_backup1, col_backup2 = st.columns(2)
        
        with col_backup1:
            if st.button("💾 Criar Backup"):
                backup_data = self.create_backup()
                st.download_button(
                    label="💾 Baixar Backup",
                    data=json.dumps(backup_data, indent=2),
                    file_name=f"{project_name}_backup_{self.get_timestamp()}.json",
                    mime="application/json"
                )
        
        with col_backup2:
            backup_file = st.file_uploader("Restaurar backup:", type=['json'])
            if backup_file is not None:
                if st.button("🔄 Restaurar Backup"):
                    self.restore_backup(backup_file)
                    st.success("✅ Backup restaurado com sucesso!")
    
    def create_preview_canvas(self, element_name):
        """Cria canvas de preview para um elemento"""
        animation = self.animations.get(element_name, {})
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://unpkg.com/@rive-app/canvas@2.31.2/dist/index.js"></script>
            <style>
                .preview-container {{
                    width: 100%;
                    height: 300px;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                    border-radius: 15px;
                    border: 2px solid #dee2e6;
                }}
                .preview-canvas {{
                    border-radius: 10px;
                    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
                }}
                .preview-info {{
                    position: absolute;
                    top: 10px;
                    left: 10px;
                    background: rgba(0,0,0,0.8);
                    color: white;
                    padding: 5px 10px;
                    border-radius: 5px;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="preview-container">
                <div class="preview-info">
                    {element_name.replace('_', ' ').title()}
                </div>
                <canvas id="preview-canvas" class="preview-canvas" width="200" height="150"></canvas>
            </div>
            
            <script>
                const {{ Rive }} = window.rive;
                
                // Configuração da animação
                const animationConfig = {{
                    type: '{animation.get('type', 'entrance')}',
                    duration: {animation.get('duration', 1.0)},
                    easing: '{animation.get('easing', 'ease-out')}',
                    loop: {str(animation.get('loop', False)).lower()},
                    properties: {animation.get('properties', [])}
                }};
                
                // Criar animação baseada na configuração
                const canvas = document.getElementById('preview-canvas');
                const ctx = canvas.getContext('2d');
                
                // Simular animação baseada na configuração
                let startTime = Date.now();
                let animationId;
                
                function animate() {{
                    const elapsed = (Date.now() - startTime) / 1000;
                    const progress = Math.min(elapsed / animationConfig.duration, 1);
                    
                    // Aplicar easing
                    let easedProgress = progress;
                    switch(animationConfig.easing) {{
                        case 'ease-out':
                            easedProgress = 1 - Math.pow(1 - progress, 3);
                            break;
                        case 'ease-in':
                            easedProgress = Math.pow(progress, 3);
                            break;
                        case 'ease-in-out':
                            easedProgress = progress < 0.5 ? 
                                2 * Math.pow(progress, 3) : 
                                1 - Math.pow(-2 * progress + 2, 3) / 2;
                            break;
                    }}
                    
                    // Limpar canvas
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    
                    // Desenhar elemento baseado no tipo
                    if (animationConfig.type === 'loading') {{
                        // Loading spinner
                        ctx.save();
                        ctx.translate(100, 75);
                        ctx.rotate(progress * Math.PI * 2);
                        ctx.strokeStyle = '#9333EA';
                        ctx.lineWidth = 4;
                        ctx.beginPath();
                        ctx.arc(0, 0, 30, 0, Math.PI * 1.5);
                        ctx.stroke();
                        ctx.restore();
                    }} else if (animationConfig.type === 'success') {{
                        // Success check
                        ctx.strokeStyle = '#10B981';
                        ctx.lineWidth = 6;
                        ctx.beginPath();
                        ctx.moveTo(50, 75);
                        ctx.lineTo(80, 105);
                        ctx.lineTo(150, 45);
                        ctx.stroke();
                    }} else {{
                        // Default rectangle
                        ctx.fillStyle = '#9333EA';
                        ctx.fillRect(50, 50, 100, 50);
                    }}
                    
                    // Continuar animação se necessário
                    if (progress < 1 || animationConfig.loop) {{
                        animationId = requestAnimationFrame(animate);
                        if (animationConfig.loop && progress >= 1) {{
                            startTime = Date.now();
                        }}
                    }}
                }}
                
                // Iniciar animação
                animate();
                
                // Controles
                window.playPreview = function() {{
                    startTime = Date.now();
                    animate();
                }};
                
                window.pausePreview = function() {{
                    if (animationId) {{
                        cancelAnimationFrame(animationId);
                    }}
                }};
                
                window.stopPreview = function() {{
                    if (animationId) {{
                        cancelAnimationFrame(animationId);
                    }}
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                }};
            </script>
        </body>
        </html>
        """
        
        return html
    
    def create_scene_preview(self, scene_name):
        """Cria preview de uma cena completa"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://unpkg.com/@rive-app/canvas@2.31.2/dist/index.js"></script>
            <style>
                .scene-container {{
                    width: 100%;
                    height: 400px;
                    background: linear-gradient(135deg, #1F2937 0%, #374151 100%);
                    border-radius: 15px;
                    position: relative;
                    overflow: hidden;
                }}
                .scene-header {{
                    position: absolute;
                    top: 20px;
                    left: 20px;
                    color: white;
                    font-family: Arial, sans-serif;
                    z-index: 10;
                }}
                .scene-title {{
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 5px;
                }}
                .scene-subtitle {{
                    font-size: 14px;
                    opacity: 0.8;
                }}
                .metric-cards {{
                    position: absolute;
                    top: 80px;
                    left: 20px;
                    right: 20px;
                    display: flex;
                    gap: 20px;
                    justify-content: center;
                }}
                .metric-card {{
                    width: 120px;
                    height: 80px;
                    background: rgba(147, 51, 234, 0.1);
                    border: 2px solid #9333EA;
                    border-radius: 10px;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    color: white;
                    font-family: Arial, sans-serif;
                    animation: cardEntrance 0.5s ease-out forwards;
                    opacity: 0;
                    transform: translateY(20px);
                }}
                .metric-value {{
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 5px;
                }}
                .metric-label {{
                    font-size: 12px;
                    opacity: 0.8;
                }}
                @keyframes cardEntrance {{
                    to {{
                        opacity: 1;
                        transform: translateY(0);
                    }}
                }}
                .loading-spinner {{
                    position: absolute;
                    top: 200px;
                    left: 50%;
                    transform: translateX(-50%);
                    width: 60px;
                    height: 60px;
                    border: 4px solid rgba(147, 51, 234, 0.3);
                    border-top: 4px solid #9333EA;
                    border-radius: 50%;
                    animation: spin 2s linear infinite;
                }}
                @keyframes spin {{
                    0% {{ transform: translateX(-50%) rotate(0deg); }}
                    100% {{ transform: translateX(-50%) rotate(360deg); }}
                }}
                .success-check {{
                    position: absolute;
                    top: 300px;
                    left: 50%;
                    transform: translateX(-50%);
                    width: 40px;
                    height: 40px;
                    border: 3px solid #10B981;
                    border-radius: 50%;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    color: #10B981;
                    font-size: 20px;
                    animation: checkAppear 0.8s ease-out 1s forwards;
                    opacity: 0;
                    transform: translateX(-50%) scale(0);
                }}
                @keyframes checkAppear {{
                    to {{
                        opacity: 1;
                        transform: translateX(-50%) scale(1);
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="scene-container">
                <div class="scene-header">
                    <div class="scene-title">{scene_name}</div>
                    <div class="scene-subtitle">Preview em tempo real</div>
                </div>
                
                <div class="metric-cards">
                    <div class="metric-card" style="animation-delay: 0.1s;">
                        <div class="metric-value">150</div>
                        <div class="metric-label">Total Itens</div>
                    </div>
                    <div class="metric-card" style="animation-delay: 0.2s;">
                        <div class="metric-value">120</div>
                        <div class="metric-label">Conferidos</div>
                    </div>
                    <div class="metric-card" style="animation-delay: 0.3s;">
                        <div class="metric-value">80%</div>
                        <div class="metric-label">% Conferido</div>
                    </div>
                    <div class="metric-card" style="animation-delay: 0.4s;">
                        <div class="metric-value">12</div>
                        <div class="metric-label">Categorias</div>
                    </div>
                </div>
                
                <div class="loading-spinner"></div>
                <div class="success-check">✓</div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def update_animation(self, element_name, new_config):
        """Atualiza configuração de uma animação"""
        self.animations[element_name] = new_config
        self.save_animations()
    
    def save_project(self, project_name):
        """Salva o projeto atual"""
        project_data = {
            'id': str(uuid.uuid4()),
            'name': project_name,
            'date': self.get_timestamp(),
            'animations': self.animations,
            'editor_config': self.editor_config
        }
        
        # Salvar em arquivo local
        projects_dir = Path("saved_projects")
        projects_dir.mkdir(exist_ok=True)
        
        project_file = projects_dir / f"{project_name}_{project_data['id']}.json"
        with open(project_file, 'w') as f:
            json.dump(project_data, f, indent=2)
    
    def load_project(self, uploaded_file):
        """Carrega um projeto"""
        try:
            project_data = json.load(uploaded_file)
            self.animations = project_data.get('animations', self.animations)
            self.editor_config = project_data.get('editor_config', self.editor_config)
            self.save_animations()
        except Exception as e:
            st.error(f"❌ Erro ao carregar projeto: {e}")
    
    def export_configuration(self):
        """Exporta configuração atual"""
        return {
            'animations': self.animations,
            'editor_config': self.editor_config,
            'export_date': self.get_timestamp(),
            'version': '1.0.0'
        }
    
    def export_to_rive(self):
        """Exporta para formato Rive"""
        # Simular exportação para Rive
        rive_data = f"""
# Finance-Vibes Theme Export
# Generated on: {self.get_timestamp()}

# Animations
{json.dumps(self.animations, indent=2)}

# Theme Colors
{json.dumps(self.editor_config['theme_colors'], indent=2)}

# End of Export
        """.encode('utf-8')
        
        return rive_data
    
    def get_saved_projects(self):
        """Lista projetos salvos"""
        projects_dir = Path("saved_projects")
        if not projects_dir.exists():
            return []
        
        projects = []
        for project_file in projects_dir.glob("*.json"):
            try:
                with open(project_file, 'r') as f:
                    project_data = json.load(f)
                    projects.append(project_data)
            except:
                continue
        
        return sorted(projects, key=lambda x: x['date'], reverse=True)
    
    def load_project_by_id(self, project_id):
        """Carrega projeto por ID"""
        projects_dir = Path("saved_projects")
        for project_file in projects_dir.glob("*.json"):
            try:
                with open(project_file, 'r') as f:
                    project_data = json.load(f)
                    if project_data['id'] == project_id:
                        self.animations = project_data.get('animations', self.animations)
                        self.editor_config = project_data.get('editor_config', self.editor_config)
                        self.save_animations()
                        return
            except:
                continue
    
    def delete_project(self, project_id):
        """Exclui projeto por ID"""
        projects_dir = Path("saved_projects")
        for project_file in projects_dir.glob("*.json"):
            try:
                with open(project_file, 'r') as f:
                    project_data = json.load(f)
                    if project_data['id'] == project_id:
                        project_file.unlink()
                        return
            except:
                continue
    
    def create_backup(self):
        """Cria backup do estado atual"""
        return {
            'animations': self.animations,
            'editor_config': self.editor_config,
            'backup_date': self.get_timestamp(),
            'version': '1.0.0'
        }
    
    def restore_backup(self, backup_file):
        """Restaura backup"""
        try:
            backup_data = json.load(backup_file)
            self.animations = backup_data.get('animations', self.animations)
            self.editor_config = backup_data.get('editor_config', self.editor_config)
            self.save_animations()
        except Exception as e:
            st.error(f"❌ Erro ao restaurar backup: {e}")
    
    def save_animations(self):
        """Salva animações em arquivo local"""
        animations_file = Path("saved_animations.json")
        with open(animations_file, 'w') as f:
            json.dump(self.animations, f, indent=2)
    
    def get_timestamp(self):
        """Retorna timestamp atual formatado"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def render_rive_visual_editor():
    """Função principal para renderizar o editor visual Rive"""
    st.set_page_config(
        page_title="Editor Visual Rive - Finance-Vibes",
        page_icon="🎨",
        layout="wide"
    )
    
    # Aplicar tema personalizado
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Inicializar editor
    editor = RiveVisualEditor()
    
    # Renderizar interface
    editor.render_editor_interface()

if __name__ == "__main__":
    render_rive_visual_editor()
