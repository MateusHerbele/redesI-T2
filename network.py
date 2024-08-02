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
def verifications(type_message, sender_index, socket_receiver, NEXT_NODE_ADDRESS):
    if type_message == 0: # TOKEN
        data, _ = socket_receiver.recvfrom(1024)
        packet = pickle.loads(data)
        if packet.sender ==  sender_index and packet.verifier == True:
            return True, packet.message
        return False, None
    # Se for um broadcast
    data, _ = socket_receiver.recvfrom(1024)
    packet = pickle.loads(data)
    if packet.sender == sender_index:
        for i in range(3):
            if packet.verifier[i] == False:
                return False, None 
        return True, packet.message

def send_broadcast(socket_sender, socket_receiver, type_message, message, sender_index, NEXT_NODE_ADDRESS):
    packet = BroadcastPacket(sender_index, type_message, message)
    socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
    # Verifica se a mensagem foi recebida corretamente e reenvia caso não tenha sido
    validation, message = verifications(type_message, sender_index, socket_receiver, NEXT_NODE_ADDRESS)
    while validation == False:
        validation, message = verifications(type_message, sender_index, socket_receiver, NEXT_NODE_ADDRESS)
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
    return validation, message

def send_unicast(socket_sender, socket_receiver, type_message, message, sender_index, NEXT_NODE_ADDRESS): # SÓ TEM UM TIPO DE UNICAST MAS NÃO SEI SE VALE DEIXAR SÓ AQUI MSM SEM TIPO DE MENSAGEM, ACHO Q FOGE DO PADRÃO
    packet = UnicastPacket(sender_index, message[0] , 0, message[1])
    socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
    # Verifica se a mensagem foi recebida corretamente e reenvia caso não tenha sido
    validation, message = verifications(type_message, sender_index, socket_receiver, NEXT_NODE_ADDRESS)
    while validation == False:
        validation, message = verifications(type_message, sender_index, socket_receiver, NEXT_NODE_ADDRESS)
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
    return validation, message # esse retorno do validation é inútil, mudar isso

def ring_messages(CURRENT_NODE_ADDRESS, NEXT_NODE_ADDRESS, game, socket_receiver, socket_sender, player):
    data, _ = socket_receiver.recvfrom(1024)
    packet = pickle.loads(data)
    print(packet)
    
    # É preciso "corrigir" o index, para que faça sentido com o index do dealer atual
    # print(f"[DEBUG] player: {player.index} corrected_index desse player na tr: {corrected_index}")
    if packet.message_type == 0: # TOKEN 
        print(f"[DEBUG] Token recebido de {packet.sender}")
        print(f"[DEBUG] Token enviado para {packet.dest}")
        if packet.dest == CURRENT_NODE_ADDRESS[1]:
            packet.verifier = True # não é um vetor pq é unicast
            socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
            # time.sleep(1) # Garante que a mensagem de token recebido chegou no jogador que enviou
            print(f"[DEBUG] ESTADOS DO JOGO: {packet.message}")
            game.load_state(packet.message) # Atualiza o estado do jogo
            return 1 # RETORNA QUE O TOKEN FOI RECEBIDO
        else: # Se não for para mim, passo adiante
            socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
            return 2
        
        
# Tratamento das mensagens de broadcast:
    if packet.message_type == 1: # CARTAS
        game.set_current_dealer(packet.sender) # Define o dealer -> gambiarra 
        # isso vai dar problema quando morrer um player:
        # mudar para que o dealer 2 e o index do 0 fique certo (1) 
        if CURRENT_NODE_ADDRESS[1] == 0: # Manter a circularidade
            if game.state['current_dealer'] == 1:
                corrected_index = 2
            elif game.state['current_dealer'] == 2:
                corrected_index = 1
            elif game.state['current_dealer'] == 3:
                corrected_index = 0
        else:
            corrected_index = abs(CURRENT_NODE_ADDRESS[1] - game.state['current_dealer'] - 1) % 4
        player.load_corrected_index(corrected_index)
        player.receive_cards(packet.message[player.corrected_index])
        packet.verifier[player.corrected_index] = True # Marca que a mensagem foi recebida
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
        return 2
    elif packet.verifier[player.corrected_index] == True:
        return 2 # RETORNA QUE A MENSAGEM JÁ FOI RECEBIDA
    elif packet.message_type == 2: # VIRA
        player.receive_vira(packet.message)
        packet.verifier[player.corrected_index] = True # Marca que a mensagem foi recebida
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
        return 2
    elif packet.message_type == 3: # PALPITE
        n_players_alive = len(packet.message) - 1 # Número de jogadores vivos
        player.make_a_guess(packet.message, n_players_alive)
        packet.message[player.corrected_index + 1] = player.guess
        packet.verifier[player.corrected_index] = True # Marca que a mensagem foi recebida
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
        return 2
    elif packet.message_type == 4: # MOSTRA TODOS OS PALPITES
        packet.verifier[player.corrected_index] = True # Marca que a mensagem foi recebida
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
        return 2
    elif packet.message_type == 5: # JOGAR A SUB RODADA
        player.play_a_card(packet.message)
        packet.message.append(player.card_played)
        packet.verifier[player.corrected_index] = True # Marca que a mensagem foi recebida
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
        return 2
    elif packet.message_type == 6: # FIM DA RODADA
        player.lose_lifes(packet.message[player.corrected_index])
        packet.verifier[player.corrected_index] = True # Marca que a mensagem foi recebida
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
        return 2
    elif packet.message_type == 7: # EMPATE
        player.all_losers()
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
        # termina o jogo
        return 0
    elif packet.message_type == 8: # VENCEDOR
        if packet.message == player.corrected_index:
            player.winner() # Você ganhou
        player.loser(packet.message) # Outro player ganhou
        socket_sender.sendto(pickle.dumps(packet), NEXT_NODE_ADDRESS[0])
        # termina o jogo
        return 0