import socket
import time
from queue import Queue
from package import Package
import pickle # Biblioteca para serialização de objetos

def token_passage(socket_receiver, socket_sender, current_node, next_node):
    message_to_send = Package(next_node[1], current_node[1], "token")
    data = pickle.dumps(message_to_send)
    n_tries = 0
    while True:
        socket_sender.sendto(data, next_node[0])
        print(f"Token enviado para {next_node[1]}")

        try:
            print("Esperando resposta do token")
            data_recv, addr = socket_receiver.recvfrom(1024)
            data_recv = pickle.loads(data_recv)
            print(f"Mensagem recebida de {addr}: {data_recv.message}")

            if (data_recv.dest == message_to_send.dest and
                data_recv.sender == message_to_send.sender and
                data_recv.message == message_to_send.message and
                data_recv.received == True):    
                return False
            
        except socket.timeout:
            print("Tempo limite atingido, tentando novamente enviar o token.")
            n_tries += 1
            if n_tries > 3:
                print("O nodo seguinte está fora da rede.")
                return True
            continue


def token_received(socket_receiver, socket_sender, current_node, next_node):
    try:
        data_recv, addr = socket_receiver.recvfrom(1024)
        data_recv = pickle.loads(data_recv)
        print(f"Dados recebidos (token esperado): {data_recv.message}")
        if data_recv.message == "token":
            print(f"Token recebido de {addr}")
            data_recv.received_message() 
            data_recv = pickle.dumps(data_recv)
            socket_sender.sendto(data_recv, next_node[0])
            return True
    except socket.timeout:
        print("Tempo limite atingido ao esperar pelo token.")
    return False


def send_messages(messages_queue, socket_sender, token_hold_time, current_node, next_node):
    start_time = time.time()
    while time.time() - start_time < token_hold_time:
        if not messages_queue.empty():
            current_message = messages_queue.get()
            message = Package(next_node[1], current_node[1], current_message)
            data = pickle.dumps(message)
            socket_sender.sendto(data, next_node[0])
            print(f"Mensagem enviada para {next_node[1]}: {current_message}")
    return

def wait_for_user_input():
    while True:
        user_input = input("Digite 'sim' para iniciar a comunicação: ").strip().lower()
        if user_input == "sim":
            break
        else:
            print("Entrada inválida. Por favor, digite 'sim' para iniciar a comunicação.")

# ----------------- Main -----------------
CURRENT_NODE_ADDRESS = (("127.0.0.1", 21255), 'B')
NEXT_NODE_ADRESS =  (("127.0.0.1", 21254), 'A')

token_hold_time = 5 
node_messages_queue = Queue()

# Adicionar mensagens à fila para testes
node_messages_queue.put("Hello, Node A!")
node_messages_queue.put("How are you?")

socket_sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

socket_receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket_receiver.bind(CURRENT_NODE_ADDRESS[0])
socket_receiver.settimeout(5.0)  # Configurando o timeout do socket

token_available = True if CURRENT_NODE_ADDRESS[1] == 'A' else False

wait_for_user_input()
while True:
    if token_available:
        # Enviar mensagens da fila
        send_messages(node_messages_queue, socket_sender, token_hold_time, CURRENT_NODE_ADDRESS, NEXT_NODE_ADRESS)
        # Passar o token para o próximo nó
        if token_passage(socket_receiver, socket_sender, CURRENT_NODE_ADDRESS, NEXT_NODE_ADRESS):
            break
    # Verificar se o token foi recebido
    token_available = token_received(socket_receiver, socket_sender, CURRENT_NODE_ADDRESS, NEXT_NODE_ADRESS)
