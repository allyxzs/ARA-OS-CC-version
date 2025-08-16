import psutil
from pathlib import Path
import tempfile
from .executor import SafeExecutor

from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer

class ARAChatSystem:
    def __init__(self, executor=None):
        self.executor = executor if executor else SafeExecutor()
        self.chatbot = self._initialize_chatbot()
        self._train_basic()

    def _initialize_chatbot(self):
        return ChatBot(
            'ARA_Assistant',
            storage_adapter='chatterbot.storage.SQLStorageAdapter',
            database_uri='sqlite:///ara_chat.db',
            logic_adapters=[
                {
                    'import_path': 'chatterbot.logic.BestMatch',
                    'default_response': 'Não entendi. Use !ajuda para comandos.',
                    'maximum_similarity_threshold': 0.85,
                    'language': 'POR'
                },
                {
                    'import_path': 'chatterbot.logic.MathematicalEvaluation'
                }
            ],
            preprocessors=[
                'chatterbot.preprocessors.clean_whitespace',
                'chatterbot.preprocessors.convert_to_ascii'
            ]
        )

    def _train_basic(self):
        corpus_trainer = ChatterBotCorpusTrainer(self.chatbot)
        corpus_trainer.train('chatterbot.corpus.portuguese')
        
        list_trainer = ListTrainer(self.chatbot)
        commands_training = [
            "Como está o sistema?",
            "Por favor, verifique o status do sistema",
            "Quais processos estão rodando?",
            "Liste os processos ativos",
            "Execute este código: print('Hello')",
            "Executando código Python",
            "Limpe os temporários",
            "Iniciando limpeza de arquivos temporários",
            "Reinicie o aplicativo",
            "Reiniciando sistema ARA"
        ]
        list_trainer.train(commands_training)

    def get_response(self, query: str) -> str:
        if query.startswith("!"):
            return self.handle_command(query[1:])
        
        try:
            response = self.chatbot.get_response(query)
            return str(response)
        except Exception as e:
            return f"Erro no chatbot: {str(e)}"
    
    def handle_command(self, command: str) -> str:
        cmd, *args = command.split(maxsplit=1)
        arg = args[0] if args else ""
        
        if cmd == "status":
            return self._handle_status()
        elif cmd == "processos":
            return self._handle_processes()
        elif cmd == "executar":
            return self._handle_execute(arg)
        elif cmd == "limpar_temp":
            return self._handle_clean_temp()
        elif cmd == "rede":
            return self._handle_network()
        elif cmd == "ajuda":
            return self._handle_help()
        else:
            return "Comando inválido. Digite !ajuda para opções."
    
    def _handle_status(self) -> str:
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage(str(Path.home())).percent
        return f"Status do Sistema:\nCPU: {cpu}%\nMemória: {mem}%\nDisco: {disk}%"

    def _handle_processes(self) -> str:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            if proc.info['cpu_percent'] > 0.5:
                processes.append(f"{proc.info['pid']}: {proc.info['name']} ({proc.info['cpu_percent']:.1f}%)")
        return "Processos ativos:\n" + "\n".join(processes[:15])

    def _handle_execute(self, code: str) -> str:
        try:
            success, output = self.executor.run(code)
            return f"Execução {'bem-sucedida' if success else 'falhou'}:\n{output[:500]}"
        except Exception as e:
            return f"Erro na execução: {str(e)}"

    def _handle_clean_temp(self) -> str:
        temp_dir = tempfile.gettempdir()
        count = 0
        for f in Path(temp_dir).glob('*'):
            try:
                if f.is_file():
                    f.unlink()
                    count += 1
            except:
                pass
        return f"Limpeza concluída: {count} arquivos temporários removidos"

    def _handle_network(self) -> str:
        net = psutil.net_io_counters()
        return f"Uso de rede:\nEnviado: {net.bytes_sent/1024:.1f} KB\nRecebido: {net.bytes_recv/1024:.1f} KB"

    def _handle_help(self) -> str:
        return ("Comandos disponíveis:\n"
                "!status - Status do sistema\n"
                "!processos - Lista processos\n"
                "!executar [código] - Executa código Python\n"
                "!limpar_temp - Limpa arquivos temporários\n"
                "!rede - Mostra uso de rede\n"
                "!ajuda - Mostra esta mensagem")
