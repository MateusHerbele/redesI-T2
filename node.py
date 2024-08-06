from utils import *

# --------main--------
def main():
    CURRENT_NODE_ADDRESS, NEXT_NODE_ADDRESS = get_addresses()

    # Inicializar os sockets
    socket_sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    socket_receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket_receiver.bind(CURRENT_NODE_ADDRESS[0])

    token_available = True if CURRENT_NODE_ADDRESS[1] == 0 else False
    player = Player(CURRENT_NODE_ADDRESS[1])
    game = Game()
    game_state = 0
    wait_for_user_input()
    while True:
        # Verificar se o token está disponível
        if token_available:
            game_state = player.dealer_routine(player, game, socket_sender, socket_receiver, NEXT_NODE_ADDRESS)
            token_available = False  # Token usado
        # Se não tiver, só espera as mensagens
        elif game_state == 0: # Continua o jogo
            # Receber as mensagens
            # Essa função só para quando receber o token
            network_comunication = ring_messages(CURRENT_NODE_ADDRESS, NEXT_NODE_ADDRESS, game, socket_receiver, socket_sender, player)
            if network_comunication == 1:
                token_available = True
            if network_comunication == 0:
                clear_input_buffer()
                break # Acaba a execução do programa
        else: # Fim do jogo
            clear_input_buffer()
            break
if __name__ == "__main__":
    main()