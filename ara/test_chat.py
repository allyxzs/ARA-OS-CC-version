import sys
from pathlib import Path

# Adiciona o diretório raiz ao path para que Python encontre o módulo 'ara'
sys.path.append(str(Path(__file__).parent))

from ara.core.chat_system import ARAChatSystem

def main():
    print("\n=== TESTE DO SISTEMA DE CHAT DA ARA ===")
    print("Digite mensagens normais ou comandos como:")
    print("!status - Mostra status do sistema")
    print("!processos - Lista processos ativos")
    print("!executar [código] - Executa código Python")
    print("!ajuda - Mostra todos os comandos")
    print("Digite 'sair' para encerrar\n")

    chat = ARAChatSystem()

    while True:
        try:
            user_input = input("Você: ").strip()
            if user_input.lower() == 'sair':
                break
            
            resposta = chat.get_response(user_input)
            print("\nARA:", resposta, "\n")

        except KeyboardInterrupt:
            print("\nEncerrando teste...")
            break
        except Exception as e:
            print(f"\n[ERRO] {str(e)}\n")

if __name__ == "__main__":
    main()