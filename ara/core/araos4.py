import webview
import threading
import time
from flask import Flask, render_template_string
import psutil
import GPUtil
import platform
import socket
import datetime

# ========== CONFIGURAÇÃO FLASK (SERVER LOCAL) ==========
app = Flask(__name__)

# Template HTML/CSS/JS completo com correções
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
            --primary: #6a5af9;
            --secondary: #d66efd;
            --accent: #4cc9f0;
            --dark: #0f0c29;
            --darker: #090616;
            --card: rgba(30, 30, 65, 0.7);
            --success: #00c9a7;
            --warning: #ff9e00;
            --danger: #ff3860;
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
            padding: 20px;
            overflow: hidden;
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
            padding-right: 5px; /* Espaço para a scrollbar */
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
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 0;
            border-bottom: 1px solid rgba(106, 90, 249, 0.5);
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
        
        .tab-btn:hover {
            color: var(--secondary);
            background: rgba(214, 110, 253, 0.1);
        }
        
        .tab-btn.active {
            color: var(--secondary);
            background: rgba(214, 110, 253, 0.15);
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
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(106, 90, 249, 0.3);
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(106, 90, 249, 0.4);
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
        
        .metric-details {
            font-size: 12px;
            color: #a0a0ff;
            margin-top: 10px;
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
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(106, 90, 249, 0.3);
            height: 300px;
            /* Garante que o gráfico não cresça além do contêiner */
            overflow: hidden;
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
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(106, 90, 249, 0.3);
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
        
        .status-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            background: rgba(0, 201, 167, 0.2);
            color: var(--success);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">
                <h1>🚀 ARA OS</h1>
            </div>
            <div class="tabs">
                <button class="tab-btn active">Dashboard</button>
                <button class="tab-btn">Performance</button>
                <button class="tab-btn">Configurações</button>
            </div>
        </div>
        
        <div class="content">
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
        
        <div class="footer">
            <div>ARA Desktop v2.0</div>
            <div>ARA OS CC</div>
            <div>Desenvolvido com ❤️ por Tottenham A.C.</div>
        </div>
    </div>

    <script>
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
                font: { color: "#a0a0ff" },
                // FUNDO TRANSPARENTE PARA MANTER A ESTÉTICA
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)'
            };
            
            // Destruir gráfico existente antes de criar um novo
            const element = document.getElementById(elementId);
            Plotly.purge(element);
            
            // Criar novo gráfico com tamanho fixo
            Plotly.newPlot(element, data, layout, {
                displayModeBar: false, // Oculta a barra de ferramentas
                staticPlot: false
            });
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
            
            // Atualizar gráficos com fundo transparente
            createGaugeChart('cpu-chart', data.cpu_usage, "Uso da CPU", "#6a5af9");
            createGaugeChart('memory-chart', data.memory.percent, "Uso de Memória", "#d66efd");
            createGaugeChart('disk-chart', data.disk.percent, "Uso de Disco", "#4cc9f0");
        }
        
        // Buscar dados do sistema periodicamente
        function fetchSystemData() {
            fetch('/system-data')
                .then(response => response.json())
                .then(data => {
                    updateSystemData(data);
                    setTimeout(fetchSystemData, 2000); // Atualizar a cada 2 segundos
                })
                .catch(error => {
                    console.error('Erro ao buscar dados:', error);
                    setTimeout(fetchSystemData, 5000); // Tentar novamente após 5 segundos
                });
        }
        
        // Iniciar quando o documento estiver pronto
        document.addEventListener('DOMContentLoaded', function() {
            // Iniciar o carregamento dos dados
            fetchSystemData();
            
            // Configurar botões de tab
            const tabButtons = document.querySelectorAll('.tab-btn');
            tabButtons.forEach(button => {
                button.addEventListener('click', function() {
                    tabButtons.forEach(btn => btn.classList.remove('active'));
                    this.classList.add('active');
                });
            });
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
    
    return {
        'cpu_usage': psutil.cpu_percent(interval=1),
        'cpu_cores': psutil.cpu_count(logical=False),
        'cpu_threads': psutil.cpu_count(logical=True),
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
        'last_update': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

@app.route('/')
def dashboard():
    return render_template_string(HTML_TEMPLATE)

@app.route('/system-data')
def system_data():
    return get_system_info()

def run_server():
    app.run(host='127.0.0.1', port=5000)

# ========== CONFIGURAÇÃO DA JANELA DESKTOP ==========
def create_window():
    window = webview.create_window(
        'ARA OS CC - Desktop vers. 2.0',
        'http://127.0.0.1:5000',
        width=1200,
        height=800,
        resizable=True,
        text_select=True,
        # Forçar tema escuro no Windows
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