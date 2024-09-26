import os
import sys
from json import loads
from time import sleep, time as current_time, strftime, gmtime
from json import dumps
from websocket import WebSocket, WebSocketConnectionClosedException
from concurrent.futures import ThreadPoolExecutor
import logging
import ssl
import threading

# Configura o log de erros
logging.basicConfig(filename="websocket_errors.log", level=logging.ERROR)

# IDs pré-definidos
guild_id = "876880568560803900"  # ID do servidor
chid = "1274517394756472862"  # ID do canal
channel_name = "DISCORD BRASIL CALL PUBLICA"  # Nome do canal
tokenlist = open("tokens.txt").read().splitlines()

# Limita o número de threads para um valor seguro
executor = ThreadPoolExecutor(max_workers=100)
mute = False
deaf = False

# Tempo para reiniciar (2 minutos = 120 segundos)
RESTART_INTERVAL = 120

# Função para limpar o console
def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

# Função para exibir o cabeçalho do programa
def print_header():
    clear_console()
    print("\033[94m" + "="*50 + "\033[0m")
    print("\033[96m" + f"{'BOT DE CONEXÃO DISCORD':^50} \033[0m")
    print("\033[93m" + f"{'Autor: Obama':^50} \033[0m")
    print("\033[92m" + f"{'Canal: DISCORD BRASIL CALL PUBLICA':^50} \033[0m")
    print("\033[94m" + "="*50 + "\033[0m")
    print()  # Linha em branco para espaçamento

# Função para formatar o tempo em horas, minutos e segundos
def format_time(seconds):
    return strftime("%H:%M:%S", gmtime(seconds))

# Função para conectar ao WebSocket
def connect_to_voice(ws, token):
    try:
        hello = loads(ws.recv())
        heartbeat_interval = hello['d']['heartbeat_interval']

        ws.send(dumps({
            "op": 2,
            "d": {
                "token": token,
                "properties": {
                    "$os": "windows",
                    "$browser": "Discord",
                    "$device": "desktop"
                }
            }
        }))

        ws.send(dumps({
            "op": 4,
            "d": {
                "guild_id": guild_id,
                "channel_id": chid,
                "self_mute": mute,
                "self_deaf": deaf
            }
        }))

        ws.send(dumps({
            "op": 18,
            "d": {
                "type": "guild",
                "guild_id": guild_id,
                "channel_id": chid,
                "preferred_region": "singapore"
            }
        }))

        return heartbeat_interval

    except Exception as e:
        logging.error(f"Erro ao conectar com o token {token}: {str(e)}")
        print(f"\033[91m[ERRO] › Token {token}: {e}. Tentando reconectar...\033[0m")
        sleep(5)
        return None

# Função que executa a conexão e mantém o WebSocket ativo
def run(token, index):
    connection_time = current_time()
    log_token_connection(index)  # Loga a conexão do token
    
    while True:
        try:
            ws = WebSocket()
            ws.connect("wss://gateway.discord.gg/?v=9&encoding=json", sslopt={"cert_reqs": ssl.CERT_NONE})

            heartbeat_interval = connect_to_voice(ws, token)
            if heartbeat_interval is None:
                continue

            last_check = current_time()

            while True:
                sleep(heartbeat_interval / 1000)
                try:
                    ws.send(dumps({"op": 1, "d": None}))

                    elapsed_time = int(current_time() - connection_time)
                    formatted_time = format_time(elapsed_time)
                    
                    # Exibe o tempo a cada 1 minuto
                    if elapsed_time % 60 == 0 and elapsed_time > 0:  # Evita mostrar no primeiro minuto
                        print(f"\033[94m[TEMPO] › Token {index} conectado por {formatted_time}.\033[0m")

                except WebSocketConnectionClosedException:
                    print(f"\033[91m[ERRO] › Conexão fechada para Token {index}. Tentando reconectar...\033[0m")
                    break

                except Exception as e:
                    logging.error(f"Erro com o Token {index}: {str(e)}")
                    print(f"\033[91m[ERRO] › Token {index}: {e}. Tentando reconectar...\033[0m")
                    break

        except ssl.SSLError as ssl_err:
            logging.error(f"Erro SSL com o Token {index}: {str(ssl_err)}")
            print(f"\033[91m[ERRO SSL] › Token {index}: {ssl_err}. Tentando reconectar...\033[0m")
            sleep(5)

        except Exception as e:
            logging.error(f"Erro com o Token {index}: {str(e)}")
            print(f"\033[91m[ERRO] › Token {index}: {e}. Tentando reconectar...\033[0m")
            sleep(5)

# Função para registrar a conexão do token
def log_token_connection(token_index):
    print(f"\033[92m[INFO] › Token {token_index} conectado à DISCORD BRASIL CALL PUBLICA.\033[0m")

# Função para reiniciar o programa
def restart_program():
    print("\033[93m[REINÍCIO] › Reiniciando o programa após 2 minutos...\033[0m")
    os.execv(sys.executable, ['python'] + sys.argv)

# Função para iniciar a reconexão de todos os tokens
def start_tokens():
    print_header()
    i = 0
    for token in tokenlist:
        i += 1
        executor.submit(run, token, i)

# Função para iniciar o programa e reiniciá-lo automaticamente
def main():
    # Inicia a reconexão dos tokens
    start_tokens()

    # Após 2 minutos, reinicia o programa
    timer = threading.Timer(RESTART_INTERVAL, restart_program)
    timer.start()

# Inicia o programa principal
if __name__ == "__main__":
    main()