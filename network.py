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
            
            # transformar isso em um método ou função
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
    data_recv, addr = socket_receiver.recvfrom(1024)
    data_recv = pickle.loads(data_recv)
    print(f"Dados recebidos (token esperado): {data_recv.message}")
    if data_recv.message == "token":
        print(f"Token recebido de {addr}")
        data_recv.received_message() 
        data_recv = pickle.dumps(data_recv)
        socket_sender.sendto(data_recv, next_node[0])
        return True
    return False

def send_messages(messages_queue, socket_sender, token_hold_time, current_node, next_node):
    while messages_queue.empty():
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
