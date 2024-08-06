import time
import pickle # Biblioteca para serialização de objetos
# from game import Game
from packet import BroadcastPacket, UnicastPacket
import sys

NETWORK_ADDRESSES = [
    (("10.254.224.56", 21254), 0), # 0 # i29
    (("10.254.224.57", 21255), 1), # 1 # i30
    (("10.254.224.58", 21256), 2), # 2 # i31 
    (("10.254.224.59", 21257), 3)  # 3 # i32
]

def get_addresses():
    identification = int(sys.argv[1])
    return NETWORK_ADDRESSES[identification], NETWORK_ADDRESSES[(identification + 1) % 4]

# Verifica se a mensagem foi recebida corretamente 
def verifications(type_message, sender_index, socket_receiver):
    if type_message == "TOKEN": # TOKEN
        data, _ = socket_receiver.recvfrom(1024)
        packet = pickle.loads(data)
        if packet.sender ==  sender_index and packet.verifier == True:
            return True, packet.message
        return False, None
    # Se for um broadcast
    data, _ = socket_receiver.recvfrom(1024)
    packet = pickle.loads(data)
    if packet.sender == sender_index:
        for i in range(4):
            if i == sender_index:
                continue
            if packet.verifier[i] == False:
                return False, None 
        return True, packet.message

# Envia a mensagem de broadcast
def send_broadcast(socket_sender, socket_receiver, type_message, message, sender_index, NEXT_NODE_ADDRESS):
    packet = BroadcastPacket(sender_index, type_message, message)
    socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
    # Verifica se a mensagem foi recebida corretamente e reenvia caso não tenha sido
    validation, message = verifications(type_message, sender_index, socket_receiver)
    while validation == False:
        validation, message = verifications(type_message, sender_index, socket_receiver)
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
    return message

# Envia a mensagem de unicast
def send_unicast(socket_sender, socket_receiver, type_message, message, sender_index, NEXT_NODE_ADDRESS): # SÓ TEM UM TIPO DE UNICAST MAS NÃO SEI SE VALE DEIXAR SÓ AQUI MSM SEM TIPO DE MENSAGEM, ACHO Q FOGE DO PADRÃO
    packet = UnicastPacket(sender_index, message[0] , "TOKEN", message[1])
    socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
    # Verifica se a mensagem foi recebida corretamente e reenvia caso não tenha sido
    validation, message = verifications(type_message, sender_index, socket_receiver)
    while validation == False:
        validation, message = verifications(type_message, sender_index, socket_receiver)
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
    return message # esse retorno do validation é inútil, mudar isso

# Verifica se os jogadores anteriores receberam a mensagem
def verify_verifiers(packet, node_index):
    n_trues = 0
    if packet.sender == 0:
        if node_index == 1:
            n_trues = 0
        elif node_index == 2:
            n_trues = 1
        elif node_index == 3:
            n_trues = 2
    elif packet.sender == 1:
        if node_index == 2:
            n_trues = 0
        elif node_index == 3:
            n_trues = 1
        elif node_index == 0:
            n_trues = 2
    elif packet.sender == 2:
        if node_index == 3:
            n_trues = 0
        elif node_index == 0:
            n_trues = 1
        elif node_index == 1:
            n_trues = 2
    elif packet.sender == 3:
        if node_index == 0:
            n_trues = 0
        elif node_index == 1:
            n_trues = 1
        elif node_index == 2:
            n_trues = 2

    if n_trues == 0:
        return True
    else:
        if packet.verifier.count(True) == n_trues:
            return True
        else:
            return False

# Filtra as mensagens recebidas nas redes pelos nós que não estão com o bastão
def ring_messages(CURRENT_NODE_ADDRESS, NEXT_NODE_ADDRESS, game, socket_receiver, socket_sender, player):
    data, _ = socket_receiver.recvfrom(1024)
    packet = pickle.loads(data)
    # print(packet) # DEBUG
    
    # É preciso "corrigir" o index, para que faça sentido com o index do dealer atual
    # print(f"[DEBUG] player: {player.index} corrected_index desse player na tr: {corrected_index}")
    if packet.message_type == "TOKEN": # TOKEN 
        if packet.dest == CURRENT_NODE_ADDRESS[1]:
            packet.verifier = True # não é um vetor pq é unicast
            socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
            # time.sleep(1) # Garante que a mensagem de token recebido chegou no jogador que enviou
            game.set_state(packet.message) # Atualiza o estado do jogo
            return 1 # RETORNA QUE O TOKEN FOI RECEBIDO
        else: # Se não for para mim, passo adiante
            socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
            return 2 # se quebrar o jogo remove o 2
    # Tratamento das mensagens de broadcast:

    # Se algum nodo anterior não verificou a mensagem, reenvia pro nodo com o bastão para ele reenviar a mensagem
    if verify_verifiers(packet, CURRENT_NODE_ADDRESS[1]) == False:
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
        return 2 
    elif packet.verifier[player.index] == True:
        return 2 # RETORNA QUE A MENSAGEM JÁ FOI RECEBIDA
    elif packet.message_type == "TIE": # EMPATE
        player.all_losers()
        packet.verifier[player.index] = True # Marca que a mensagem foi recebida
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
        # termina o jogo
        return 0
    elif packet.message_type == "WINNER": # VENCEDOR
        player.game_winner(packet.message) # Você ganhou
        packet.verifier[player.index] = True # Marca que a mensagem foi recebida
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
        # termina o jogo
        return 0
    elif game.state["players_alive"][player.index] == False:
        print(f"Você foi eliminado ...")
        packet.verifier[player.index] = True
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
        return 2
    elif packet.message_type == "GAME-STATE":
        player.set_vira(packet.message['vira'])
        game.set_state(packet.message)
        packet.verifier[player.index] = True
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
        return 2
    elif packet.message_type == "CARDS": # CARTAS
        player.set_cards(packet.message[player.index])
        packet.verifier[player.index] = True # Marca que a mensagem foi recebida
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
        return 2
    elif packet.message_type == "TAKE-GUESSES": # PALPITE
        player.make_a_guess(game, packet.message)
        packet.message[player.index] = player.guess
        packet.verifier[player.index] = True # Marca que a mensagem foi recebida
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
        return 2
    elif packet.message_type == "SHOW-GUESSES": # MOSTRA TODOS OS PALPITES
        packet.verifier[player.index] = True # Marca que a mensagem foi recebida
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
        return 2
    elif packet.message_type == "CARDS-PLAYED": # JOGAR A SUB RODADA
        player.play_a_card(packet.message)
        game.set_card_played(packet.message, player.card_played, player.index)
        packet.message = game.get_cards_played()
        packet.verifier[player.index] = True # Marca que a mensagem foi recebida
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
        return 2
    elif packet.message_type == "SUBROUND-WINNER": # MOSTRA QUEM FEZ A SUB RODADA
        player.sub_round_winner(packet.message)
        packet.verifier[player.index] = True
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
    elif packet.message_type == "END-OF-ROUND": # FIM DA RODADA
        player.lose_lifes(packet.message[player.index])
        packet.verifier[player.index] = True # Marca que a mensagem foi recebida
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
        return 2
