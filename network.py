import time
import pickle # Biblioteca para serialização de objetos
# from game import Game
from packet import BroadcastPacket, UnicastPacket
import sys

NETWORK_ADDRESSES = [
    (("127.0.0.1", 21254), 0), # 0
    (("127.0.0.1", 21255), 1), # 1
    (("127.0.0.1", 21256), 2), # 2 
    (("127.0.0.1", 21257), 3)  # 3
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

def send_broadcast(socket_sender, socket_receiver, type_message, message, sender_index, NEXT_NODE_ADDRESS):
    packet = BroadcastPacket(sender_index, type_message, message)
    socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
    # Verifica se a mensagem foi recebida corretamente e reenvia caso não tenha sido
    validation, message = verifications(type_message, sender_index, socket_receiver)
    while validation == False:
# $& Enviando de novo BROADCAST")
        validation, message = verifications(type_message, sender_index, socket_receiver)
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
    return message

def send_unicast(socket_sender, socket_receiver, type_message, message, sender_index, NEXT_NODE_ADDRESS): # SÓ TEM UM TIPO DE UNICAST MAS NÃO SEI SE VALE DEIXAR SÓ AQUI MSM SEM TIPO DE MENSAGEM, ACHO Q FOGE DO PADRÃO
    packet = UnicastPacket(sender_index, message[0] , "TOKEN", message[1])
    socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
    # Verifica se a mensagem foi recebida corretamente e reenvia caso não tenha sido
    validation, message = verifications(type_message, sender_index, socket_receiver)
    while validation == False:
# $& Enviando de novo UNICAST")
        validation, message = verifications(type_message, sender_index, socket_receiver)
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
    return message # esse retorno do validation é inútil, mudar isso

# SE CONSEGUIR CONCERTAR ESSA **** OBG GUILHERME/MILENA:
def corrected_index_func(node, game):
    if node == 0: # Manter a circularidade
        if game.state['current_dealer'] == 1:
            return 2
        elif game.state['current_dealer'] == 2:
            return 1
        elif game.state['current_dealer'] == 3:
            return 0
    elif node == 1:
        if game.state['current_dealer'] == 0:
            return 0
        elif game.state['current_dealer'] == 2:
            return 2
        elif game.state['current_dealer'] == 3:
            return 1
    elif node == 2:
        if game.state['current_dealer'] == 0:
            return 1
        elif game.state['current_dealer'] == 1:
            return 0
        elif game.state['current_dealer'] == 3:
            return 2
    elif node == 3:
        if game.state['current_dealer'] == 0:
            return 2
        elif game.state['current_dealer'] == 1:
            return 1
        elif game.state['current_dealer'] == 2:
            return 0    

def ring_messages(CURRENT_NODE_ADDRESS, NEXT_NODE_ADDRESS, game, socket_receiver, socket_sender, player):
    data, _ = socket_receiver.recvfrom(1024)
    packet = pickle.loads(data)
    # print(packet) # DEBUG
    
    # É preciso "corrigir" o index, para que faça sentido com o index do dealer atual
    # print(f"[DEBUG] player: {player.index} corrected_index desse player na tr: {corrected_index}")
    if packet.message_type == "TOKEN": # TOKEN 
# $& Token recebido de {packet.sender}")
# $& Token enviado para {packet.dest}")
        if packet.dest == CURRENT_NODE_ADDRESS[1]:
            packet.verifier = True # não é um vetor pq é unicast
            socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
            # time.sleep(1) # Garante que a mensagem de token recebido chegou no jogador que enviou
# $& ESTADOS DO JOGO: {packet.message}")
            game.set_state(packet.message) # Atualiza o estado do jogo
            return 1 # RETORNA QUE O TOKEN FOI RECEBIDO
        else: # Se não for para mim, passo adiante
            socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
            return 2
# Tratamento das mensagens de broadcast:
    elif packet.verifier[player.index] == True:
# $& Mensagem já recebida")
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
# $& Player morto")
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
