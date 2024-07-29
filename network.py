import socket
import time
from packet import Package
import pickle # Biblioteca para serialização de objetos
from packet import Packet, BroadcastPacket, UnicastPacket

# Define o tipo da mensagem
def type_of_message(type_message, message, sender_index):
    if type_message == 0:    # TOKEN 
        return UnicastPacket(sender_index, message[0] , 0, message[1]) # Envia o token para o próximo jogador e o jogo
    elif type_message == 1:  # CARTAS
        return BroadcastPacket(sender_index, 1, message) # Envia as cartas para todos
    elif type_message == 2:  # VIRA
        return BroadcastPacket(sender_index, 2, message) # Envia o vira
    elif type_message == 3:  # PALPITES
        return BroadcastPacket(sender_index, 3, message) # Pede os palpites
    elif type_message == 4:  # MOSTRA TODOS OS PALPITES
        return BroadcastPacket(sender_index, 4, message)
    elif type_message == 5:  # JOGAR A SUB RODADA
        return BroadcastPacket(sender_index, 5, message) # Pede as cartas jogadas
    elif type_message == 6:  # FIM DA RODADA
        return BroadcastPacket(sender_index, 6, message) # Passa os resultados da rodada
    elif type_message == 7:  # EMPATE
        return BroadcastPacket(sender_index, 7, message) # Passa o empate
    elif type_message == 8:  # VENCEDOR
        return BroadcastPacket(sender_index, 8, message) # Passa o vencedor 

# Verifica se a mensagem foi recebida corretamente 
def verifications(type_message, sender_index, socket_receiver, NEXT_NODE_ADDRESS):
    if type_message == 0: # TOKEN
        data, _ = socket_receiver.recvfrom(1024)
        packet = pickle.loads(data)
        if packet.sender[0] ==  sender_index and packet.verifier == True:
            return True, packet.message
        return False, None
    # Se for um broadcast
    data, _ = socket_receiver.recvfrom(1024)
    packet = pickle.loads(data)
    if packet.sender[0] == sender_index:
        for i in range(3):
            if packet.verifier[i] == False:
                return False, None 
        return True, packet.message

def send_broadcast(socket_sender, socket_receiver, type_message, message, sender_index, NEXT_NODE_ADDRESS):
    validation = False
    packet = type_of_message(type_message, message, sender_index)
    socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
    # Verifica se a mensagem foi recebida corretamente e reenvia caso não tenha sido
    while validation == False:
        validation, message = verifications(type_message, sender_index, socket_receiver, NEXT_NODE_ADDRESS)
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
    return validation, message

def send_unicast(socket_sender, socket_receiver, type_message, message, sender_index, NEXT_NODE_ADDRESS): # SÓ TEM UM TIPO DE UNICAST MAS NÃO SEI SE VALE DEIXAR SÓ AQUI MSM SEM TIPO DE MENSAGEM, ACHO Q FOGE DO PADRÃO
    packet = type_of_message(type_message, message, sender_index)
    socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
    # Verifica se a mensagem foi recebida corretamente e reenvia caso não tenha sido
    while validation == False:
        validation, message = verifications(type_message, sender_index, socket_receiver, NEXT_NODE_ADDRESS)
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
    return validation, message

def ring_messages(CURRENT_NODE_ADDRESS, NEXT_NODE_ADDRESS, socket_receiver, socket_sender, player):
    data, _ = socket_receiver.recvfrom(1024)
    packet = pickle.loads(data)
    # É preciso "corrigir" o index, para que faça sentido com o index do dealer atual
    corrected_index = abs(CURRENT_NODE_ADDRESS[1] - packet.sender[1] - 1) % 4
    if packet.message_type == 0: # TOKEN
        if packet.dest == CURRENT_NODE_ADDRESS[1]:
            packet.verifier = True
            socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
            time.sleep(1) # Garante que a mensagem de token recebido chegou no jogador que enviou
            return 1 # RETORNA QUE O TOKEN FOI RECEBIDO
        
        
    # Tratamento das mensagens de broadcast:
    elif packet.verifier[corrected_index] == True:
            return 2 # RETORNA QUE A MENSAGEM JÁ FOI RECEBIDA
    elif packet.message_type == 1: # CARTAS
        player.receive_cards(packet.message[corrected_index])
        packet.verifier.append(True) # Marca que a mensagem foi recebida
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
        return 2
    elif packet.message_type == 2: # VIRA
        player.receive_vira(packet.message)
        packet.verifier.append(True)
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
        return 2
    elif packet.message_type == 3: # PALPITE
        player.make_a_guess()
        packet.message.append(player.guess)
        packet.verifier.append(True)
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
        return 2
    elif packet.message_type == 4: # MOSTRA TODOS OS PALPITES
        packet.verifier.append(True)
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
        return 2
    elif packet.message_type == 5: # JOGAR A SUB RODADA
        player.play_a_card()
        packet.message.append(player.card_played)
        packet.verifier.append(True)
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
        return 2
    elif packet.message_type == 6: # FIM DA RODADA
        player.lose_lifes(packet.message[corrected_index])
        packet.verifier.append(True)
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
        return 2
    elif packet.message_type == 7: # EMPATE
        player.all_losers()
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
        #termina o jogo
        return 0
    elif packet.message_type == 8: # VENCEDOR
        if(packet.message == corrected_index):
            player.winner() # Você ganhou
        player.loser(packet.message) # Outro player ganhou
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
        #termina o jogo
        return 0