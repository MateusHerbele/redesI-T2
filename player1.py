import socket
from game import Game
from player import Player
from network import send_broadcast, send_unicast, ring_messages
from utils import *

# --------main--------
def main():
    CURRENT_NODE_ADDRESS, NEXT_NODE_ADDRESS = get_addresses()

    socket_sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    socket_receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_receiver.bind(CURRENT_NODE_ADDRESS[0])

    token_available = True if CURRENT_NODE_ADDRESS[1] == 0 else False
    start_game = True if CURRENT_NODE_ADDRESS[1] == 0 else False
    player = Player()
    game = Game()
    game_state = 0
    wait_for_user_input()
    while True:
        # Inicializar o jogo
        if start_game:
            game_state = player.dealer_routine(CURRENT_NODE_ADDRESS[1], game, socket_sender, socket_receiver, NEXT_NODE_ADDRESS)
            token_available = False
            start_game = False
        # Verificar se o token está disponível
        if token_available:
            game_state = player.dealer_routine(CURRENT_NODE_ADDRESS[1], game, socket_sender, socket_receiver, NEXT_NODE_ADDRESS)
            token_available = False  # Token usado
        # Se não tiver, só espera as mensagens
        elif game_state == 0: # Continua o jogo
            # Receber as mensagens
            # Essa função só para quando receber o token
            network_comunication = ring_messages(socket_sender, socket_receiver)
            if network_comunication == 1:
                token_available = True
            if network_comunication == 0:
                break # Acaba a execução do programa
        else: # Fim do jogo
            break
if __name__ == "__main__":
    main()