from network import send_broadcast, send_unicast

class Player:
    def __init__(self, index):
        self.lifes = 7
        self.cards = []
        self.vira = None
        self.guess = None
        self.index = index # Talvez remover, avaliar a necessidade
        self.card_played = None
        # Métodos set

    def set_lifes(self, lifes):
        self.lifes = lifes

    def set_cards(self, cards):
        print(f"Cartas recebidas: {cards}")
        self.cards = cards

    def set_vira(self, vira):
        print(f"Vira recebido: {vira}")
        self.vira = vira
        # Manilha
        if self.vira[0] == '7':
            print("Manilha da rodada: Q (Dama)")
        elif self.vira[0] == 'Q (Dama)':
            print("Manilha da rodada: J (Valete)")
        elif self.vira[0] == 'J (Valete)':
            print("Manilha da rodada: K (Rei)")
        elif self.vira[0] == 'K (Rei)':
            print("Manilha da rodada: A")
        elif self.vira[0] == 'A':
            print("Manilha da rodada: 2")
        else:
            print(f"Manilha da rodada: {int(self.vira[0])+1}")    

    def set_guess(self, guess):
        self.guess = guess

    def set_index(self, index):
        self.index = index

    def set_card_played(self, card_played):
        self.card_played = card_played

    # Métodos get
    def get_lifes(self):
        return self.lifes

    def get_cards(self):
        return self.cards

    def get_vira(self):
        return self.vira

    def get_guess(self):
        return self.guess

    def get_index(self):
        return self.index

    def get_card_played(self):
        return self.card_played
    
    def sub_round_winner(self, winner):
        if winner == self.index:
            print("Você venceu a sub-rodada!")
        else:    
            print(f"O jogador {winner} venceu a sub-rodada!")

    # Faz um palpite e guarda no objeto 
    def make_a_guess(self, game, previous_guesses):
        sum_guesses = 0
        n_previous_guesses = 0
# $& previous_guesses: {previous_guesses}")
        n_previous_guesses = len([guess for guess in previous_guesses if guess is not None])
        # Primeiro palpite da rodada
        if n_previous_guesses == 0: 
            while True:
                try:
                    guess = int(input("Digite seu palpite: "))
                    if 0 <= guess <= game.get_round():
                        self.guess = guess
                        return self.guess
                    else:
                        print(f"Por favor, digite um número entre 0 e {game.get_round():}.")
                except ValueError:
                    print("Entrada inválida. Por favor, digite um número.")
        else:
            print(f"Palpites anteriores: ")
            for i in range(4):
                if previous_guesses[i] is not None:
                    print(f"Jogador {i}: {previous_guesses[i]}")
                    sum_guesses += previous_guesses[i]
            if n_previous_guesses == 3: # Último palpite
                while True:
                    try:
                        guess = int(input("Digite seu palpite: "))
                        sum_guesses += guess
                        if sum_guesses != game.get_round():
                            self.set_guess(guess)
                            return self.guess
                        else:
                            print(f"Seu palpite, em conjunto com os palpites anteriores, não pode ser igual ao número da rodada")
                            sum_guesses -= guess
                    except ValueError:
                        print("Entrada inválida. Por favor, digite um número.")
            else:
                while True:
                    try:
                        guess = int(input("Digite seu palpite: "))
                        self.set_guess(guess)
                        return self.guess
                    except ValueError:
                        print("Entrada inválida. Por favor, digite um número.")

    # Escolhe uma carta para jogar e guarda no objeto
    def play_a_card(self, previous_cards):
        n_previous_cards = len([card for card in previous_cards if card is not None])
# $& previous_cards: {previous_cards}")
        if n_previous_cards == 0:
            print("VOCÊ É O PRIMEIRO A JOGAR, escolha uma carta: ")
            for i in range(len(self.cards)):
                print(f" {i+1}: {self.cards[i][0]} de {self.cards[i][1]}")
            while True:
                try:
                    card = int(input())
                    if 1 <= card <= len(self.cards):
                        break
                    else:
                        print("Número inválido. Por favor, escolha um número entre 1 e", len(self.cards))
                except ValueError:
                    print("Entrada inválida. Por favor, digite um número.")
# $& cards: {self.cards}")
            self.card_played = self.cards[card-1]
            self.cards.pop(card-1)
        else:
            print("Cartas jogadas anteriormente: ")
            for i in range(4):
                if previous_cards[i] is not None:
                    print(f"Jogador {i}: {previous_cards[i][0]} de {previous_cards[i][1]}")
            print("Escolha uma carta: ")
            for i in range(len(self.cards)):
                print(f" {i+1}: {self.cards[i][0]} de {self.cards[i][1]}")
            while True:
                try:
                    card = int(input())
                    if 1 <= card <= len(self.cards):
                        break
                    else:
                        print("Número inválido. Por favor, escolha um número entre 1 e", len(self.cards))
                except ValueError:
                    print("Entrada inválida. Por favor, digite um número.")
            self.card_played = self.cards[card-1]
            self.cards.pop(card-1)
        

    def lose_lifes(self, points):
        number_of_lost_lifes = abs(points - self.guess)    
        self.lifes -= number_of_lost_lifes
        print(f"Número de vidas perdidas: {number_of_lost_lifes}. Vidas restantes: {self.lifes}")

    def all_losers(self):
        print("Todos os jogadores perderam!")
    
    def game_winner(self, winner):
            if winner == self.index:
                print("Você venceu!")
            else:
                print(f"O jogador {winner} venceu!")

    def dealer_routine(self, player, game, socket_sender, socket_receiver, NEXT_NODE_ADDRESS):
        # Inicializar o jogo
        while True:
            if game.state['n_sub_rounds'] == 0:
                guesses = 0
# $& Começando a rodada {game.state['round']}")
                game.set_current_dealer(player.index) # Define o dealer
                game.initialize_deck() # Inicializa o baralho
                game.shuffle_deck() # Embaralha o baralho
                cards_to_send = game.draw_cards() # Sorteia as cartas
                cards = send_broadcast(socket_sender, socket_receiver, "CARDS", cards_to_send, player.index, NEXT_NODE_ADDRESS) # Envia as cartas para os jogadores
                # n_players_alive = game.state['players_alive'].count(True)
                self.set_cards(cards[player.index]) # Recebe as cartas do dealer
                send_broadcast(socket_sender, socket_receiver, "GAME-STATE", game.get_state(), player.index, NEXT_NODE_ADDRESS) # Envia o estado do jogo
                self.set_vira(game.state['vira']) # Recebe o vira
                guesses = send_broadcast(socket_sender, socket_receiver, "TAKE-GUESSES", game.get_guesses(), player.index, NEXT_NODE_ADDRESS) # Pede os palpites
                #---------------------------------------------------------------------------------------
# $& guesses: {guesses}")
                self.make_a_guess(game, guesses) # Dealer faz o palpite
# $& guesses a serem acoplados: {guesses}")
                guesses[player.index] = self.guess # Palpite do dealer
                game.load_guesses(guesses) # Carrega os palpites no jogo
# $& guesses acoplados: {guesses}")
                send_broadcast(socket_sender, socket_receiver, "SHOW-GUESSES", guesses, player.index, NEXT_NODE_ADDRESS) # Envia os palpites
            # Manda a mensagem para coletar as cartas jogadas 
            # e recebe as cartas jogadas
            self.play_a_card([]) # Dealer joga uma carta
# $& card_played: {self.card_played}")
            game.set_card_played(game.state['cards_played'], self.card_played, self.index) # Adiciona a carta jogada ao jogo
            cards_played = send_broadcast(socket_sender, socket_receiver, "CARDS-PLAYED", game.get_cards_played(), player.index, NEXT_NODE_ADDRESS) 
            game.set_cards_played(cards_played) # Recebe as cartas jogadas
            subround_winner = game.end_of_sub_round(game.get_cards_played()) # Contabiliza quem fez a rodada
            self.sub_round_winner(subround_winner) # Mostra o vencedor da sub-rodada
            send_broadcast(socket_sender, socket_receiver, "SUBROUND-WINNER", subround_winner, player.index, NEXT_NODE_ADDRESS) # Envia o vencedor da sub-rodada
            game.increment_sub_rounds() # Incrementa a rodada
            # Validação de fim de rodada
            if game.state['n_sub_rounds'] == game.state['round']:
                round_evaluation = game.end_of_round() # Avalia a situação pós-rodada
                dealer_points = send_broadcast(socket_sender, socket_receiver, "END-OF-ROUND", game.state['points'], player.index, NEXT_NODE_ADDRESS) # Passa os resultados da rodada
                self.lose_lifes(dealer_points[player.index]) # Perde vidas
                game.reset_points() # Reseta os pontos
                if round_evaluation == -1: # Ninguém ganhou
                    game.increment_round() # Incrementa a rodada
                    next_dealer = game.next_dealer() # Pega o próximo dealer
                    game.reset_sub_rounds() # Reseta o número de sub-rodadas
# $& next_dealer: {next_dealer}")
                    if next_dealer != player.index:
                        send_unicast(socket_sender, socket_receiver, "TOKEN", (next_dealer, game.state), player.index, NEXT_NODE_ADDRESS) # Passa o token para o próximo dealer
                        return 0 # Retorna 0 para indicar que a sub-rotina desse nodo terminou
                    continue # Continua o loop
                elif round_evaluation == -2: # Empate
                    self.all_losers()
                    send_broadcast(socket_sender, socket_receiver, "TIE", round_evaluation, player.index, NEXT_NODE_ADDRESS)
                    return 1
                else: # Tem um vencedor
                    self.game_winner(round_evaluation) # Anuncia o vencedor
                    send_broadcast(socket_sender, socket_receiver, "WINNER", round_evaluation, player.index, NEXT_NODE_ADDRESS)
                    return 1
                # return 0 # Retorna 0 para indicar que a sub-rotina desse nodo terminou
            
            # Validação de quem torna:
            if subround_winner != player.index:
# $& subround_winner (torna): {subround_winner}")
                send_unicast(socket_sender, socket_receiver, "TOKEN", (subround_winner, game.state), player.index, NEXT_NODE_ADDRESS) # Passa o token para quem vai "tornar" e se tornar o "dealer" da próxima rodada
                return 0 # Retorna 0 para indicar que a sub-rotina desse nodo terminou      