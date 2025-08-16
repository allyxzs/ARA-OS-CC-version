import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import time
import random
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="ARA - Advanced Performance Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado para estilo escuro e gradientes
st.markdown("""
<style>
    :root {
        --primary: #6a5af9;
        --secondary: #d66efd;
        --accent: #4cc9f0;
        --dark: #0f0c29;
        --darker: #090616;
        --card: rgba(30, 30, 65, 0.7);
    }
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    body {
        background: linear-gradient(135deg, var(--darker), var(--dark));
        color: #e0e0ff;
        min-height: 100vh;
    }
    
    .stApp {
        background: transparent !important;
        max-width: 1400px;
        margin: 0 auto;
        padding: 0 20px;
    }
    
    .header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 0;
        border-bottom: 1px solid rgba(106, 90, 249, 0.5);
        margin-bottom: 25px;
    }
    
    .logo {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .logo h1 {
        font-size: 28px;
        font-weight: 700;
        background: linear-gradient(90deg, var(--primary), var(--secondary));
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .plugin-tabs {
        display: flex;
        gap: 10px;
        background: rgba(20, 20, 45, 0.7);
        padding: 5px;
        border-radius: 12px;
    }
    
    .plugin-btn {
        background: transparent !important;
        border: none !important;
        color: #a0a0ff !important;
        font-weight: 600;
        padding: 8px 20px !important;
        transition: all 0.3s !important;
        border-radius: 8px !important;
    }
    
    .plugin-btn:hover {
        color: var(--secondary) !important;
        background: rgba(214, 110, 253, 0.1) !important;
    }
    
    .plugin-btn.active {
        color: var(--secondary) !important;
        background: rgba(214, 110, 253, 0.15) !important;
    }
    
    .metric-card {
        background: var(--card);
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(106, 90, 249, 0.3);
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .metric-title {
        font-size: 14px;
        color: #a0a0ff;
        margin-bottom: 5px;
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: 700;
        background: linear-gradient(90deg, var(--primary), var(--accent));
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-delta {
        font-size: 12px;
        color: #ff6b6b;
    }
    
    .fps-indicator {
        font-size: 32px;
        font-weight: 800;
        background: linear-gradient(90deg, var(--accent), var(--secondary));
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .section-title {
        font-size: 18px;
        color: var(--secondary);
        margin: 20px 0 10px 0;
        padding-bottom: 5px;
        border-bottom: 1px solid rgba(106, 90, 249, 0.3);
    }
    
    .graph-container {
        background: var(--card);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(106, 90, 249, 0.3);
    }
    
    .status-card {
        background: var(--card);
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.5);
        border: 1px solid rgba(106, 90, 249, 0.3);
        margin-top: 20px;
    }
    
    .status-value {
        font-size: 22px;
        font-weight: 600;
        color: var(--accent);
    }
    
    .footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 30px;
        padding: 15px 0;
        border-top: 1px solid rgba(106, 90, 249, 0.3);
        color: #a0a0ff;
        font-size: 14px;
    }
    
    .stButton>button {
        width: 100% !important;
    }
    
    .st-bb {
        background-color: transparent !important;
    }
    
    /* Correção para warnings de contexto */
    .reportview-container .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Ajustes para gráficos */
    .js-plotly-plot .plotly, .js-plotly-plot .plotly div {
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)

# Solução para os warnings de contexto
if 'first_run' not in st.session_state:
    st.session_state.first_run = True
    st.session_state.last_update = time.time()
    
# Estado da aplicação
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 'Dashboard'
    
# Funções para atualizar dados simulados
def get_cpu_usage():
    return max(10, min(100, 51 + random.randint(-5, 5)))

def get_memory_usage():
    return max(70, min(99, 92 + random.randint(-2, 2)))

def get_disk_usage():
    return max(40, min(80, 57 + random.uniform(-1, 1)))

def get_fps():
    return 100000 + random.randint(-5000, 5000)

# Header com logo e plugins
st.markdown("""
<div class="header">
    <div class="logo">
        <h1>🔍 ARA</h1>
    </div>
    <div class="plugin-tabs">
""", unsafe_allow_html=True)

# Botões dos plugins
cols = st.columns(4)
with cols[0]:
    if st.button("Dashboard", key="dash"):
        st.session_state.active_tab = 'Dashboard'
with cols[1]:
    if st.button("Code Creator", key="code"):
        st.session_state.active_tab = 'Code Creator'
with cols[2]:
    if st.button("Architecture", key="arch"):
        st.session_state.active_tab = 'Architecture'
with cols[3]:
    if st.button("Chat", key="chat"):
        st.session_state.active_tab = 'Chat'

st.markdown("</div></div>", unsafe_allow_html=True)

# Atualização automática a cada 2 segundos
refresh_needed = False
if time.time() - st.session_state.last_update > 2:
    st.session_state.last_update = time.time()
    refresh_needed = True

# Conteúdo baseado na aba selecionada
if st.session_state.active_tab == 'Dashboard':
    # Métricas principais
    st.markdown('<div class="section-title">Plugins</div>', unsafe_allow_html=True)
    metric_cols = st.columns(4)
    
    with metric_cols[0]:
        cpu = get_cpu_usage()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">CPU</div>
            <div class="metric-value">{cpu:.0f}%</div>
            <div class="metric-delta">▲ 2%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with metric_cols[1]:
        mem = get_memory_usage()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">MEMÓRIA</div>
            <div class="metric-value">{mem:.0f}%</div>
            <div class="metric-delta">▲ 3%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with metric_cols[2]:
        disk = get_disk_usage()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">DISCO</div>
            <div class="metric-value">{disk:.1f}%</div>
            <div class="metric-delta">▼ 1%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with metric_cols[3]:
        fps = get_fps()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">FPS</div>
            <div class="fps-indicator">{fps}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Gráficos de desempenho
    st.markdown('<div class="section-title">Desempenho</div>', unsafe_allow_html=True)
    graph_cols = st.columns(3)
    
    # Gráfico CPU
    with graph_cols[0]:
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        fig_cpu = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = cpu,
            number = {'suffix': "%"},
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 0},
                'bar': {'color': "#6a5af9"},
                'bgcolor': "rgba(0,0,0,0)",
                'steps': [
                    {'range': [0, 50], 'color': 'rgba(30, 30, 65, 0.3)'},
                    {'range': [50, 80], 'color': 'rgba(106, 90, 249, 0.2)'},
                    {'range': [80, 100], 'color': 'rgba(214, 110, 253, 0.2)'}
                ],
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.8,
                    'value': cpu
                }
            }
        ))
        fig_cpu.update_layout(
            height=300,
            margin=dict(t=0, b=0),
            font={'color': "#a0a0ff"}
        )
        st.plotly_chart(fig_cpu, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Gráfico Memória
    with graph_cols[1]:
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        fig_mem = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = mem,
            number = {'suffix': "%"},
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 0},
                'bar': {'color': "#d66efd"},
                'bgcolor': "rgba(0,0,0,0)",
                'steps': [
                    {'range': [0, 50], 'color': 'rgba(30, 30, 65, 0.3)'},
                    {'range': [50, 80], 'color': 'rgba(106, 90, 249, 0.2)'},
                    {'range': [80, 100], 'color': 'rgba(214, 110, 253, 0.2)'}
                ],
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.8,
                    'value': mem
                }
            }
        ))
        fig_mem.update_layout(
            height=300,
            margin=dict(t=0, b=0),
            font={'color': "#a0a0ff"}
        )
        st.plotly_chart(fig_mem, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Gráfico Disco
    with graph_cols[2]:
        st.markdown('<div class="graph-container">', unsafe_allow_html=True)
        fig_disk = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = disk,
            number = {'suffix': "%"},
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 0},
                'bar': {'color': "#4cc9f0"},
                'bgcolor': "rgba(0,0,0,0)",
                'steps': [
                    {'range': [0, 50], 'color': 'rgba(30, 30, 65, 0.3)'},
                    {'range': [50, 70], 'color': 'rgba(76, 201, 240, 0.2)'},
                    {'range': [70, 100], 'color': 'rgba(106, 90, 249, 0.2)'}
                ],
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.8,
                    'value': disk
                }
            }
        ))
        fig_disk.update_layout(
            height=300,
            margin=dict(t=0, b=0),
            font={'color': "#a0a0ff"}
        )
        st.plotly_chart(fig_disk, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Status de rede e uptime
    st.markdown('<div class="section-title">Status do Sistema</div>', unsafe_allow_html=True)
    status_cols = st.columns([3, 1])
    
    with status_cols[0]:
        st.markdown("""
        <div class="status-card">
            <div class="metric-title">REDE</div>
            <div class="status-value">0,770,018/3</div>
        </div>
        """, unsafe_allow_html=True)
    
    with status_cols[1]:
        st.markdown("""
        <div class="status-card">
            <div class="metric-title">UPTIME</div>
            <div class="status-value">20%</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Gráfico de histórico de desempenho
    st.markdown('<div class="section-title">Histórico de Desempenho</div>', unsafe_allow_html=True)
    
    # Criar dados históricos
    time_points = list(range(30))
    cpu_history = [max(10, min(100, 50 + random.randint(-10, 10))) for _ in time_points]
    mem_history = [max(70, min(99, 90 + random.randint(-5, 5))) for _ in time_points]
    disk_history = [max(40, min(80, 55 + random.uniform(-5, 5))) for _ in time_points]
    
    fig_history = go.Figure()
    fig_history.add_trace(go.Scatter(
        x=time_points, y=cpu_history,
        mode='lines+markers',
        name='CPU',
        line=dict(color='#6a5af9', width=3)
    ))
    fig_history.add_trace(go.Scatter(
        x=time_points, y=mem_history,
        mode='lines+markers',
        name='Memória',
        line=dict(color='#d66efd', width=3)
    ))
    fig_history.add_trace(go.Scatter(
        x=time_points, y=disk_history,
        mode='lines+markers',
        name='Disco',
        line=dict(color='#4cc9f0', width=3)
    ))
    
    fig_history.update_layout(
        height=300,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=30, b=30, l=30, r=30),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#a0a0ff")
        ),
        xaxis=dict(showgrid=False, color="#a0a0ff"),
        yaxis=dict(showgrid=True, gridcolor='rgba(100,100,150,0.2)', color="#a0a0ff")
    )
    
    st.markdown('<div class="graph-container">', unsafe_allow_html=True)
    st.plotly_chart(fig_history, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.active_tab == 'Code Creator':
    st.markdown("""
    <div class="graph-container" style="height: 600px;">
        <h2 style="color: #d66efd; margin-bottom: 20px;">Code Creator</h2>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <div>
                <h3 style="color: #a0a0ff; margin-bottom: 10px;">Gerar Código</h3>
                <textarea style="width: 100%; height: 200px; background: rgba(30,30,50,0.8); 
                border: 1px solid #4cc9f0; border-radius: 8px; color: white; padding: 10px;" 
                placeholder="Descreva o código que deseja gerar..."></textarea>
                <button style="background: linear-gradient(90deg, #6a5af9, #d66efd); 
                border: none; border-radius: 8px; color: white; padding: 10px 20px; 
                margin-top: 10px; cursor: pointer;">Gerar Código</button>
            </div>
            <div>
                <h3 style="color: #a0a0ff; margin-bottom: 10px;">Código Gerado</h3>
                <div style="background: rgba(30,30,50,0.8); border: 1px solid #6a5af9; 
                border-radius: 8px; color: white; padding: 15px; height: 200px; 
                font-family: monospace; overflow: auto;">
                # Código aparecerá aqui
                </div>
            </div>
        </div>
        
        <div style="margin-top: 30px;">
            <h3 style="color: #a0a0ff; margin-bottom: 10px;">Histórico de Geração</h3>
            <div style="background: rgba(30,30,50,0.8); border: 1px solid #4cc9f0; 
            border-radius: 8px; padding: 15px; max-height: 200px; overflow: auto;">
                <div style="padding: 10px; border-bottom: 1px solid rgba(100,100,150,0.3);">
                    <div style="color: #6a5af9; font-weight: bold;">Função de ordenação em Python</div>
                    <div style="color: #a0a0ff; font-size: 0.9em;">Gerado em: 2023-11-15 14:30</div>
                </div>
                <div style="padding: 10px; border-bottom: 1px solid rgba(100,100,150,0.3);">
                    <div style="color: #6a5af9; font-weight: bold;">API REST com Flask</div>
                    <div style="color: #a0a0ff; font-size: 0.9em;">Gerado em: 2023-11-14 09:45</div>
                </div>
                <div style="padding: 10px;">
                    <div style="color: #6a5af9; font-weight: bold;">Script de web scraping</div>
                    <div style="color: #a0a0ff; font-size: 0.9em;">Gerado em: 2023-11-13 16:20</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.active_tab == 'Architecture':
    st.markdown("""
    <div class="graph-container" style="height: 600px;">
        <h2 style="color: #d66efd; margin-bottom: 20px;">Architecture Designer</h2>
        <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 20px;">
            <div>
                <h3 style="color: #a0a0ff; margin-bottom: 10px;">Componentes</h3>
                <div style="background: rgba(30,30,50,0.8); border: 1px solid #4cc9f0; 
                border-radius: 8px; padding: 15px; height: 450px; overflow: auto;">
                    <div style="padding: 10px; background: rgba(106,90,249,0.2); 
                    border-radius: 5px; margin-bottom: 10px; cursor: move;">
                        Banco de Dados
                    </div>
                    <div style="padding: 10px; background: rgba(214,110,253,0.2); 
                    border-radius: 5px; margin-bottom: 10px; cursor: move;">
                        API Gateway
                    </div>
                    <div style="padding: 10px; background: rgba(76,201,240,0.2); 
                    border-radius: 5px; margin-bottom: 10px; cursor: move;">
                        Serviço de Autenticação
                    </div>
                    <div style="padding: 10px; background: rgba(106,90,249,0.2); 
                    border-radius: 5px; margin-bottom: 10px; cursor: move;">
                        Serviço de Pagamentos
                    </div>
                    <div style="padding: 10px; background: rgba(214,110,253,0.2); 
                    border-radius: 5px; margin-bottom: 10px; cursor: move;">
                        Frontend Web
                    </div>
                    <div style="padding: 10px; background: rgba(76,201,240,0.2); 
                    border-radius: 5px; cursor: move;">
                        Serviço de Notificações
                    </div>
                </div>
            </div>
            <div>
                <h3 style="color: #a0a0ff; margin-bottom: 10px;">Diagrama de Arquitetura</h3>
                <div style="background: rgba(30,30,50,0.8); border: 1px solid #6a5af9; 
                border-radius: 8px; padding: 20px; height: 450px; position: relative;">
                    <div style="position: absolute; top: 50px; left: 100px; padding: 15px; 
                    background: rgba(106,90,249,0.3); border-radius: 8px; border: 1px solid #6a5af9;">
                        API Gateway
                    </div>
                    <div style="position: absolute; top: 200px; left: 50px; padding: 15px; 
                    background: rgba(214,110,253,0.3); border-radius: 8px; border: 1px solid #d66efd;">
                        Autenticação
                    </div>
                    <div style="position: absolute; top: 200px; left: 250px; padding: 15px; 
                    background: rgba(76,201,240,0.3); border-radius: 8px; border: 1px solid #4cc9f0;">
                        Pagamentos
                    </div>
                    <div style="position: absolute; top: 200px; left: 450px; padding: 15px; 
                    background: rgba(214,110,253,0.3); border-radius: 8px; border: 1px solid #d66efd;">
                        Notificações
                    </div>
                    <div style="position: absolute; top: 350px; left: 250px; padding: 15px; 
                    background: rgba(106,90,249,0.3); border-radius: 8px; border: 1px solid #6a5af9;">
                        Banco de Dados
                    </div>
                    
                    <!-- Linhas de conexão -->
                    <svg height="400" width="600" style="position: absolute; top: 0; left: 0;">
                        <line x1="160" y1="90" x2="160" y2="170" style="stroke:#4cc9f0;stroke-width:2" />
                        <line x1="160" y1="170" x2="90" y2="170" style="stroke:#4cc9f0;stroke-width:2" />
                        <line x1="160" y1="170" x2="230" y2="170" style="stroke:#4cc9f0;stroke-width:2" />
                        <line x1="160" y1="170" x2="390" y2="170" style="stroke:#4cc9f0;stroke-width:2" />
                        <line x1="90" y1="170" x2="90" y2="250" style="stroke:#4cc9f0;stroke-width:2" />
                        <line x1="230" y1="170" x2="230" y2="250" style="stroke:#4cc9f0;stroke-width:2" />
                        <line x1="390" y1="170" x2="390" y2="250" style="stroke:#4cc9f0;stroke-width:2" />
                        <line x1="160" y1="290" x2="230" y2="290" style="stroke:#4cc9f0;stroke-width:2" />
                        <line x1="230" y1="290" x2="230" y2="250" style="stroke:#4cc9f0;stroke-width:2" />
                    </svg>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.active_tab == 'Chat':
    st.markdown("""
    <div class="graph-container" style="height: 600px;">
        <h2 style="color: #d66efd; margin-bottom: 20px;">Assistente de IA</h2>
        <div style="display: grid; grid-template-rows: 1fr auto; height: 500px; gap: 15px;">
            <div style="background: rgba(30,30,50,0.8); border: 1px solid #6a5af9; 
            border-radius: 8px; padding: 20px; overflow: auto;">
                <div style="text-align: right; margin-bottom: 15px;">
                    <div style="display: inline-block; background: rgba(106,90,249,0.3); 
                    border-radius: 15px; padding: 10px 15px; max-width: 80%;">
                        Como posso monitorar o desempenho do meu servidor?
                    </div>
                </div>
                <div style="margin-bottom: 15px;">
                    <div style="display: inline-block; background: rgba(76,201,240,0.3); 
                    border-radius: 15px; padding: 10px 15px; max-width: 80%;">
                        Você pode usar o dashboard da ARA para monitorar CPU, memória, disco e rede em tempo real. 
                        Além disso, recomendo configurar alertas para quando os recursos atingirem 80% de utilização.
                    </div>
                </div>
                <div style="text-align: right; margin-bottom: 15px;">
                    <div style="display: inline-block; background: rgba(106,90,249,0.3); 
                    border-radius: 15px; padding: 10px 15px; max-width: 80%;">
                        Como posso melhorar o desempenho do meu banco de dados?
                    </div>
                </div>
                <div style="margin-bottom: 15px;">
                    <div style="display: inline-block; background: rgba(76,201,240,0.3); 
                    border-radius: 15px; padding: 10px 15px; max-width: 80%;">
                        Algumas sugestões:
                        <ul style="margin: 10px 0; padding-left: 20px;">
                            <li>Otimizar consultas frequentes</li>
                            <li>Adicionar índices em colunas frequentemente filtradas</li>
                            <li>Aumentar memória alocada para cache</li>
                            <li>Considerar particionamento de tabelas grandes</li>
                        </ul>
                        Posso gerar um script de análise para você?
                    </div>
                </div>
            </div>
            <div style="display: flex; gap: 10px;">
                <input type="text" placeholder="Digite sua mensagem..." style="
                    flex: 1; 
                    background: rgba(30,30,50,0.8); 
                    border: 1px solid #4cc9f0;
                    border-radius: 25px;
                    padding: 12px 20px;
                    color: white;
                ">
                <button style="
                    background: linear-gradient(90deg, #6a5af9, #d66efd); 
                    border: none; 
                    border-radius: 25px; 
                    color: white; 
                    padding: 12px 25px;
                    cursor: pointer;
                ">Enviar</button>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Rodapé
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f"""
<div class="footer">
    <div>Atualizado em: {now}</div>
    <div>Sistema ARA v2.4.1</div>
    <div>Status: <span style="color: #6a5af9;">Operacional</span></div>
</div>
""", unsafe_allow_html=True)

# Forçar atualização se necessário
if refresh_needed:
    # Verifica qual função de rerun está disponível
    if hasattr(st, 'rerun'):
        st.rerun()
    elif hasattr(st, 'experimental_rerun'):
        st.experimental_rerun()
    else:
        # Atualiza o estado para forçar nova renderização
        st.experimental_set_query_params(timestamp=time.time())