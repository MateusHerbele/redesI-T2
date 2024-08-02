from network import send_broadcast, send_unicast

class Player:
    def __init__(self, index):
        self.lifes = 7
        self.cards = []
        self.vira = None
        self.guess = None
        self.index = index # Talvez remover, avaliar a necessidade
        self.card_played = None
        
    # Faz um palpite e guarda no objeto 
    # DA PARA IMPLEMENTAR PARA LIMITAR O PALPITE AO NÚMERO DA RODADA
    def make_a_guess(self, previous_guesses, n_playes_alive):
        sum_guesses = 0

        if previous_guesses[1] != None:
            print(f"Palpites anteriores: ")
            n_previous_guesses = len([guess for guess in previous_guesses if guess is not None]) - 1
            print(f"[DEBUG] n_previous_guesses: {n_previous_guesses}")
            for i in range(0, n_previous_guesses): # Palpites anteriores que não são none e não são o número da rodada
                corrected_index = (self.index - i - 1) % n_playes_alive
                # Tem que ser  + 1 por conta do roung
                print(f"Jogador {corrected_index}: {previous_guesses[i+1]}")
                sum_guesses += previous_guesses[i+1]
            print(f"[DEBUG] sum_guesses: {sum_guesses}, n_playes_alive: {n_playes_alive}")

            if n_previous_guesses == n_playes_alive - 1:
                print("[DEBUG] Último palpite")
                self.guess = int(input("Digite seu palpite: "))
                sum_guesses += self.guess
                while previous_guesses[0] == sum_guesses:
                    print(f"Seu palpite, em conjunto com os palpites anteriores, não pode ser igual ao número de cartas jogadas")
                    sum_guesses -= self.guess
                    self.guess = int(input("Digite seu palpite: "))
                    sum_guesses += self.guess
                return self.guess
            else:
                self.guess = int(input("Digite seu palpite: "))
                return self.guess
        else: # Primeiro palpite da rodada
            self.guess = int(input("Digite seu palpite: "))
            return self.guess

    # Escolhe uma carta para jogar e guarda no objeto
    def play_a_card(self, previous_cards):
        print(f"[DEBUG] previous_cards: {previous_cards}")
        if previous_cards == []:
            print("Você é o primeiro a jogar, escolha uma carta: ")
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
            print(f"[DEBUG] cards: {self.cards}")
            self.card_played = self.cards[card-1]
            self.cards.pop(card-1)
        else:
            print("Cartas jogadas anteriormente: ")
            print(f"len:{(len(previous_cards))}")
            for i in range(len(previous_cards)):
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
        

    def lose_lifes(self, number_of_lost_lifes):
        self.lifes -= number_of_lost_lifes
        print(f"Você perdeu {number_of_lost_lifes} vidas. Vidas restantes: {self.lifes}")

    def receive_cards(self, cards):
        print(f"Cartas recebidas: {cards}")
        self.cards = cards

    def receive_vira(self, vira):
        print(f"Vira recebido: {vira}")
        self.vira = vira

    def all_losers(self):
        print("Todos os jogadores perderam!")
    
    def winner(self, ):
            print("Você venceu!")
    
    def loser(self, winner):
        print(f"O jogador {winner} venceu!")

    def dealer_routine(self, dealer_index, game, socket_sender, socket_receiver, NEXT_NODE_ADDRESS):
        # Inicializar o jogo
        while True:
            if game.state['n_sub_rounds'] == 0:
                corrected_index = (self.index - 1) % game.n_players
                game.initialize_deck() # Inicializa o baralho
                game.shuffle_deck() # Embaralha o baralho
                cards_to_send = game.draw_cards() # Distribui as cartas 
                _, cards = send_broadcast(socket_sender, socket_receiver, 1, cards_to_send, dealer_index, NEXT_NODE_ADDRESS) # Envia as cartas para os jogadores
                n_players_alive = game.state['players_alive'].count(True)
                self.receive_cards(cards[n_players_alive-1]) # Recebe as cartas do dealer
                send_broadcast(socket_sender, socket_receiver, 2, game.state['vira'], dealer_index, NEXT_NODE_ADDRESS) # Envia o vira
                self.receive_vira(game.state['vira']) # Recebe o vira
                # Fazer uma lista vazia com os palpites dos jogadores vivos
                # GUILHERME - MELHORAR ISSO AQUI PFV:
                guesses = [game.state['round']] # Reserva a primeira posição para o número da rodada
                for i in range(n_players_alive):
                    guesses.append(None)
                _, guesses = send_broadcast(socket_sender, socket_receiver, 3, guesses, dealer_index, NEXT_NODE_ADDRESS) # Pede os palpites
                #---------------------------------------------------------------------------------------
                print(f"[DEBUG] guesses: {guesses}")
                self.make_a_guess(guesses, n_players_alive) # Dealer faz o palpite
                guesses = guesses[1:] # Remove o número da rodada
                guesses[corrected_index] = self.guess

                send_broadcast(socket_sender, socket_receiver, 4, guesses, dealer_index, NEXT_NODE_ADDRESS) # Envia os palpites
            # Manda a mensagem para coletar as cartas jogadas 
            # e recebe as cartas jogadas
            self.play_a_card([]) # Dealer joga uma carta
            print(f"[DEBUG] card_played: {self.card_played}")
            card_message = [self.card_played]
            _, cards_played = send_broadcast(socket_sender, socket_receiver, 5, card_message, dealer_index, NEXT_NODE_ADDRESS) 
            subround_winner = game.end_of_sub_round(cards_played) # Contabiliza quem fez a rodada
                                    
            game.increment_sub_round() # Incrementa a rodada
            # Validação de fim de rodada
            if game.state['n_sub_round'] == game.state['round']:
                round_evaluation = game.end_of_round() # Avalia a situação pós-rodada
                send_broadcast(socket_sender, 6, None, NEXT_NODE_ADDRESS) # Passa os resultados da rodada
                if round_evaluation == -1: # Ninguém ganhou
                    next_dealer = game.next_dealer() # Pega o próximo dealer
                    game.reset_sub_rounds() # Reseta o número de sub-rodadas
                    send_broadcast(socket_sender, socket_receiver, 0, (next_dealer, game), dealer_index, NEXT_NODE_ADDRESS) # Passa o token para o próximo dealer
                    # continue
                elif round_evaluation == -2: # Empate
                    send_broadcast(socket_sender, socket_receiver, 7, round_evaluation, dealer_index, NEXT_NODE_ADDRESS)
                    return 1
                else: # Tem um vencedor
                    send_broadcast(socket_sender, socket_receiver, 8, round_evaluation, dealer_index, NEXT_NODE_ADDRESS)
                    return 1
                return 0 # Retorna 0 para indicar que a sub-rotina desse nodo terminou
            
            # Validação de quem torna:
            if subround_winner != dealer_index:
                validation, _ = send_unicast(socket_sender, 0, (subround_winner, game), dealer_index, NEXT_NODE_ADDRESS) # Passa o token para quem vai "tornar" e se tornar o "dealer" da próxima rodada
                return 0 # Retorna 0 para indicar que a sub-rotina desse nodo terminou        