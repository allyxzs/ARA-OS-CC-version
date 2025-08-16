import webview
import threading
import time
from flask import Flask, render_template_string, request, jsonify
import psutil
import GPUtil
import platform
import socket
import datetime
import json
import os
import uuid

# ========== CONFIGURAÇÃO FLASK (SERVER LOCAL) ==========
app = Flask(__name__)

# Configurações padrão
DEFAULT_CONFIG = {
    "theme": "dark",
    "primary_color": "#6a5af9",
    "secondary_color": "#d66efd",
    "accent_color": "#4cc9f0",
    "gauge_cpu_color": "#6a5af9",
    "gauge_memory_color": "#d66efd",
    "gauge_disk_color": "#4cc9f0",
    "text_color": "#e0e0ff",
    "card_color": "rgba(30, 30, 65, 0.7)",
    "font": "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif"
}

# Carregar ou criar configurações
CONFIG_FILE = "ara_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return DEFAULT_CONFIG
    return DEFAULT_CONFIG

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

# Configuração atual
current_config = load_config()

# Template HTML/CSS/JS completo com todas as funcionalidades
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ARA OS CC - Desktop vers. 2.0</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        :root {
            --primary: {{ config.primary_color }};
            --secondary: {{ config.secondary_color }};
            --accent: {{ config.accent_color }};
            --dark: #0f0c29;
            --darker: #090616;
            --card: {{ config.card_color }};
            --success: #00c9a7;
            --warning: #ff9e00;
            --danger: #ff3860;
            --text: {{ config.text_color }};
            --font: {{ config.font }};
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: var(--font);
            transition: background-color 0.3s, color 0.3s;
        }
        
        body {
            background: linear-gradient(135deg, var(--darker), var(--dark));
            color: var(--text);
            min-height: 100vh;
            padding: 20px;
            overflow: hidden;
        }
        
        .light-mode {
            --dark: #f0f2f5;
            --darker: #e4e7eb;
            --card: rgba(255, 255, 255, 0.9);
            --text: #333333;
            background: linear-gradient(135deg, var(--darker), var(--dark));
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            height: calc(100vh - 40px);
            display: flex;
            flex-direction: column;
        }
        
        .content {
            overflow-y: auto;
            flex: 1;
            padding-right: 5px;
        }
        
        /* Barra de rolagem personalizada */
        .content::-webkit-scrollbar {
            width: 8px;
        }
        
        .content::-webkit-scrollbar-track {
            background: rgba(20, 20, 45, 0.3);
            border-radius: 4px;
        }
        
        .content::-webkit-scrollbar-thumb {
            background: linear-gradient(var(--primary), var(--secondary));
            border-radius: 4px;
        }
        
        .content::-webkit-scrollbar-thumb:hover {
            background: var(--accent);
        }
        
        .light-mode .content::-webkit-scrollbar-track {
            background: rgba(200, 200, 220, 0.3);
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 0;
            border-bottom: 1px solid rgba(106, 90, 249, 0.3);
            margin-bottom: 25px;
            flex-shrink: 0;
        }
        
        .logo h1 {
            font-size: 28px;
            font-weight: 700;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .tabs {
            display: flex;
            gap: 10px;
            background: rgba(20, 20, 45, 0.7);
            padding: 5px;
            border-radius: 12px;
        }
        
        .light-mode .tabs {
            background: rgba(230, 230, 245, 0.7);
        }
        
        .tab-btn {
            background: transparent;
            border: none;
            color: #a0a0ff;
            font-weight: 600;
            padding: 8px 20px;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .light-mode .tab-btn {
            color: #555577;
        }
        
        .tab-btn:hover {
            color: var(--secondary);
            background: rgba(214, 110, 253, 0.1);
        }
        
        .light-mode .tab-btn:hover {
            background: rgba(214, 110, 253, 0.15);
        }
        
        .tab-btn.active {
            color: var(--secondary);
            background: rgba(214, 110, 253, 0.15);
        }
        
        .light-mode .tab-btn.active {
            background: rgba(214, 110, 253, 0.2);
        }
        
        .metric-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .metric-card {
            background: var(--card);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(106, 90, 249, 0.2);
            transition: all 0.3s ease;
        }
        
        .light-mode .metric-card {
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(200, 200, 220, 0.5);
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(106, 90, 249, 0.3);
        }
        
        .metric-title {
            font-size: 14px;
            color: #a0a0ff;
            margin-bottom: 5px;
        }
        
        .light-mode .metric-title {
            color: #555577;
        }
        
        .metric-value {
            font-size: 32px;
            font-weight: 700;
            background: linear-gradient(90deg, var(--primary), var(--accent));
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .metric-details {
            font-size: 12px;
            color: #a0a0ff;
            margin-top: 10px;
        }
        
        .light-mode .metric-details {
            color: #555577;
        }
        
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .chart-container {
            background: var(--card);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(106, 90, 249, 0.2);
            height: 300px;
            overflow: hidden;
        }
        
        .light-mode .chart-container {
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(200, 200, 220, 0.5);
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .info-card {
            background: var(--card);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(106, 90, 249, 0.2);
        }
        
        .light-mode .info-card {
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(200, 200, 220, 0.5);
        }
        
        .info-title {
            font-size: 18px;
            color: var(--secondary);
            margin-bottom: 15px;
            padding-bottom: 5px;
            border-bottom: 1px solid rgba(106, 90, 249, 0.3);
        }
        
        .info-content {
            color: #a0a0ff;
            line-height: 1.6;
        }
        
        .light-mode .info-content {
            color: #555577;
        }
        
        .footer {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 0;
            border-top: 1px solid rgba(106, 90, 249, 0.3);
            color: #a0a0ff;
            font-size: 14px;
            flex-shrink: 0;
        }
        
        .light-mode .footer {
            color: #555577;
            border-top: 1px solid rgba(200, 200, 220, 0.5);
        }
        
        .status-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            background: rgba(0, 201, 167, 0.2);
            color: var(--success);
        }
        
        /* Tabs de conteúdo */
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        /* Personalização */
        .customization-panel {
            background: var(--card);
            border-radius: 15px;
            padding: 20px;
            margin-top: 20px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        }
        
        .color-picker-group {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .color-picker {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        
        .color-picker label {
            font-size: 14px;
            color: #a0a0ff;
        }
        
        .light-mode .color-picker label {
            color: #555577;
        }
        
        .color-picker input {
            width: 100%;
            height: 40px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
        }
        
        .theme-toggle {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .switch {
            position: relative;
            display: inline-block;
            width: 60px;
            height: 34px;
        }
        
        .switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }
        
        .slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: .4s;
            border-radius: 34px;
        }
        
        .slider:before {
            position: absolute;
            content: "";
            height: 26px;
            width: 26px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }
        
        input:checked + .slider {
            background: linear-gradient(90deg, var(--primary), var(--secondary));
        }
        
        input:checked + .slider:before {
            transform: translateX(26px);
        }
        
        /* Code Creator */
        .code-editor {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }
        
        .editor-section {
            background: var(--card);
            border-radius: 15px;
            padding: 15px;
            height: 400px;
            display: flex;
            flex-direction: column;
        }
        
        .editor-section h3 {
            color: var(--secondary);
            margin-bottom: 10px;
        }
        
        .editor-section textarea {
            flex: 1;
            background: rgba(30, 30, 50, 0.5);
            border: 1px solid var(--accent);
            border-radius: 8px;
            color: var(--text);
            padding: 10px;
            font-family: monospace;
            resize: none;
        }
        
        .light-mode .editor-section textarea {
            background: rgba(240, 240, 250, 0.7);
        }
        
        .editor-section button {
            margin-top: 10px;
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            border: none;
            border-radius: 8px;
            color: white;
            padding: 10px;
            cursor: pointer;
            font-weight: 600;
        }
        
        /* Architecture */
        .architecture-container {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 20px;
            margin-top: 20px;
        }
        
        .components-panel {
            background: var(--card);
            border-radius: 15px;
            padding: 15px;
            height: 500px;
            overflow-y: auto;
        }
        
        .component-item {
            background: rgba(106, 90, 249, 0.1);
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 10px;
            cursor: move;
        }
        
        .architecture-canvas {
            background: var(--card);
            border-radius: 15px;
            padding: 20px;
            height: 500px;
            position: relative;
        }
    </style>
</head>
<body class="{{ 'light-mode' if config.theme == 'light' else '' }}">
    <div class="container">
        <div class="header">
            <div class="logo">
                <h1>🚀 ARA OS</h1>
            </div>
            <div class="tabs">
                <button class="tab-btn active" data-tab="dashboard">Dashboard</button>
                <button class="tab-btn" data-tab="performance">Performance</button>
                <button class="tab-btn" data-tab="architecture">Architecture</button>
                <button class="tab-btn" data-tab="code-creator">Code Creator</button>
                <button class="tab-btn" data-tab="settings">Configurações</button>
            </div>
        </div>
        
        <div class="content">
            <!-- Dashboard Tab -->
            <div id="dashboard" class="tab-content active">
                <div class="metric-grid">
                    <div class="metric-card">
                        <div class="metric-title">CPU</div>
                        <div class="metric-value" id="cpu-value">0%</div>
                        <div class="metric-details" id="cpu-details">Núcleos: 0 | Threads: 0</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-title">MEMÓRIA</div>
                        <div class="metric-value" id="memory-value">0%</div>
                        <div class="metric-details" id="memory-details">Usado: 0GB / Total: 0GB</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-title">DISCO</div>
                        <div class="metric-value" id="disk-value">0%</div>
                        <div class="metric-details" id="disk-details">Usado: 0GB / Total: 0GB</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-title">GPU</div>
                        <div class="metric-value" id="gpu-value">0%</div>
                        <div class="metric-details" id="gpu-details">Nenhuma GPU detectada</div>
                    </div>
                </div>
                
                <div class="charts-grid">
                    <div class="chart-container" id="cpu-chart"></div>
                    <div class="chart-container" id="memory-chart"></div>
                    <div class="chart-container" id="disk-chart"></div>
                </div>
                
                <div class="info-grid">
                    <div class="info-card">
                        <div class="info-title">Informações do Sistema</div>
                        <div class="info-content">
                            <p><strong>Hostname:</strong> <span id="hostname">-</span></p>
                            <p><strong>Sistema Operacional:</strong> <span id="os">-</span></p>
                            <p><strong>Tempo de Atividade:</strong> <span id="uptime">-</span></p>
                            <p><strong>Processos Ativos:</strong> <span id="processes">-</span></p>
                        </div>
                    </div>
                    
                    <div class="info-card">
                        <div class="info-title">Status da Rede</div>
                        <div class="info-content">
                            <p><strong>Enviados:</strong> <span id="net-sent">- MB</span></p>
                            <p><strong>Recebidos:</strong> <span id="net-recv">- MB</span></p>
                            <p><strong>Status:</strong> <span class="status-badge">Operacional</span></p>
                            <p><strong>Última Atualização:</strong> <span id="last-update">-</span></p>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Performance Tab -->
            <div id="performance" class="tab-content">
                <div class="info-card">
                    <div class="info-title">Histórico de Desempenho</div>
                    <div class="chart-container" id="performance-chart" style="height: 400px;"></div>
                </div>
                
                <div class="metric-grid" style="margin-top: 20px;">
                    <div class="metric-card">
                        <div class="metric-title">Processos</div>
                        <div class="metric-value" id="process-count">0</div>
                        <div class="metric-details" id="top-process">-</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-title">Temperatura</div>
                        <div class="metric-value" id="temperature-value">0°C</div>
                        <div class="metric-details" id="temperature-details">CPU: 0°C | GPU: 0°C</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-title">Rede</div>
                        <div class="metric-value" id="network-speed">0 Mbps</div>
                        <div class="metric-details">Upload: 0 Mbps | Download: 0 Mbps</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-title">Bateria</div>
                        <div class="metric-value" id="battery-value">0%</div>
                        <div class="metric-details" id="battery-status">-</div>
                    </div>
                </div>
            </div>
            
            <!-- Architecture Tab -->
            <div id="architecture" class="tab-content">
                <div class="architecture-container">
                    <div class="components-panel">
                        <h3>Componentes</h3>
                        <div class="component-item" draggable="true">API Gateway</div>
                        <div class="component-item" draggable="true">Banco de Dados</div>
                        <div class="component-item" draggable="true">Serviço de Autenticação</div>
                        <div class="component-item" draggable="true">Microserviço de Pagamentos</div>
                        <div class="component-item" draggable="true">Frontend Web</div>
                        <div class="component-item" draggable="true">Serviço de Notificações</div>
                        <div class="component-item" draggable="true">Cache Redis</div>
                        <div class="component-item" draggable="true">Filas RabbitMQ</div>
                    </div>
                    
                    <div class="architecture-canvas" id="arch-canvas">
                        <h3>Diagrama de Arquitetura</h3>
                        <p>Arraste componentes para esta área para criar seu diagrama</p>
                    </div>
                </div>
            </div>
            
            <!-- Code Creator Tab -->
            <div id="code-creator" class="tab-content">
                <div class="info-card">
                    <div class="info-title">Code Creator</div>
                    <p>Crie código rapidamente com nossa ferramenta de IA</p>
                    
                    <div class="code-editor">
                        <div class="editor-section">
                            <h3>Descrição</h3>
                            <textarea id="code-description" placeholder="Descreva o código que deseja gerar..."></textarea>
                            <button id="generate-code">Gerar Código</button>
                        </div>
                        
                        <div class="editor-section">
                            <h3>Código Gerado</h3>
                            <textarea id="generated-code" placeholder="O código aparecerá aqui..."></textarea>
                            <button id="copy-code">Copiar Código</button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Settings Tab -->
            <div id="settings" class="tab-content">
                <div class="info-card">
                    <div class="info-title">Configurações de Aparência</div>
                    
                    <div class="theme-toggle">
                        <span>Modo Escuro</span>
                        <label class="switch">
                            <input type="checkbox" id="theme-toggle" {{ 'checked' if config.theme == 'light' else '' }}>
                            <span class="slider"></span>
                        </label>
                        <span>Modo Claro</span>
                    </div>
                    
                    <div class="customization-panel">
                        <h3>Personalização de Cores</h3>
                        
                        <div class="color-picker-group">
                            <div class="color-picker">
                                <label>Cor Primária</label>
                                <input type="color" id="primary-color" value="{{ config.primary_color }}">
                            </div>
                            
                            <div class="color-picker">
                                <label>Cor Secundária</label>
                                <input type="color" id="secondary-color" value="{{ config.secondary_color }}">
                            </div>
                            
                            <div class="color-picker">
                                <label>Cor de Destaque</label>
                                <input type="color" id="accent-color" value="{{ config.accent_color }}">
                            </div>
                            
                            <div class="color-picker">
                                <label>Cor do Gráfico (CPU)</label>
                                <input type="color" id="gauge-cpu-color" value="{{ config.gauge_cpu_color }}">
                            </div>
                            
                            <div class="color-picker">
                                <label>Cor do Gráfico (Memória)</label>
                                <input type="color" id="gauge-memory-color" value="{{ config.gauge_memory_color }}">
                            </div>
                            
                            <div class="color-picker">
                                <label>Cor do Gráfico (Disco)</label>
                                <input type="color" id="gauge-disk-color" value="{{ config.gauge_disk_color }}">
                            </div>
                        </div>
                        
                        <button id="save-settings" style="width: 100%; padding: 12px; margin-top: 10px;">Salvar Configurações</button>
                        <button id="reset-settings" style="width: 100%; padding: 12px; margin-top: 10px; background: var(--danger);">Restaurar Padrões</button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <div>ARA Desktop v2.0</div>
            <div>ARA OS CC</div>
            <div>Desenvolvido com ❤️ por Tottenham A.C.</div>
            <div id="system-status">Status: <span class="status-badge">Operacional</span></div>
        </div>
    </div>

    <script>
        // Configuração atual
        const config = JSON.parse('{{ config | tojson | safe }}');
        
        // Funções para atualizar os gráficos
        function createGaugeChart(elementId, value, title, color) {
            const data = [{
                type: "indicator",
                mode: "gauge+number",
                value: value,
                title: { text: title },
                gauge: {
                    axis: { range: [null, 100], tickwidth: 1 },
                    bar: { color: color },
                    steps: [
                        { range: [0, 60], color: 'rgba(30, 30, 65, 0.3)' },
                        { range: [60, 80], color: 'rgba(255, 158, 0, 0.2)' },
                        { range: [80, 100], color: 'rgba(255, 56, 96, 0.2)' }
                    ],
                    threshold: {
                        line: { color: "white", width: 4 },
                        thickness: 0.8,
                        value: value
                    }
                }
            }];
            
            const layout = {
                height: 250,
                margin: { t: 0, b: 0, l: 0, r: 0 },
                font: { color: config.text_color },
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)'
            };
            
            const element = document.getElementById(elementId);
            Plotly.purge(element);
            Plotly.newPlot(element, data, layout, {
                displayModeBar: false,
                staticPlot: false
            });
        }
        
        // Criar gráfico de performance
        function createPerformanceChart() {
            const timePoints = [];
            const cpuData = [];
            const memoryData = [];
            
            // Gerar dados históricos simulados
            for (let i = 0; i < 60; i++) {
                timePoints.push(i);
                cpuData.push(Math.random() * 40 + 30);
                memoryData.push(Math.random() * 30 + 50);
            }
            
            const data = [
                {
                    x: timePoints,
                    y: cpuData,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'CPU',
                    line: { color: config.gauge_cpu_color, width: 3 }
                },
                {
                    x: timePoints,
                    y: memoryData,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Memória',
                    line: { color: config.gauge_memory_color, width: 3 }
                }
            ];
            
            const layout = {
                title: 'Histórico de Desempenho (Últimos 60 pontos)',
                height: 350,
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                font: { color: config.text_color },
                xaxis: { title: 'Tempo' },
                yaxis: { title: 'Uso (%)' },
                legend: { orientation: 'h' }
            };
            
            Plotly.newPlot('performance-chart', data, layout);
        }
        
        // Atualizar dados do sistema
        function updateSystemData(data) {
            // Atualizar métricas
            document.getElementById('cpu-value').textContent = data.cpu_usage.toFixed(1) + '%';
            document.getElementById('cpu-details').textContent = 
                `Núcleos: ${data.cpu_cores} | Threads: ${data.cpu_threads}`;
            
            document.getElementById('memory-value').textContent = data.memory.percent.toFixed(1) + '%';
            document.getElementById('memory-details').textContent = 
                `Usado: ${data.memory.used.toFixed(1)}GB / Total: ${data.memory.total.toFixed(1)}GB`;
            
            document.getElementById('disk-value').textContent = data.disk.percent.toFixed(1) + '%';
            document.getElementById('disk-details').textContent = 
                `Usado: ${data.disk.used.toFixed(1)}GB / Total: ${data.disk.total.toFixed(1)}GB`;
            
            if (data.gpu) {
                document.getElementById('gpu-value').textContent = data.gpu.load.toFixed(1) + '%';
                document.getElementById('gpu-details').textContent = 
                    `${data.gpu.name} | Memória: ${(data.gpu.memory.used/1024).toFixed(1)}/${(data.gpu.memory.total/1024).toFixed(1)}GB`;
            }
            
            // Atualizar informações do sistema
            document.getElementById('hostname').textContent = data.hostname;
            document.getElementById('os').textContent = data.os;
            document.getElementById('uptime').textContent = data.uptime;
            document.getElementById('processes').textContent = data.processes;
            
            document.getElementById('net-sent').textContent = data.network.sent.toFixed(2) + ' MB';
            document.getElementById('net-recv').textContent = data.network.recv.toFixed(2) + ' MB';
            document.getElementById('last-update').textContent = data.last_update;
            
            // Atualizar gráficos com cores personalizadas
            createGaugeChart('cpu-chart', data.cpu_usage, "Uso da CPU", config.gauge_cpu_color);
            createGaugeChart('memory-chart', data.memory.percent, "Uso de Memória", config.gauge_memory_color);
            createGaugeChart('disk-chart', data.disk.percent, "Uso de Disco", config.gauge_disk_color);
        }
        
        // Buscar dados do sistema periodicamente
        function fetchSystemData() {
            fetch('/system-data')
                .then(response => response.json())
                .then(data => {
                    updateSystemData(data);
                    setTimeout(fetchSystemData, 2000);
                })
                .catch(error => {
                    console.error('Erro ao buscar dados:', error);
                    setTimeout(fetchSystemData, 5000);
                });
        }
        
        // Gerenciamento de abas
        function setupTabs() {
            const tabButtons = document.querySelectorAll('.tab-btn');
            const tabContents = document.querySelectorAll('.tab-content');
            
            tabButtons.forEach(button => {
                button.addEventListener('click', function() {
                    const tabId = this.dataset.tab;
                    
                    // Atualizar botões
                    tabButtons.forEach(btn => btn.classList.remove('active'));
                    this.classList.add('active');
                    
                    // Atualizar conteúdo
                    tabContents.forEach(tab => tab.classList.remove('active'));
                    document.getElementById(tabId).classList.add('active');
                    
                    // Recriar gráfico de performance quando a aba é aberta
                    if (tabId === 'performance') {
                        createPerformanceChart();
                    }
                });
            });
        }
        
        // Configurar arrastar e soltar para arquitetura
        function setupDragAndDrop() {
            const components = document.querySelectorAll('.component-item');
            const canvas = document.getElementById('arch-canvas');
            
            components.forEach(component => {
                component.addEventListener('dragstart', function(e) {
                    e.dataTransfer.setData('text/plain', this.textContent);
                });
            });
            
            canvas.addEventListener('dragover', function(e) {
                e.preventDefault();
                this.style.border = '2px dashed ' + config.accent_color;
            });
            
            canvas.addEventListener('dragleave', function() {
                this.style.border = 'none';
            });
            
            canvas.addEventListener('drop', function(e) {
                e.preventDefault();
                this.style.border = 'none';
                
                const componentName = e.dataTransfer.getData('text/plain');
                const component = document.createElement('div');
                component.className = 'component-item';
                component.textContent = componentName;
                component.style.position = 'absolute';
                component.style.left = (e.clientX - this.getBoundingClientRect().left - 50) + 'px';
                component.style.top = (e.clientY - this.getBoundingClientRect().top - 25) + 'px';
                component.style.width = '100px';
                component.style.cursor = 'move';
                component.draggable = true;
                
                component.addEventListener('dragstart', function(ev) {
                    ev.dataTransfer.setData('text/plain', this.textContent);
                });
                
                this.appendChild(component);
            });
        }
        
        // Configurar code creator
        function setupCodeCreator() {
            document.getElementById('generate-code').addEventListener('click', function() {
                const description = document.getElementById('code-description').value;
                if (!description.trim()) {
                    alert('Por favor, descreva o código que deseja gerar.');
                    return;
                }
                
                // Simulação de geração de código por IA
                const generatedCode = `# Código gerado para: ${description}\n\ndef main():\n    print("Hello, World!")\n\nif __name__ == "__main__":\n    main()`;
                document.getElementById('generated-code').value = generatedCode;
            });
            
            document.getElementById('copy-code').addEventListener('click', function() {
                const code = document.getElementById('generated-code');
                code.select();
                document.execCommand('copy');
                alert('Código copiado para a área de transferência!');
            });
        }
        
        // Configurar personalização
        function setupCustomization() {
            // Toggle do tema
            document.getElementById('theme-toggle').addEventListener('change', function() {
                const theme = this.checked ? 'light' : 'dark';
                updateConfig({ theme });
            });
            
            // Atualização de cores
            const colorInputs = [
                'primary-color', 'secondary-color', 'accent-color',
                'gauge-cpu-color', 'gauge-memory-color', 'gauge-disk-color'
            ];
            
            colorInputs.forEach(id => {
                document.getElementById(id).addEventListener('input', function() {
                    const field = id.replace(/-/g, '_');
                    updateConfig({ [field]: this.value });
                });
            });
            
            // Salvar configurações
            document.getElementById('save-settings').addEventListener('click', function() {
                saveConfig();
                alert('Configurações salvas com sucesso!');
            });
            
            // Restaurar padrões
            document.getElementById('reset-settings').addEventListener('click', function() {
                if (confirm('Restaurar configurações padrão?')) {
                    resetConfig();
                }
            });
        }
        
        // Atualizar configuração local
        function updateConfig(newConfig) {
            Object.assign(config, newConfig);
            applyConfig();
        }
        
        // Aplicar configuração visual
        function applyConfig() {
            // Atualizar variáveis CSS
            document.documentElement.style.setProperty('--primary', config.primary_color);
            document.documentElement.style.setProperty('--secondary', config.secondary_color);
            document.documentElement.style.setProperty('--accent', config.accent_color);
            document.documentElement.style.setProperty('--text', config.text_color);
            document.documentElement.style.setProperty('--card', config.card_color);
            document.documentElement.style.setProperty('--font', config.font);
            
            // Atualizar tema
            if (config.theme === 'light') {
                document.body.classList.add('light-mode');
            } else {
                document.body.classList.remove('light-mode');
            }
            
            // Atualizar gráficos
            if (document.getElementById('cpu-chart').innerHTML !== '') {
                fetchSystemData();
            }
        }
        
        // Salvar configuração no servidor
        function saveConfig() {
            fetch('/save-config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(config)
            });
        }
        
        // Restaurar configurações padrão
        function resetConfig() {
            fetch('/reset-config', {
                method: 'POST'
            }).then(() => {
                location.reload();
            });
        }
        
        // Iniciar quando o documento estiver pronto
        document.addEventListener('DOMContentLoaded', function() {
            // Aplicar configuração inicial
            applyConfig();
            
            // Iniciar o carregamento dos dados
            fetchSystemData();
            
            // Configurar funcionalidades
            setupTabs();
            setupDragAndDrop();
            setupCodeCreator();
            setupCustomization();
            
            // Criar gráfico de performance inicial
            createPerformanceChart();
        });
    </script>
</body>
</html>
"""

def get_system_info():
    """Coleta informações detalhadas do sistema"""
    try:
        gpus = GPUtil.getGPUs()
        gpu_info = gpus[0] if gpus else None
    except:
        gpu_info = None
    
    # Formatar tempo de atividade
    uptime_seconds = time.time() - psutil.boot_time()
    uptime_str = str(datetime.timedelta(seconds=int(uptime_seconds))).split(".")[0]
    
    # Obter temperatura da CPU (simulação)
    cpu_temp = psutil.sensors_temperatures().get('coretemp', [{}])[0].current if hasattr(psutil, "sensors_temperatures") else 40
    
    return {
        'cpu_usage': psutil.cpu_percent(interval=1),
        'cpu_cores': psutil.cpu_count(logical=False),
        'cpu_threads': psutil.cpu_count(logical=True),
        'cpu_temp': cpu_temp,
        'memory': {
            'total': psutil.virtual_memory().total / (1024**3),
            'used': psutil.virtual_memory().used / (1024**3),
            'percent': psutil.virtual_memory().percent
        },
        'disk': {
            'total': psutil.disk_usage('/').total / (1024**3),
            'used': psutil.disk_usage('/').used / (1024**3),
            'percent': psutil.disk_usage('/').percent
        },
        'gpu': {
            'name': gpu_info.name if gpu_info else "N/A",
            'load': gpu_info.load * 100 if gpu_info else 0,
            'temp': gpu_info.temperature if gpu_info else 0,
            'memory': {
                'total': gpu_info.memoryTotal if gpu_info else 0,
                'used': gpu_info.memoryUsed if gpu_info else 0,
                'free': gpu_info.memoryFree if gpu_info else 0
            }
        } if gpu_info else None,
        'network': {
            'sent': psutil.net_io_counters().bytes_sent / (1024**2),
            'recv': psutil.net_io_counters().bytes_recv / (1024**2)
        },
        'hostname': socket.gethostname(),
        'os': f"{platform.system()} {platform.release()}",
        'uptime': uptime_str,
        'processes': len(psutil.pids()),
        'last_update': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'battery': psutil.sensors_battery().percent if hasattr(psutil, "sensors_battery") else 100
    }

@app.route('/')
def dashboard():
    global current_config
    current_config = load_config()
    return render_template_string(HTML_TEMPLATE, config=current_config)

@app.route('/system-data')
def system_data():
    return jsonify(get_system_info())

@app.route('/save-config', methods=['POST'])
def save_config_route():
    global current_config
    new_config = request.json
    current_config = {**current_config, **new_config}
    save_config(current_config)
    return jsonify({"status": "success"})

@app.route('/reset-config', methods=['POST'])
def reset_config():
    global current_config
    current_config = DEFAULT_CONFIG
    save_config(current_config)
    return jsonify({"status": "success"})

def run_server():
    app.run(host='127.0.0.1', port=5000)

# ========== CONFIGURAÇÃO DA JANELA DESKTOP ==========
def create_window():
    window = webview.create_window(
        'ARA OS CC - Desktop vers. 2.0',
        'http://127.0.0.1:5000',
        width=1300,
        height=850,
        resizable=True,
        text_select=True,
        frameless=False
    )
    webview.start()

if __name__ == '__main__':
    # Iniciar servidor Flask em uma thread separada
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Aguardar o servidor iniciar
    time.sleep(1)
    
    # Iniciar a janela desktop
    create_window()