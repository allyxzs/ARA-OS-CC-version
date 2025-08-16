import webview
import threading
import time
import os
import json
import uuid
import platform
import socket
import datetime
import psutil
import GPUtil
from flask import Flask, render_template_string, request, jsonify, Response

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
    "font": "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif",
    "automation_rules": []
}

# Carregar ou criar configurações
CONFIG_FILE = "ara_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Garantir que as novas configurações estejam presentes
                for key in DEFAULT_CONFIG:
                    if key not in config:
                        config[key] = DEFAULT_CONFIG[key]
                return config
        except:
            return DEFAULT_CONFIG
    return DEFAULT_CONFIG

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

# Configuração atual
current_config = load_config()

# Sistema de automação
AUTOMATION_TASKS = []
TASK_HISTORY = []

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
    cpu_temp = 40
    try:
        if hasattr(psutil, "sensors_temperatures"):
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                cpu_temp = max([x.current for x in temps['coretemp'] if x.current > 0])
    except:
        pass
    
    return {
        'cpu_usage': psutil.cpu_percent(interval=0.1),
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
            'recv': psutil.net_io_counters().bytes_recv / (1024**2),
            'speed': (psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv) / (1024**2) / 10
        },
        'hostname': socket.gethostname(),
        'os': f"{platform.system()} {platform.release()}",
        'uptime': uptime_str,
        'processes': len(psutil.pids()),
        'last_update': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'battery': psutil.sensors_battery().percent if hasattr(psutil, "sensors_battery") else 100
    }

def check_automation_rules():
    """Verifica e executa regras de automação"""
    global TASK_HISTORY, AUTOMATION_TASKS
    
    system_info = get_system_info()
    for rule in current_config.get('automation_rules', []):
        condition_met = False
        
        # Verificar condição
        if rule['condition_type'] == 'cpu_usage' and system_info['cpu_usage'] > float(rule['condition_value']):
            condition_met = True
        elif rule['condition_type'] == 'memory_usage' and system_info['memory']['percent'] > float(rule['condition_value']):
            condition_met = True
        elif rule['condition_type'] == 'disk_usage' and system_info['disk']['percent'] > float(rule['condition_value']):
            condition_met = True
        elif rule['condition_type'] == 'process_count' and system_info['processes'] > int(rule['condition_value']):
            condition_met = True
        
        # Executar ação se a condição for atendida
        if condition_met:
            # Registrar execução
            task_id = str(uuid.uuid4())
            task_event = {
                'id': task_id,
                'rule_id': rule['id'],
                'rule_name': rule['name'],
                'timestamp': datetime.datetime.now().isoformat(),
                'status': 'executed',
                'action': rule['action_type']
            }
            TASK_HISTORY.append(task_event)
            
            # Limitar histórico a 100 eventos
            if len(TASK_HISTORY) > 100:
                TASK_HISTORY = TASK_HISTORY[-100:]
            
            # Executar ação
            if rule['action_type'] == 'clean_temp_files':
                clean_temp_files()
            elif rule['action_type'] == 'restart_service':
                restart_service(rule.get('action_param', ''))
            elif rule['action_type'] == 'kill_processes':
                kill_processes(rule.get('action_param', ''))
            elif rule['action_type'] == 'notify':
                AUTOMATION_TASKS.append({
                    'id': task_id,
                    'message': rule.get('action_param', 'Condição de automação foi acionada'),
                    'type': 'info'
                })

def clean_temp_files():
    """Limpar arquivos temporários (simulação)"""
    # Em uma implementação real, isso limparia os diretórios temporários
    return {"status": "success", "message": "Arquivos temporários limpos"}

def restart_service(service_name):
    """Reiniciar um serviço (simulação)"""
    return {"status": "success", "message": f"Serviço {service_name} reiniciado"}

def kill_processes(process_name):
    """Encerrar processos (simulação)"""
    return {"status": "success", "message": f"Processos {process_name} encerrados"}

# Template HTML/CSS/JS completo com todas as funcionalidades
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ARA OS CC - Desktop vers. 2.0</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
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
        
        /* Automation */
        .automation-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }
        
        .automation-card {
            background: var(--card);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .automation-card h3 {
            color: var(--secondary);
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .form-group {
            margin-bottom: 15px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: #a0a0ff;
        }
        
        .light-mode .form-group label {
            color: #555577;
        }
        
        .form-group input, .form-group select, .form-group textarea {
            width: 100%;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid rgba(106, 90, 249, 0.3);
            background: rgba(20, 20, 45, 0.3);
            color: var(--text);
        }
        
        .light-mode .form-group input, 
        .light-mode .form-group select, 
        .light-mode .form-group textarea {
            background: rgba(230, 230, 245, 0.5);
            border: 1px solid rgba(200, 200, 220, 0.5);
        }
        
        .btn {
            background: linear-gradient(90deg, var(--primary), var(--secondary));
            border: none;
            border-radius: 8px;
            color: white;
            padding: 10px 15px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(106, 90, 249, 0.3);
        }
        
        .btn-danger {
            background: var(--danger);
        }
        
        .task-history {
            max-height: 300px;
            overflow-y: auto;
            margin-top: 15px;
            border: 1px solid rgba(106, 90, 249, 0.2);
            border-radius: 8px;
            padding: 10px;
        }
        
        .task-item {
            padding: 10px;
            border-bottom: 1px solid rgba(106, 90, 249, 0.1);
        }
        
        .task-item:last-child {
            border-bottom: none;
        }
        
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 8px;
            background: var(--card);
            border-left: 4px solid var(--accent);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
            z-index: 1000;
            max-width: 400px;
            display: flex;
            align-items: center;
            gap: 10px;
            transform: translateX(120%);
            transition: transform 0.3s ease;
        }
        
        .notification.show {
            transform: translateX(0);
        }
        
        .notification.success {
            border-left-color: var(--success);
        }
        
        .notification.warning {
            border-left-color: var(--warning);
        }
        
        .notification.danger {
            border-left-color: var(--danger);
        }
        
        .notification .close {
            margin-left: auto;
            cursor: pointer;
        }
    </style>
</head>
<body class="{{ 'light-mode' if config.theme == 'light' else '' }}">
    <div class="container">
        <div class="header">
            <div class="logo">
                <h1><i class="fas fa-rocket"></i> ARA Desktop Pro</h1>
            </div>
            <div class="tabs">
                <button class="tab-btn active" data-tab="dashboard">Dashboard</button>
                <button class="tab-btn" data-tab="performance">Performance</button>
                <button class="tab-btn" data-tab="automation">Automação</button>
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
            <div id="automation" class="tab-content">
                <div class="info-card">
                    <div class="info-title">Sistema de Automação</div>
                    <p>Configure regras para execução automática de tarefas</p>
                    
                    <div class="automation-container">
                        <!-- Regras de Automação -->
                        <div class="automation-card">
                            <h3><i class="fas fa-robot"></i> Regras de Automação</h3>
                            
                            <div class="form-group">
                                <label>Nome da Regra</label>
                                <input type="text" id="rule-name" placeholder="Ex: Limpeza quando memória alta">
                            </div>
                            
                            <div class="form-group">
                                <label>Condição</label>
                                <select id="rule-condition">
                                    <option value="cpu_usage">Uso de CPU acima de</option>
                                    <option value="memory_usage">Uso de Memória acima de</option>
                                    <option value="disk_usage">Uso de Disco acima de</option>
                                    <option value="process_count">Número de Processos acima de</option>
                                </select>
                                <input type="number" id="rule-value" placeholder="Valor" min="0" max="100" step="1">
                            </div>
                            
                            <div class="form-group">
                                <label>Ação</label>
                                <select id="rule-action">
                                    <option value="clean_temp_files">Limpar Arquivos Temporários</option>
                                    <option value="restart_service">Reiniciar Serviço</option>
                                    <option value="kill_processes">Encerrar Processos</option>
                                    <option value="notify">Enviar Notificação</option>
                                </select>
                                <input type="text" id="rule-action-param" placeholder="Parâmetro (opcional)" style="margin-top: 5px;">
                            </div>
                            
                            <button id="add-rule" class="btn">Adicionar Regra</button>
                        </div>
                        
                        <!-- Tarefas Agendadas -->
                        <div class="automation-card">
                            <h3><i class="fas fa-tasks"></i> Tarefas Agendadas</h3>
                            
                            <div class="form-group">
                                <label>Tipo de Tarefa</label>
                                <select id="task-type">
                                    <option value="cleanup">Limpeza de Sistema</option>
                                    <option value="backup">Backup de Dados</option>
                                    <option value="update">Atualização de Software</option>
                                </select>
                            </div>
                            
                            <div class="form-group">
                                <label>Agendamento</label>
                                <select id="task-schedule">
                                    <option value="daily">Diariamente</option>
                                    <option value="weekly">Semanalmente</option>
                                    <option value="monthly">Mensalmente</option>
                                </select>
                            </div>
                            
                            <div class="form-group">
                                <label>Hora de Execução</label>
                                <input type="time" id="task-time">
                            </div>
                            
                            <button id="schedule-task" class="btn">Agendar Tarefa</button>
                            
                            <div class="task-history">
                                <h4>Histórico de Execuções</h4>
                                <div id="task-history-list"></div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Tarefas de Manutenção -->
                    <div class="automation-card">
                        <h3><i class="fas fa-tools"></i> Ferramentas de Manutenção</h3>
                        
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px;">
                            <button id="clean-temp" class="btn">
                                <i class="fas fa-trash"></i> Limpar Arquivos Temporários
                            </button>
                            
                            <button id="optimize-disk" class="btn">
                                <i class="fas fa-hdd"></i> Otimizar Disco
                            </button>
                            
                            <button id="restart-system" class="btn">
                                <i class="fas fa-power-off"></i> Reiniciar Sistema
                            </button>
                        </div>
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
                        
                        <button id="save-settings" class="btn">Salvar Configurações</button>
                        <button id="reset-settings" class="btn btn-danger">Restaurar Padrões</button>
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
    
    <div id="notification-area"></div>

    <script>
        // Configuração atual
        const config = JSON.parse('{{ config | tojson | safe }}');
        let automationRules = config.automation_rules || [];
        
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
        
        // Configurar code creator
        function setupCodeCreator() {
            document.getElementById('generate-code').addEventListener('click', function() {
                const description = document.getElementById('code-description').value;
                if (!description.trim()) {
                    showNotification('Por favor, descreva o código que deseja gerar.', 'warning');
                    return;
                }
                
                // Simulação de geração de código por IA
                const generatedCode = `# Código gerado para: ${description}\n\ndef main():\n    print("Hello, World!")\n\nif __name__ == "__main__":\n    main()`;
                document.getElementById('generated-code').value = generatedCode;
                showNotification('Código gerado com sucesso!', 'success');
            });
            
            document.getElementById('copy-code').addEventListener('click', function() {
                const code = document.getElementById('generated-code');
                code.select();
                document.execCommand('copy');
                showNotification('Código copiado para a área de transferência!', 'success');
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
                showNotification('Configurações salvas com sucesso!', 'success');
            });
            
            // Restaurar padrões
            document.getElementById('reset-settings').addEventListener('click', function() {
                if (confirm('Restaurar configurações padrão?')) {
                    resetConfig();
                }
            });
        }
        
        // Configurar automação
        function setupAutomation() {
            // Adicionar regra
            document.getElementById('add-rule').addEventListener('click', function() {
                const name = document.getElementById('rule-name').value;
                const conditionType = document.getElementById('rule-condition').value;
                const conditionValue = document.getElementById('rule-value').value;
                const actionType = document.getElementById('rule-action').value;
                const actionParam = document.getElementById('rule-action-param').value;
                
                if (!name || !conditionValue) {
                    showNotification('Preencha todos os campos obrigatórios.', 'warning');
                    return;
                }
                
                const newRule = {
                    id: Date.now().toString(),
                    name,
                    condition_type: conditionType,
                    condition_value: conditionValue,
                    action_type: actionType,
                    action_param: actionParam
                };
                
                automationRules.push(newRule);
                updateConfig({ automation_rules: automationRules });
                
                document.getElementById('rule-name').value = '';
                document.getElementById('rule-value').value = '';
                document.getElementById('rule-action-param').value = '';
                
                showNotification('Regra de automação adicionada!', 'success');
            });
            
            // Agendar tarefa
            document.getElementById('schedule-task').addEventListener('click', function() {
                const taskType = document.getElementById('task-type').value;
                const schedule = document.getElementById('task-schedule').value;
                const time = document.getElementById('task-time').value;
                
                if (!time) {
                    showNotification('Selecione um horário para a tarefa.', 'warning');
                    return;
                }
                
                showNotification(`Tarefa "${taskType}" agendada para ${schedule} às ${time}`, 'success');
            });
            
            // Ferramentas de manutenção
            document.getElementById('clean-temp').addEventListener('click', function() {
                fetch('/clean-temp-files', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        showNotification(data.message, 'success');
                    });
            });
            
            document.getElementById('optimize-disk').addEventListener('click', function() {
                showNotification('Otimização de disco iniciada!', 'info');
            });
            
            document.getElementById('restart-system').addEventListener('click', function() {
                if (confirm('Tem certeza que deseja reiniciar o sistema?')) {
                    showNotification('Reinicialização do sistema em andamento...', 'warning');
                }
            });
            
            // Carregar histórico de tarefas
            fetch('/task-history')
                .then(response => response.json())
                .then(history => {
                    const historyList = document.getElementById('task-history-list');
                    historyList.innerHTML = '';
                    
                    history.slice(-10).reverse().forEach(task => {
                        const taskEl = document.createElement('div');
                        taskEl.className = 'task-item';
                        taskEl.innerHTML = `
                            <strong>${task.rule_name}</strong>
                            <div>Ação: ${task.action}</div>
                            <div>${new Date(task.timestamp).toLocaleString()}</div>
                        `;
                        historyList.appendChild(taskEl);
                    });
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
                // Recarregar a página para aplicar as configurações padrão
                location.reload();
            });
        }
        
        // Mostrar notificação
        function showNotification(message, type = 'info') {
            const notificationArea = document.getElementById('notification-area');
            const notificationId = 'notification-' + Date.now();
            
            const notification = document.createElement('div');
            notification.id = notificationId;
            notification.className = `notification ${type}`;
            notification.innerHTML = `
                <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'warning' ? 'fa-exclamation-triangle' : 'fa-info-circle'}"></i>
                <span>${message}</span>
                <span class="close" onclick="document.getElementById('${notificationId}').remove()">
                    <i class="fas fa-times"></i>
                </span>
            `;
            
            notificationArea.appendChild(notification);
            
            // Mostrar notificação
            setTimeout(() => {
                notification.classList.add('show');
            }, 10);
            
            // Remover notificação após 5 segundos
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => {
                    notification.remove();
                }, 300);
            }, 5000);
        }
        
        // Iniciar quando o documento estiver pronto
        document.addEventListener('DOMContentLoaded', function() {
            // Aplicar configuração inicial
            applyConfig();
            
            // Iniciar o carregamento dos dados
            fetchSystemData();
            
            // Configurar funcionalidades
            setupTabs();
            setupCodeCreator();
            setupCustomization();
            setupAutomation();
            
            // Criar gráfico de performance inicial
            createPerformanceChart();
            
            // Verificar regras de automação periodicamente
            setInterval(() => {
                fetch('/check-automation')
                    .then(response => response.json())
                    .then(tasks => {
                        tasks.forEach(task => {
                            showNotification(task.message, task.type);
                        });
                    });
            }, 10000);
        });
    </script>
</body>
</html>
"""

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

@app.route('/clean-temp-files', methods=['POST'])
def clean_temp_files_route():
    result = clean_temp_files()
    return jsonify(result)

@app.route('/task-history')
def task_history():
    global TASK_HISTORY
    return jsonify(TASK_HISTORY)

@app.route('/check-automation')
def check_automation():
    global AUTOMATION_TASKS
    tasks = AUTOMATION_TASKS.copy()
    AUTOMATION_TASKS = []
    return jsonify(tasks)

# Tarefa em segundo plano para verificar automações
def automation_worker():
    while True:
        check_automation_rules()
        time.sleep(10)

# Iniciar worker de automação em segundo plano
automation_thread = threading.Thread(target=automation_worker, daemon=True)
automation_thread.start()

def run_server():
    app.run(host='127.0.0.1', port=5000)

# ========== CONFIGURAÇÃO DA JANELA DESKTOP ==========
def create_window():
    window = webview.create_window(
        'ARA Desktop Pro - Advanced Analytics',
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