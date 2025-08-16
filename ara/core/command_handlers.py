import psutil
from .executor import SafeExecutor

class CommandHandler:
    def __init__(self):
        self.executor = SafeExecutor()

    def handle_command(self, command: str) -> str:
        if command == "status":
            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().percent
            return f"CPU: {cpu}% | Memória: {mem}%"
        
        elif command == "processos":
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                if proc.info['cpu_percent'] > 0:
                    processes.append(f"{proc.info['pid']}: {proc.info['name']} ({proc.info['cpu_percent']:.1f}%)")
            return "Processos ativos:\n" + "\n".join(processes[:10])  # Limita a 10 resultados
        
        elif command.startswith("executar "):
            code = command[9:]  # Remove "executar "
            success, output = self.executor.run(code)
            return f"Execução {'bem-sucedida' if success else 'falhou'}:\n{output[:500]}"  # Limita o output
        
        elif command == "ajuda":
            return "Comandos disponíveis:\n!status - Status do sistema\n!processos - Lista processos\n!executar [código] - Roda código Python\n!ajuda - Mostra esta mensagem"
        
        else:
            return "Comando desconhecido. Digite !ajuda para opções."