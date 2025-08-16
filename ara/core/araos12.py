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
import random
from flask import Flask, render_template_string, request, jsonify
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from googletrans import Translator

# ========== SISTEMA DE IDIOMAS ==========
TRANSLATIONS = {
    "portuguese": {
        "dashboard": "Dashboard",
        "architecture": "Architecture",
        "code_creator": "Code Creator",
        "chat": "Chat",
        "settings": "Configurações",
        "cpu": "CPU",
        "memory": "MEMÓRIA",
        "disk": "DISCO",
        "gpu": "GPU",
        "hostname": "Hostname",
        "os": "Sistema Operacional",
        "uptime": "Tempo de Atividade",
        "processes": "Processos Ativos",
        "net_sent": "Enviados",
        "net_recv": "Recebidos",
        "status": "Status",
        "last_update": "Última Atualização",
        "performance_history": "Histórico de Desempenho",
        "process_count": "Processos",
        "temperature": "Temperatura",
        "network_speed": "Rede",
        "battery": "Bateria",
        "automation_system": "Sistema de Automação",
        "automation_rules": "Regras de Automação",
        "rule_name": "Nome da Regra",
        "rule_name_placeholder": "Ex: Limpeza quando memória alta",
        "condition": "Condição",
        "action": "Ação",
        "add_rule": "Adicionar Regra",
        "scheduled_tasks": "Tarefas Agendadas",
        "task_type": "Tipo de Tarefa",
        "schedule": "Agendamento",
        "execution_time": "Hora de Execução",
        "schedule_task": "Agendar Tarefa",
        "execution_history": "Histórico de Execuções",
        "maintenance_tools": "Ferramentas de Manutenção",
        "clean_temp_files": "Limpar Arquivos Temporários",
        "optimize_disk": "Otimizar Disco",
        "restart_system": "Reiniciar Sistema",
        "code_creator_title": "Code Creator",
        "code_creator_description": "Crie código com assistência de IA - Um mini VSCode integrado",
        "ai_assistant": "Assistente de IA",
        "code_description_placeholder": "Descreva o código que deseja gerar...",
        "generate_code": "Gerar Código",
        "generated_code": "Código Gerado",
        "copy_code": "Copiar Código",
        "save_code": "Salvar Arquivo",
        "format_code": "Formatar",
        "chat_title": "Chat ARA",
        "chat_description": "Converse com a IA da ARA OS para tirar dúvidas e obter assistência",
        "type_message": "Digite sua mensagem...",
        "appearance_settings": "Configurações de Aparência",
        "dark_mode": "Modo Escuro",
        "light_mode": "Modo Claro",
        "language": "Idioma",
        "color_customization": "Personalização de Cores",
        "primary_color": "Cor Primária",
        "secondary_color": "Cor Secundária",
        "accent_color": "Cor de Destaque",
        "gauge_cpu_color": "Cor do Gráfico (CPU)",
        "gauge_memory_color": "Cor do Gráfico (Memória)",
        "gauge_disk_color": "Cor do Gráfico (Disco)",
        "save_settings": "Salvar Configurações",
        "reset_settings": "Restaurar Padrões",
        "version": "ARA OS v3.5",
        "developed_by": "Desenvolvido com ❤️ por Tottenham A.C.",
        "system_status": "Status:",
        "operational": "Operacional",
        "cores_label": "Núcleos",
        "threads_label": "Threads",
        "used_label": "Usado",
        "total_label": "Total",
        "gpu_memory_label": "Memória",
        "gpu_name_label": "Nome",
        "gpu_temp_label": "Temperatura",
        "notifications": "Notificações",
        "cleanup_success": "Arquivos temporários limpos com sucesso!",
        "optimization_started": "Otimização de disco iniciada!",
        "restart_warning": "Reinicialização do sistema em andamento...",
        "rule_added": "Regra de automação adicionada!",
        "fill_required": "Preencha todos os campos obrigatórios.",
        "task_scheduled": "Tarefa agendada com sucesso!",
        "code_generated": "Código gerado com sucesso!",
        "code_copied": "Código copiado para a área de transferência!",
        "code_formatted": "Código formatado!",
        "settings_saved": "Configurações salvas com sucesso!",
        "settings_reset": "Configurações restauradas para padrão!",
        "reset_confirm": "Restaurar configurações padrão?",
        "ai_applied": "Assistência de IA aplicada!",
        "welcome_message": "Olá! Sou a ARA, sua assistente de sistema. Como posso ajudar?",
        "gpu_not_detected": "Nenhuma GPU detectada",
        "cpu_usage_above": "Uso de CPU acima de",
        "memory_usage_above": "Uso de Memória acima de",
        "disk_usage_above": "Uso de Disco acima de",
        "process_count_above": "Número de Processos acima de",
        "cleanup": "Limpeza de Sistema",
        "backup": "Backup de Dados",
        "update": "Atualização de Software",
        "daily": "Diariamente",
        "weekly": "Semanalmente",
        "monthly": "Mensalmente",
        "value": "Valor",
        "parameter_optional": "Parâmetro (opcional)",
        "upload": "Upload",
        "download": "Download",
        "time": "Tempo",
        "usage_percent": "Uso (%)",
        "system_information": "Informações do Sistema",
        "network_status": "Status da Rede",
        "select_time": "Selecione um horário para a tarefa",
        "at": "às",
        "fill_description": "Por favor, descreva o código que deseja gerar",
        "code_placeholder": "O código aparecerá aqui...",
        "restart_confirm": "Tem certeza que deseja reiniciar o sistema?",
        "restart_service": "Reiniciar Serviço",
        "kill_processes": "Encerrar Processos",
        "notify": "Notificar",
        "typing_indicator": "ARA está digitando...",
        "online_status": "Online"
    },
    "english": {
        "dashboard": "Dashboard",
        "architecture": "Architecture",
        "code_creator": "Code Creator",
        "chat": "Chat",
        "settings": "Settings",
        "cpu": "CPU",
        "memory": "MEMORY",
        "disk": "DISK",
        "gpu": "GPU",
        "hostname": "Hostname",
        "os": "Operating System",
        "uptime": "Uptime",
        "processes": "Active Processes",
        "net_sent": "Sent",
        "net_recv": "Received",
        "status": "Status",
        "last_update": "Last Update",
        "performance_history": "Performance History",
        "process_count": "Processes",
        "temperature": "Temperature",
        "network_speed": "Network",
        "battery": "Battery",
        "automation_system": "Automation System",
        "automation_rules": "Automation Rules",
        "rule_name": "Rule Name",
        "rule_name_placeholder": "Ex: Cleanup when high memory",
        "condition": "Condition",
        "action": "Action",
        "add_rule": "Add Rule",
        "scheduled_tasks": "Scheduled Tasks",
        "task_type": "Task Type",
        "schedule": "Schedule",
        "execution_time": "Execution Time",
        "schedule_task": "Schedule Task",
        "execution_history": "Execution History",
        "maintenance_tools": "Maintenance Tools",
        "clean_temp_files": "Clean Temp Files",
        "optimize_disk": "Optimize Disk",
        "restart_system": "Restart System",
        "code_creator_title": "Code Creator",
        "code_creator_description": "Create code with AI assistance - An integrated mini VSCode",
        "ai_assistant": "AI Assistant",
        "code_description_placeholder": "Describe the code you want to generate...",
        "generate_code": "Generate Code",
        "generated_code": "Generated Code",
        "copy_code": "Copy Code",
        "save_code": "Save File",
        "format_code": "Format",
        "chat_title": "ARA Chat",
        "chat_description": "Chat with ARA OS AI to get help and assistance",
        "type_message": "Type your message...",
        "appearance_settings": "Appearance Settings",
        "dark_mode": "Dark Mode",
        "light_mode": "Light Mode",
        "language": "Language",
        "color_customization": "Color Customization",
        "primary_color": "Primary Color",
        "secondary_color": "Secondary Color",
        "accent_color": "Accent Color",
        "gauge_cpu_color": "Gauge Color (CPU)",
        "gauge_memory_color": "Gauge Color (Memory)",
        "gauge_disk_color": "Gauge Color (Disk)",
        "save_settings": "Save Settings",
        "reset_settings": "Reset to Defaults",
        "version": "ARA OS v3.5",
        "developed_by": "Developed with ❤️ by Tottenham A.C.",
        "system_status": "Status:",
        "operational": "Operational",
        "cores_label": "Cores",
        "threads_label": "Threads",
        "used_label": "Used",
        "total_label": "Total",
        "gpu_memory_label": "Memory",
        "gpu_name_label": "Name",
        "gpu_temp_label": "Temperature",
        "notifications": "Notifications",
        "cleanup_success": "Temporary files cleaned successfully!",
        "optimization_started": "Disk optimization started!",
        "restart_warning": "System restart in progress...",
        "rule_added": "Automation rule added!",
        "fill_required": "Please fill all required fields.",
        "task_scheduled": "Task scheduled successfully!",
        "code_generated": "Code generated successfully!",
        "code_copied": "Code copied to clipboard!",
        "code_formatted": "Code formatted!",
        "settings_saved": "Settings saved successfully!",
        "settings_reset": "Settings restored to default!",
        "reset_confirm": "Restore default settings?",
        "ai_applied": "AI assistance applied!",
        "welcome_message": "Hello! I'm ARA, your system assistant. How can I help you?",
        "gpu_not_detected": "No GPU detected",
        "cpu_usage_above": "CPU usage above",
        "memory_usage_above": "Memory usage above",
        "disk_usage_above": "Disk usage above",
        "process_count_above": "Process count above",
        "cleanup": "System Cleanup",
        "backup": "Data Backup",
        "update": "Software Update",
        "daily": "Daily",
        "weekly": "Weekly",
        "monthly": "Monthly",
        "value": "Value",
        "parameter_optional": "Parameter (optional)",
        "upload": "Upload",
        "download": "Download",
        "time": "Time",
        "usage_percent": "Usage (%)",
        "system_information": "System Information",
        "network_status": "Network Status",
        "select_time": "Select a time for the task",
        "at": "at",
        "fill_description": "Please describe the code you want to generate",
        "code_placeholder": "Code will appear here...",
        "restart_confirm": "Are you sure you want to restart the system?",
        "restart_service": "Restart Service",
        "kill_processes": "Kill Processes",
        "notify": "Notify",
        "typing_indicator": "ARA is typing...",
        "online_status": "Online"
    },
    "french": {
        "dashboard": "Tableau de bord",
        "architecture": "Architecture",
        "code_creator": "Créateur de code",
        "chat": "Chat",
        "settings": "Paramètres",
        "cpu": "CPU",
        "memory": "MÉMOIRE",
        "disk": "DISQUE",
        "gpu": "GPU",
        "hostname": "Nom d'hôte",
        "os": "Système d'exploitation",
        "uptime": "Temps de fonctionnement",
        "processes": "Processus actifs",
        "net_sent": "Envoyé",
        "net_recv": "Reçu",
        "status": "Statut",
        "last_update": "Dernière mise à jour",
        "performance_history": "Historique des performances",
        "process_count": "Processus",
        "temperature": "Température",
        "network_speed": "Réseau",
        "battery": "Batterie",
        "automation_system": "Système d'automatisation",
        "automation_rules": "Règles d'automatisation",
        "rule_name": "Nom de la règle",
        "rule_name_placeholder": "Ex: Nettoyage quand mémoire élevée",
        "condition": "Condition",
        "action": "Action",
        "add_rule": "Ajouter une règle",
        "scheduled_tasks": "Tâches planifiées",
        "task_type": "Type de tâche",
        "schedule": "Planification",
        "execution_time": "Heure d'exécution",
        "schedule_task": "Planifier la tâche",
        "execution_history": "Historique d'exécution",
        "maintenance_tools": "Outils de maintenance",
        "clean_temp_files": "Nettoyer les fichiers temporaires",
        "optimize_disk": "Optimiser le disque",
        "restart_system": "Redémarrer le système",
        "code_creator_title": "Créateur de code",
        "code_creator_description": "Créez du code avec assistance IA - Un mini VSCode intégré",
        "ai_assistant": "Assistant IA",
        "code_description_placeholder": "Décrivez le code que vous souhaitez générer...",
        "generate_code": "Générer du code",
        "generated_code": "Code généré",
        "copy_code": "Copier le code",
        "save_code": "Enregistrer le fichier",
        "format_code": "Formater",
        "chat_title": "Chat ARA",
        "chat_description": "Discutez avec l'IA d'ARA OS pour obtenir de l'aide et de l'assistance",
        "type_message": "Tapez votre message...",
        "appearance_settings": "Paramètres d'apparence",
        "dark_mode": "Mode sombre",
        "light_mode": "Mode clair",
        "language": "Langue",
        "color_customization": "Personnalisation des couleurs",
        "primary_color": "Couleur primaire",
        "secondary_color": "Couleur secondaire",
        "accent_color": "Couleur d'accentuation",
        "gauge_cpu_color": "Couleur du graphique (CPU)",
        "gauge_memory_color": "Couleur du graphique (Mémoire)",
        "gauge_disk_color": "Couleur du graphique (Disque)",
        "save_settings": "Enregistrer les paramètres",
        "reset_settings": "Restaurer les paramètres par défaut",
        "version": "ARA OS v3.5",
        "developed_by": "Développé avec ❤️ par Tottenham A.C.",
        "system_status": "Statut:",
        "operational": "Opérationnel",
        "cores_label": "Cœurs",
        "threads_label": "Threads",
        "used_label": "Utilisé",
        "total_label": "Total",
        "gpu_memory_label": "Mémoire",
        "gpu_name_label": "Nom",
        "gpu_temp_label": "Température",
        "notifications": "Notifications",
        "cleanup_success": "Fichiers temporaires nettoyés avec succès !",
        "optimization_started": "Optimisation du disque démarrée !",
        "restart_warning": "Redémarrage du système en cours...",
        "rule_added": "Règle d'automatisation ajoutée !",
        "fill_required": "Veuillez remplir tous les champs obligatoires.",
        "task_scheduled": "Tâche planifiée avec succès !",
        "code_generated": "Code généré avec succès !",
        "code_copied": "Code copié dans le presse-papiers !",
        "code_formatted": "Code formaté !",
        "settings_saved": "Paramètres enregistrés avec succès !",
        "settings_reset": "Paramètres restaurés par défault !",
        "reset_confirm": "Restaurer les paramètres par défaut ?",
        "ai_applied": "Assistance IA appliquée !",
        "welcome_message": "Bonjour ! Je suis ARA, votre assistant système. Comment puis-je vous aider ?",
        "gpu_not_detected": "Aucun GPU détecté",
        "cpu_usage_above": "Utilisation CPU au-dessus de",
        "memory_usage_above": "Utilisation mémoire au-dessus de",
        "disk_usage_above": "Utilisation disque au-dessus de",
        "process_count_above": "Nombre de processus au-dessus de",
        "cleanup": "Nettoyage système",
        "backup": "Sauvegarde de données",
        "update": "Mise à jour logicielle",
        "daily": "Quotidien",
        "weekly": "Hebdomadaire",
        "monthly": "Mensuel",
        "value": "Valeur",
        "parameter_optional": "Paramètre (optionnel)",
        "upload": "Upload",
        "download": "Download",
        "time": "Temps",
        "usage_percent": "Utilisation (%)",
        "system_information": "Informations système",
        "network_status": "Statut réseau",
        "select_time": "Sélectionnez une heure pour la tâche",
        "at": "à",
        "fill_description": "Veuillez décrire le code que vous souhaitez générer",
        "code_placeholder": "Le code apparaîtra ici...",
        "restart_confirm": "Êtes-vous sûr de vouloir redémarrer le système ?",
        "restart_service": "Redémarrer le service",
        "kill_processes": "Arrêter les processus",
        "notify": "Notifier",
        "typing_indicator": "ARA est en train d'écrire...",
        "online_status": "En ligne"
    },
    "italian": {
        "dashboard": "Dashboard",
        "architecture": "Architettura",
        "code_creator": "Creatore di codice",
        "chat": "Chat",
        "settings": "Impostazioni",
        "cpu": "CPU",
        "memory": "MEMORIA",
        "disk": "DISCO",
        "gpu": "GPU",
        "hostname": "Nome host",
        "os": "Sistema operativo",
        "uptime": "Tempo di attività",
        "processes": "Processi attivi",
        "net_sent": "Inviati",
        "net_recv": "Ricevuti",
        "status": "Stato",
        "last_update": "Ultimo aggiornamento",
        "performance_history": "Cronologia prestazioni",
        "process_count": "Processi",
        "temperature": "Temperatura",
        "network_speed": "Rete",
        "battery": "Batteria",
        "automation_system": "Sistema di automazione",
        "automation_rules": "Regole di automazione",
        "rule_name": "Nome regola",
        "rule_name_placeholder": "Es: Pulizia quando memoria alta",
        "condition": "Condizione",
        "action": "Azione",
        "add_rule": "Aggiungi regola",
        "scheduled_tasks": "Attività pianificate",
        "task_type": "Tipo di attività",
        "schedule": "Pianificazione",
        "execution_time": "Ora di esecuzione",
        "schedule_task": "Pianifica attività",
        "execution_history": "Cronologia esecuzioni",
        "maintenance_tools": "Strumenti di manutenzione",
        "clean_temp_files": "Pulisci file temporanei",
        "optimize_disk": "Ottimizza disco",
        "restart_system": "Riavvia sistema",
        "code_creator_title": "Creatore di codice",
        "code_creator_description": "Crea codice con assistenza IA - Un mini VSCode integrato",
        "ai_assistant": "Assistente IA",
        "code_description_placeholder": "Descrivi il codice che vuoi generare...",
        "generate_code": "Genera codice",
        "generated_code": "Codice generato",
        "copy_code": "Copia codice",
        "save_code": "Salva file",
        "format_code": "Formatta",
        "chat_title": "Chat ARA",
        "chat_description": "Chatta con l'IA di ARA OS per ottenere aiuto e assistenza",
        "type_message": "Digita il tuo messaggio...",
        "appearance_settings": "Impostazioni aspetto",
        "dark_mode": "Modalità scura",
        "light_mode": "Modalità chiara",
        "language": "Lingua",
        "color_customization": "Personalizzazione colori",
        "primary_color": "Colore primario",
        "secondary_color": "Colore secondario",
        "accent_color": "Colore di accento",
        "gauge_cpu_color": "Colore grafico (CPU)",
        "gauge_memory_color": "Colore grafico (Memoria)",
        "gauge_disk_color": "Colore grafico (Disco)",
        "save_settings": "Salva impostazioni",
        "reset_settings": "Ripristina predefiniti",
        "version": "ARA OS v3.5",
        "developed_by": "Sviluppato con ❤️ da Tottenham A.C.",
        "system_status": "Stato:",
        "operational": "Operativo",
        "cores_label": "Core",
        "threads_label": "Thread",
        "used_label": "Usato",
        "total_label": "Totale",
        "gpu_memory_label": "Memoria",
        "gpu_name_label": "Nome",
        "gpu_temp_label": "Temperatura",
        "notifications": "Notifiche",
        "cleanup_success": "File temporanei puliti con successo!",
        "optimization_started": "Ottimizzazione disco avviata!",
        "restart_warning": "Riavvio sistema in corso...",
        "rule_added": "Regola automazione aggiunta!",
        "fill_required": "Compila tutti i campi obbligatori.",
        "task_scheduled": "Attività pianificata con successo!",
        "code_generated": "Codice generato con successo!",
        "code_copied": "Codice copiato negli appunti!",
        "code_formatted": "Codice formattato!",
        "settings_saved": "Impostazioni salvate con successo!",
        "settings_reset": "Impostazioni ripristinate ai valori predefiniti!",
        "reset_confirm": "Ripristinare le impostazioni predefinite?",
        "ai_applied": "Assistenza IA applicata!",
        "welcome_message": "Ciao! Sono ARA, il tuo assistente di sistema. Come posso aiutarti?",
        "gpu_not_detected": "Nessuna GPU rilevata",
        "cpu_usage_above": "Uso CPU sopra",
        "memory_usage_above": "Uso memoria sopra",
        "disk_usage_above": "Uso disco sopra",
        "process_count_above": "Conteggio processi sopra",
        "cleanup": "Pulizia sistema",
        "backup": "Backup dati",
        "update": "Aggiornamento software",
        "daily": "Quotidiano",
        "weekly": "Settimanale",
        "monthly": "Mensile",
        "value": "Valore",
        "parameter_optional": "Parametro (opzionale)",
        "upload": "Upload",
        "download": "Download",
        "time": "Tempo",
        "usage_percent": "Utilizzo (%)",
        "system_information": "Informazioni sistema",
        "network_status": "Stato rete",
        "select_time": "Seleziona un orario per l'attività",
        "at": "alle",
        "fill_description": "Per favore descrivi il codice che desideri generare",
        "code_placeholder": "Il codice apparirà qui...",
        "restart_confirm": "Sei sicuro di voler riavviare il sistema?",
        "restart_service": "Riavvia servizio",
        "kill_processes": "Termina processi",
        "notify": "Notifica",
        "typing_indicator": "ARA sta scrivendo...",
        "online_status": "Online"
    }
}

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
    "automation_rules": [],
    "language": "portuguese"
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

# Inicializar chatbot
chatbot = ChatBot(
    'ARA',
    storage_adapter='chatterbot.storage.SQLStorageAdapter',
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.BestMatch',
            'default_response': 'Desculpe, não entendi. Pode reformular?',
            'maximum_similarity_threshold': 0.90
        }
    ],
    database_uri='sqlite:///database.sqlite3'
)

# Treinar o chatbot
trainer = ChatterBotCorpusTrainer(chatbot)
trainer.train("chatterbot.corpus.portuguese")
trainer.train("chatterbot.corpus.english")
trainer.train("chatterbot.corpus.french")
trainer.train("chatterbot.corpus.italian")

# Inicializar tradutor
translator = Translator()

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
    
    # Obter informações de rede com tratamento de erro
    net_sent = 0
    net_recv = 0
    try:
        net_sent = psutil.net_io_counters().bytes_sent / (1024**2)
        net_recv = psutil.net_io_counters().bytes_recv / (1024**2)
    except:
        pass
    
    # Obter bateria com tratamento de erro
    battery_percent = 100
    try:
        if hasattr(psutil, "sensors_battery"):
            battery = psutil.sensors_battery()
            battery_percent = battery.percent if battery else 100
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
            'sent': net_sent,
            'recv': net_recv,
            'speed': (net_sent + net_recv) / (1024**2) / 10
        },
        'hostname': socket.gethostname(),
        'os': f"{platform.system()} {platform.release()}",
        'uptime': uptime_str,
        'processes': len(psutil.pids()),
        'last_update': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'battery': battery_percent
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

def generate_code(description, language="Python"):
    """Gera código com base na descrição usando modelo de IA"""
    # Em uma implementação real, isso se conectaria a um modelo de IA
    # Aqui usamos templates básicos com preenchimento aleatório
    
    if language == "Python":
        return f"""# Código gerado para: {description}
import os
import sys

def main():
    print("Hello, World!")
    # {description}
    
if __name__ == "__main__":
    main()
"""
    elif language == "JavaScript":
        return f"""// Código gerado para: {description}
function main() {{
    console.log("Hello, World!");
    // {description}
}}

main();
"""
    else:
        return f"// Código gerado para: {description}\n// Suporte para {language} em breve!"

# Template HTML/CSS/JS completo com todas as funcionalidades
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="{{ config.language }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ARA OS - Desktop vers. 3.5</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/theme/dracula.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/python/python.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/javascript/javascript.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/htmlmixed/htmlmixed.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/css/css.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/clike/clike.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/addon/edit/closebrackets.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/addon/hint/show-hint.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/addon/hint/anyword-hint.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/addon/hint/show-hint.min.css">
    
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
            height: 250px;
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
        .code-editor-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
            height: 500px;
        }
        
        .editor-section {
            background: var(--card);
            border-radius: 15px;
            padding: 15px;
            display: flex;
            flex-direction: column;
            height: 100%;
        }
        
        .editor-section h3 {
            color: var(--secondary);
            margin-bottom: 10px;
        }
        
        .editor-controls {
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
        }
        
        .editor-controls select, .editor-controls button {
            padding: 8px 12px;
            border-radius: 6px;
            background: rgba(20, 20, 45, 0.3);
            color: var(--text);
            border: 1px solid rgba(106, 90, 249, 0.3);
        }
        
        .light-mode .editor-controls select, 
        .light-mode .editor-controls button {
            background: rgba(230, 230, 245, 0.5);
            border: 1px solid rgba(200, 200, 220, 0.5);
        }
        
        .editor-container {
            flex: 1;
            border: 1px solid rgba(106, 90, 249, 0.3);
            border-radius: 8px;
            overflow: hidden;
        }
        
        .CodeMirror {
            height: 100% !important;
            font-family: monospace;
            font-size: 14px;
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
        
        /* Chat UI */
        .chat-container {
            display: flex;
            flex-direction: column;
            height: 500px;
            background: var(--card);
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        }
        
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 15px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .message {
            max-width: 80%;
            padding: 12px 16px;
            border-radius: 18px;
            line-height: 1.4;
            position: relative;
            white-space: pre-wrap;
        }
        
        .user-message {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            align-self: flex-end;
            border-bottom-right-radius: 4px;
        }
        
        .bot-message {
            background: rgba(76, 201, 240, 0.2);
            align-self: flex-start;
            border-bottom-left-radius: 4px;
        }
        
        .typing-indicator {
            background: rgba(76, 201, 240, 0.2);
            align-self: flex-start;
            border-bottom-left-radius: 4px;
            padding: 8px 16px;
            display: none;
        }
        
        .typing-indicator span {
            height: 8px;
            width: 8px;
            float: left;
            margin: 0 1px;
            background-color: #9E9EA1;
            display: block;
            border-radius: 50%;
            opacity: 0.4;
        }
        
        .typing-indicator span:nth-of-type(1) {
            animation: typing 1s infinite;
        }
        
        .typing-indicator span:nth-of-type(2) {
            animation: typing 1s infinite 0.2s;
        }
        
        .typing-indicator span:nth-of-type(3) {
            animation: typing 1s infinite 0.4s;
        }
        
        @keyframes typing {
            0%, 100% {
                transform: translateY(0);
                opacity: 0.4;
            }
            50% {
                transform: translateY(-5px);
                opacity: 1;
            }
        }
        
        .chat-input-area {
            display: flex;
            padding: 15px;
            border-top: 1px solid rgba(106, 90, 249, 0.2);
            background: rgba(20, 20, 45, 0.3);
        }
        
        .chat-input {
            flex: 1;
            padding: 12px 15px;
            border-radius: 25px;
            border: 1px solid rgba(106, 90, 249, 0.3);
            background: rgba(30, 30, 50, 0.5);
            color: var(--text);
            outline: none;
        }
        
        .light-mode .chat-input {
            background: rgba(240, 240, 250, 0.7);
        }
        
        .send-btn {
            margin-left: 10px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            border: none;
            border-radius: 50%;
            width: 45px;
            height: 45px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            color: white;
        }
        
        .online-indicator {
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 12px;
            color: var(--success);
            margin-left: 10px;
        }
        
        .online-dot {
            width: 8px;
            height: 8px;
            background-color: var(--success);
            border-radius: 50%;
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
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
        
        /* Idioma selector */
        .language-selector {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .language-selector select {
            padding: 8px 12px;
            border-radius: 6px;
            background: rgba(20, 20, 45, 0.3);
            color: var(--text);
            border: 1px solid rgba(106, 90, 249, 0.3);
        }
        
        .light-mode .language-selector select {
            background: rgba(230, 230, 245, 0.5);
            border: 1px solid rgba(200, 200, 220, 0.5);
        }
    </style>
</head>
<body class="{{ 'light-mode' if config.theme == 'light' else '' }}">
    <div class="container">
        <div class="header">
            <div class="logo">
                <h1><i class="fas fa-rocket"></i> ARA OS</h1>
            </div>
            <div class="tabs">
                <button class="tab-btn active" data-tab="dashboard">{{ translations.dashboard }}</button>
                <button class="tab-btn" data-tab="architecture">{{ translations.architecture }}</button>
                <button class="tab-btn" data-tab="code-creator">{{ translations.code_creator }}</button>
                <button class="tab-btn" data-tab="chat">{{ translations.chat }}</button>
                <button class="tab-btn" data-tab="settings">{{ translations.settings }}</button>
            </div>
        </div>
        
        <div class="content">
            <!-- Dashboard Tab (Agora com conteúdo completo) -->
            <div id="dashboard" class="tab-content active">
                <div class="metric-grid">
                    <div class="metric-card">
                        <div class="metric-title">{{ translations.cpu }}</div>
                        <div class="metric-value" id="cpu-value">0%</div>
                        <div class="metric-details" id="cpu-details">{{ translations.cores_label }}: 0 | {{ translations.threads_label }}: 0</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-title">{{ translations.memory }}</div>
                        <div class="metric-value" id="memory-value">0%</div>
                        <div class="metric-details" id="memory-details">{{ translations.used_label }}: 0GB / {{ translations.total_label }}: 0GB</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-title">{{ translations.disk }}</div>
                        <div class="metric-value" id="disk-value">0%</div>
                        <div class="metric-details" id="disk-details">{{ translations.used_label }}: 0GB / {{ translations.total_label }}: 0GB</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-title">{{ translations.gpu }}</div>
                        <div class="metric-value" id="gpu-value">0%</div>
                        <div class="metric-details" id="gpu-details">{{ translations.gpu_not_detected }}</div>
                    </div>
                </div>
                
                <div class="charts-grid">
                    <div class="chart-container" id="cpu-chart"></div>
                    <div class="chart-container" id="memory-chart"></div>
                    <div class="chart-container" id="disk-chart"></div>
                </div>
                
                <div class="info-grid">
                    <div class="info-card">
                        <div class="info-title">{{ translations.system_information }}</div>
                        <div class="info-content">
                            <p><strong>{{ translations.hostname }}:</strong> <span id="hostname">-</span></p>
                            <p><strong>{{ translations.os }}:</strong> <span id="os">-</span></p>
                            <p><strong>{{ translations.uptime }}:</strong> <span id="uptime">-</span></p>
                            <p><strong>{{ translations.processes }}:</strong> <span id="processes">-</span></p>
                        </div>
                    </div>
                    
                    <div class="info-card">
                        <div class="info-title">{{ translations.network_status }}</div>
                        <div class="info-content">
                            <p><strong>{{ translations.net_sent }}:</strong> <span id="net-sent">- MB</span></p>
                            <p><strong>{{ translations.net_recv }}:</strong> <span id="net-recv">- MB</span></p>
                            <p><strong>{{ translations.status }}:</strong> <span class="status-badge">{{ translations.operational }}</span></p>
                            <p><strong>{{ translations.last_update }}:</strong> <span id="last-update">-</span></p>
                        </div>
                    </div>
                </div>
                
                <!-- Adicionado conteúdo da antiga aba Performance -->
                <div class="info-card">
                    <div class="info-title">{{ translations.performance_history }}</div>
                    <div class="chart-container" id="performance-chart" style="height: 400px;"></div>
                </div>
                
                <div class="metric-grid" style="margin-top: 20px;">
                    <div class="metric-card">
                        <div class="metric-title">{{ translations.process_count }}</div>
                        <div class="metric-value" id="process-count">0</div>
                        <div class="metric-details" id="top-process">-</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-title">{{ translations.temperature }}</div>
                        <div class="metric-value" id="temperature-value">0°C</div>
                        <div class="metric-details" id="temperature-details">{{ translations.cpu }}: 0°C | {{ translations.gpu }}: 0°C</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-title">{{ translations.network_speed }}</div>
                        <div class="metric-value" id="network-speed">0 Mbps</div>
                        <div class="metric-details">{{ translations.upload }}: 0 Mbps | {{ translations.download }}: 0 Mbps</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-title">{{ translations.battery }}</div>
                        <div class="metric-value" id="battery-value">0%</div>
                        <div class="metric-details" id="battery-status">-</div>
                    </div>
                </div>
            </div>
            
            <!-- Architecture Tab -->
            <div id="architecture" class="tab-content">
                <div class="info-card">
                    <div class="info-title">{{ translations.automation_system }}</div>
                    
                    <div class="automation-container">
                        <!-- Regras de Automação -->
                        <div class="automation-card">
                            <h3><i class="fas fa-robot"></i> {{ translations.automation_rules }}</h3>
                            
                            <div class="form-group">
                                <label>{{ translations.rule_name }}</label>
                                <input type="text" id="rule-name" placeholder="{{ translations.rule_name_placeholder }}">
                            </div>
                            
                            <div class="form-group">
                                <label>{{ translations.condition }}</label>
                                <select id="rule-condition">
                                    <option value="cpu_usage">{{ translations.cpu_usage_above }}</option>
                                    <option value="memory_usage">{{ translations.memory_usage_above }}</option>
                                    <option value="disk_usage">{{ translations.disk_usage_above }}</option>
                                    <option value="process_count">{{ translations.process_count_above }}</option>
                                </select>
                                <input type="number" id="rule-value" placeholder="{{ translations.value }}" min="0" max="100" step="1">
                            </div>
                            
                            <div class="form-group">
                                <label>{{ translations.action }}</label>
                                <select id="rule-action">
                                    <option value="clean_temp_files">{{ translations.clean_temp_files }}</option>
                                    <option value="restart_service">{{ translations.restart_service }}</option>
                                    <option value="kill_processes">{{ translations.kill_processes }}</option>
                                    <option value="notify">{{ translations.notify }}</option>
                                </select>
                                <input type="text" id="rule-action-param" placeholder="{{ translations.parameter_optional }}" style="margin-top: 5px;">
                            </div>
                            
                            <button id="add-rule" class="btn">{{ translations.add_rule }}</button>
                        </div>
                        
                        <!-- Tarefas Agendadas -->
                        <div class="automation-card">
                            <h3><i class="fas fa-tasks"></i> {{ translations.scheduled_tasks }}</h3>
                            
                            <div class="form-group">
                                <label>{{ translations.task_type }}</label>
                                <select id="task-type">
                                    <option value="cleanup">{{ translations.cleanup }}</option>
                                    <option value="backup">{{ translations.backup }}</option>
                                    <option value="update">{{ translations.update }}</option>
                                </select>
                            </div>
                            
                            <div class="form-group">
                                <label>{{ translations.schedule }}</label>
                                <select id="task-schedule">
                                    <option value="daily">{{ translations.daily }}</option>
                                    <option value="weekly">{{ translations.weekly }}</option>
                                    <option value="monthly">{{ translations.monthly }}</option>
                                </select>
                            </div>
                            
                            <div class="form-group">
                                <label>{{ translations.execution_time }}</label>
                                <input type="time" id="task-time">
                            </div>
                            
                            <button id="schedule-task" class="btn">{{ translations.schedule_task }}</button>
                            
                            <div class="task-history">
                                <h4>{{ translations.execution_history }}</h4>
                                <div id="task-history-list"></div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Tarefas de Manutenção -->
                    <div class="automation-card">
                        <h3><i class="fas fa-tools"></i> {{ translations.maintenance_tools }}</h3>
                        
                        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px;">
                            <button id="clean-temp" class="btn">
                                <i class="fas fa-trash"></i> {{ translations.clean_temp_files }}
                            </button>
                            
                            <button id="optimize-disk" class="btn">
                                <i class="fas fa-hdd"></i> {{ translations.optimize_disk }}
                            </button>
                            
                            <button id="restart-system" class="btn">
                                <i class="fas fa-power-off"></i> {{ translations.restart_system }}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Code Creator Tab -->
            <div id="code-creator" class="tab-content">
                <div class="info-card">
                    <div class="info-title">{{ translations.code_creator_title }}</div>
                    <p>{{ translations.code_creator_description }}</p>
                    
                    <div class="code-editor-container">
                        <div class="editor-section">
                            <div class="editor-controls">
                                <select id="code-language">
                                    <option value="Python">Python</option>
                                    <option value="JavaScript">JavaScript</option>
                                    <option value="HTML">HTML</option>
                                    <option value="CSS">CSS</option>
                                    <option value="C++">C++</option>
                                    <option value="Java">Java</option>
                                    <option value="PHP">PHP</option>
                                </select>
                                <button id="ai-assist-btn" class="btn">{{ translations.ai_assistant }}</button>
                            </div>
                            <textarea id="code-description" placeholder="{{ translations.code_description_placeholder }}" style="width: 100%; height: 200px; padding: 10px; border-radius: 8px; background: rgba(20, 20, 45, 0.3); color: var(--text); border: 1px solid rgba(106, 90, 249, 0.3);"></textarea>
                            <button id="generate-code" class="btn" style="margin-top: 10px;">{{ translations.generate_code }}</button>
                        </div>
                        
                        <div class="editor-section">
                            <h3>{{ translations.generated_code }}</h3>
                            <div class="editor-container">
                                <textarea id="generated-code" placeholder="{{ translations.code_placeholder }}"></textarea>
                            </div>
                            <div style="display: flex; gap: 10px; margin-top: 10px;">
                                <button id="copy-code" class="btn">{{ translations.copy_code }}</button>
                                <button id="save-code" class="btn">{{ translations.save_code }}</button>
                                <button id="format-code" class="btn">{{ translations.format_code }}</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Chat Tab - Melhorias implementadas -->
            <div id="chat" class="tab-content">
                <div class="info-card">
                    <div class="info-title">{{ translations.chat_title }}</div>
                    <p>{{ translations.chat_description }}</p>
                    
                    <div class="chat-container">
                        <div id="chat-messages" class="chat-messages">
                            <div class="message bot-message">
                                {{ translations.welcome_message }}
                            </div>
                        </div>
                        <div class="typing-indicator" id="typing-indicator">
                            <span></span>
                            <span></span>
                            <span></span>
                            <div style="margin-left: 10px;">{{ translations.typing_indicator }}</div>
                        </div>
                        <div class="chat-input-area">
                            <input type="text" id="user-input" class="chat-input" placeholder="{{ translations.type_message }}">
                            <button id="send-btn" class="send-btn">
                                <i class="fas fa-paper-plane"></i>
                            </button>
                            <div class="online-indicator">
                                <div class="online-dot"></div>
                                <span>{{ translations.online_status }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Settings Tab -->
            <div id="settings" class="tab-content">
                <div class="info-card">
                    <div class="info-title">{{ translations.appearance_settings }}</div>
                    
                    <div class="theme-toggle">
                        <span>{{ translations.dark_mode }}</span>
                        <label class="switch">
                            <input type="checkbox" id="theme-toggle" {{ 'checked' if config.theme == 'light' else '' }}>
                            <span class="slider"></span>
                        </label>
                        <span>{{ translations.light_mode }}</span>
                    </div>
                    
                    <div class="language-selector">
                        <span>{{ translations.language }}:</span>
                        <select id="language-select">
                            <option value="portuguese" {{ 'selected' if config.language == 'portuguese' else '' }}>Português</option>
                            <option value="english" {{ 'selected' if config.language == 'english' else '' }}>English</option>
                            <option value="french" {{ 'selected' if config.language == 'french' else '' }}>Français</option>
                            <option value="italian" {{ 'selected' if config.language == 'italian' else '' }}>Italiano</option>
                        </select>
                    </div>
                    
                    <div class="customization-panel">
                        <h3>{{ translations.color_customization }}</h3>
                        
                        <div class="color-picker-group">
                            <div class="color-picker">
                                <label>{{ translations.primary_color }}</label>
                                <input type="color" id="primary-color" value="{{ config.primary_color }}">
                            </div>
                            
                            <div class="color-picker">
                                <label>{{ translations.secondary_color }}</label>
                                <input type="color" id="secondary-color" value="{{ config.secondary_color }}">
                            </div>
                            
                            <div class="color-picker">
                                <label>{{ translations.accent_color }}</label>
                                <input type="color" id="accent-color" value="{{ config.accent_color }}">
                            </div>
                            
                            <div class="color-picker">
                                <label>{{ translations.gauge_cpu_color }}</label>
                                <input type="color" id="gauge-cpu-color" value="{{ config.gauge_cpu_color }}">
                            </div>
                            
                            <div class="color-picker">
                                <label>{{ translations.gauge_memory_color }}</label>
                                <input type="color" id="gauge-memory-color" value="{{ config.gauge_memory_color }}">
                            </div>
                            
                            <div class="color-picker">
                                <label>{{ translations.gauge_disk_color }}</label>
                                <input type="color" id="gauge-disk-color" value="{{ config.gauge_disk_color }}">
                            </div>
                        </div>
                        
                        <button id="save-settings" class="btn">{{ translations.save_settings }}</button>
                        <button id="reset-settings" class="btn btn-danger">{{ translations.reset_settings }}</button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <div>{{ translations.version }}</div>
            <div>Advanced Runtime Architecture</div>
            <div>{{ translations.developed_by }}</div>
            <div id="system-status">{{ translations.system_status }} <span class="status-badge">{{ translations.operational }}</span></div>
        </div>
    </div>
    
    <div id="notification-area"></div>

    <script>
        // Configuração atual
        const config = JSON.parse('{{ config | tojson | safe }}');
        const translations = JSON.parse('{{ translations | tojson | safe }}');
        let automationRules = config.automation_rules || [];
        let codeEditor = null;
        let chatHistory = [];
        
        // Inicializar editor de código
        function initCodeEditor() {
            const textarea = document.getElementById('generated-code');
            codeEditor = CodeMirror.fromTextArea(textarea, {
                mode: "python",
                theme: "dracula",
                lineNumbers: true,
                indentUnit: 4,
                smartIndent: true,
                electricChars: true,
                autoCloseBrackets: true,
                matchBrackets: true,
                extraKeys: {
                    "Ctrl-Space": "autocomplete",
                    "Ctrl-F": "findPersistent",
                    "Ctrl-Q": function(cm) { cm.foldCode(cm.getCursor()); },
                    "Tab": "indentMore",
                    "Shift-Tab": "indentLess"
                },
                foldGutter: true,
                gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"]
            });
            
            // Configurar autocompletar
            codeEditor.on("keyup", function(cm, event) {
                if (!cm.state.completionActive && 
                    (event.keyCode > 46 || event.keyCode == 32)) {
                    CodeMirror.commands.autocomplete(cm, null, {completeSingle: false});
                }
            });
            
            // Ajustar altura conforme conteúdo
            codeEditor.on("change", function() {
                codeEditor.save();
            });
        }
        
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
                height: 200,
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
                    name: translations.cpu,
                    line: { color: config.gauge_cpu_color, width: 3 }
                },
                {
                    x: timePoints,
                    y: memoryData,
                    type: 'scatter',
                    mode: 'lines',
                    name: translations.memory,
                    line: { color: config.gauge_memory_color, width: 3 }
                }
            ];
            
            const layout = {
                title: translations.performance_history,
                height: 350,
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                font: { color: config.text_color },
                xaxis: { title: translations.time },
                yaxis: { title: translations.usage_percent },
                legend: { orientation: 'h' }
            };
            
            Plotly.newPlot('performance-chart', data, layout);
        }
        
        // Atualizar dados do sistema
        function updateSystemData(data) {
            // Atualizar métricas
            document.getElementById('cpu-value').textContent = data.cpu_usage.toFixed(1) + '%';
            document.getElementById('cpu-details').textContent = 
                `${translations.cores_label}: ${data.cpu_cores} | ${translations.threads_label}: ${data.cpu_threads}`;
            
            document.getElementById('memory-value').textContent = data.memory.percent.toFixed(1) + '%';
            document.getElementById('memory-details').textContent = 
                `${translations.used_label}: ${data.memory.used.toFixed(1)}GB / ${translations.total_label}: ${data.memory.total.toFixed(1)}GB`;
            
            document.getElementById('disk-value').textContent = data.disk.percent.toFixed(1) + '%';
            document.getElementById('disk-details').textContent = 
                `${translations.used_label}: ${data.disk.used.toFixed(1)}GB / ${translations.total_label}: ${data.disk.total.toFixed(1)}GB`;
            
            if (data.gpu) {
                document.getElementById('gpu-value').textContent = data.gpu.load.toFixed(1) + '%';
                document.getElementById('gpu-details').textContent = 
                    `${data.gpu.name} | ${translations.gpu_memory_label}: ${(data.gpu.memory.used/1024).toFixed(1)}/${(data.gpu.memory.total/1024).toFixed(1)}GB`;
            } else {
                document.getElementById('gpu-details').textContent = translations.gpu_not_detected;
            }
            
            // Atualizar informações do sistema
            document.getElementById('hostname').textContent = data.hostname;
            document.getElementById('os').textContent = data.os;
            document.getElementById('uptime').textContent = data.uptime;
            document.getElementById('processes').textContent = data.processes;
            
            document.getElementById('net-sent').textContent = data.network.sent.toFixed(2) + ' MB';
            document.getElementById('net-recv').textContent = data.network.recv.toFixed(2) + ' MB';
            document.getElementById('last-update').textContent = data.last_update;
            
            // Atualizar informações de performance
            document.getElementById('process-count').textContent = data.processes;
            document.getElementById('temperature-value').textContent = data.cpu_temp.toFixed(1) + '°C';
            document.getElementById('temperature-details').textContent = 
                `${translations.cpu}: ${data.cpu_temp.toFixed(1)}°C | ${translations.gpu}: ${data.gpu ? data.gpu.temp.toFixed(1) : 'N/A'}°C`;
            document.getElementById('network-speed').textContent = data.network.speed.toFixed(2) + ' Mbps';
            document.getElementById('battery-value').textContent = data.battery.toFixed(1) + '%';
            
            // Atualizar gráficos com cores personalizadas
            createGaugeChart('cpu-chart', data.cpu_usage, translations.cpu_usage, config.gauge_cpu_color);
            createGaugeChart('memory-chart', data.memory.percent, translations.memory_usage, config.gauge_memory_color);
            createGaugeChart('disk-chart', data.disk.percent, translations.disk_usage, config.gauge_disk_color);
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
                    
                    // Inicializar editor de código na primeira vez que a aba for aberta
                    if (tabId === 'code-creator' && !codeEditor) {
                        initCodeEditor();
                    }
                    
                    // Recriar gráfico de performance quando a dashboard é aberta
                    if (tabId === 'dashboard') {
                        createPerformanceChart();
                    }
                });
            });
        }
        
        // Configurar code creator
        function setupCodeCreator() {
            document.getElementById('generate-code').addEventListener('click', function() {
                const description = document.getElementById('code-description').value;
                const language = document.getElementById('code-language').value;
                
                if (!description.trim()) {
                    showNotification(translations.fill_description, 'warning');
                    return;
                }
                
                // Solicitar geração de código ao servidor
                fetch('/generate-code', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ description, language })
                })
                .then(response => response.json())
                .then(data => {
                    if (codeEditor) {
                        codeEditor.setValue(data.code);
                        showNotification(translations.code_generated, 'success');
                    }
                });
            });
            
            document.getElementById('copy-code').addEventListener('click', function() {
                if (codeEditor) {
                    const code = codeEditor.getValue();
                    navigator.clipboard.writeText(code);
                    showNotification(translations.code_copied, 'success');
                }
            });
            
            document.getElementById('format-code').addEventListener('click', function() {
                if (codeEditor) {
                    const totalLines = codeEditor.lineCount();
                    codeEditor.autoFormatRange({line:0, ch:0}, {line:totalLines});
                    showNotification(translations.code_formatted, 'success');
                }
            });
            
            document.getElementById('ai-assist-btn').addEventListener('click', function() {
                if (codeEditor) {
                    const currentCode = codeEditor.getValue();
                    if (currentCode.trim()) {
                        fetch('/ai-assist', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ code: currentCode })
                        })
                        .then(response => response.json())
                        .then(data => {
                            codeEditor.setValue(data.assisted_code);
                            showNotification(translations.ai_applied, 'success');
                        });
                    }
                }
            });
        }
        
        // Configurar chat (melhorias implementadas)
        function setupChat() {
            const chatMessages = document.getElementById('chat-messages');
            const userInput = document.getElementById('user-input');
            const sendBtn = document.getElementById('send-btn');
            const typingIndicator = document.getElementById('typing-indicator');
            
            function addMessage(text, isUser) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
                
                // Substituir quebras de linha por tags <br>
                const formattedText = text.replace(/\n/g, '<br>');
                messageDiv.innerHTML = formattedText;
                
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            function showTypingIndicator() {
                typingIndicator.style.display = 'flex';
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            function hideTypingIndicator() {
                typingIndicator.style.display = 'none';
            }
            
            function sendMessage() {
                const message = userInput.value.trim();
                if (message) {
                    addMessage(message, true);
                    userInput.value = '';
                    
                    // Mostrar indicador de digitação
                    showTypingIndicator();
                    
                    // Enviar para o servidor
                    fetch('/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ message, language: config.language })
                    })
                    .then(response => response.json())
                    .then(data => {
                        hideTypingIndicator();
                        addMessage(data.response, false);
                        
                        // Adicionar ao histórico
                        chatHistory.push({
                            user: message,
                            bot: data.response,
                            timestamp: new Date().toISOString()
                        });
                    })
                    .catch(error => {
                        hideTypingIndicator();
                        addMessage(translations.error_occurred, false);
                    });
                }
            }
            
            sendBtn.addEventListener('click', sendMessage);
            userInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        }
        
        // Configurar personalização
        function setupCustomization() {
            // Toggle do tema
            document.getElementById('theme-toggle').addEventListener('change', function() {
                const theme = this.checked ? 'light' : 'dark';
                updateConfig({ theme });
            });
            
            // Seletor de idioma
            document.getElementById('language-select').addEventListener('change', function() {
                updateConfig({ language: this.value });
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
            });
            
            // Restaurar padrões
            document.getElementById('reset-settings').addEventListener('click', function() {
                if (confirm(translations.reset_confirm)) {
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
                    showNotification(translations.fill_required, 'warning');
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
                
                showNotification(translations.rule_added, 'success');
            });
            
            // Agendar tarefa
            document.getElementById('schedule-task').addEventListener('click', function() {
                const taskType = document.getElementById('task-type').value;
                const schedule = document.getElementById('task-schedule').value;
                const time = document.getElementById('task-time').value;
                
                if (!time) {
                    showNotification(translations.select_time, 'warning');
                    return;
                }
                
                showNotification(`${translations.task_scheduled}: ${schedule} ${translations.at} ${time}`, 'success');
            });
            
            // Ferramentas de manutenção
            document.getElementById('clean-temp').addEventListener('click', function() {
                fetch('/clean-temp-files', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        showNotification(translations.cleanup_success, 'success');
                    });
            });
            
            document.getElementById('optimize-disk').addEventListener('click', function() {
                showNotification(translations.optimization_started, 'info');
            });
            
            document.getElementById('restart-system').addEventListener('click', function() {
                if (confirm(translations.restart_confirm)) {
                    showNotification(translations.restart_warning, 'warning');
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
                            <div>${translations.action}: ${task.action}</div>
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
            })
            .then(response => {
                if (response.ok) {
                    // Recarregar a página para aplicar o novo idioma
                    location.reload();
                }
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
            setupChat();
            
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
    current_lang = current_config['language']
    lang_translations = TRANSLATIONS.get(current_lang, TRANSLATIONS['portuguese'])
    return render_template_string(HTML_TEMPLATE, config=current_config, translations=lang_translations)

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

@app.route('/generate-code', methods=['POST'])
def generate_code_route():
    data = request.json
    description = data.get('description', '')
    language = data.get('language', 'Python')
    code = generate_code(description, language)
    return jsonify({"code": code})

@app.route('/chat', methods=['POST'])
def chat_route():
    data = request.json
    user_message = data.get('message', '')
    user_lang = data.get('language', 'portuguese')
    
    # Obter resposta do chatbot
    response = chatbot.get_response(user_message).text
    
    # Simular tempo de resposta para o indicador de digitação
    time.sleep(1 + random.random() * 2)
    
    return jsonify({"response": response})

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
        'ARA OS CC',
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