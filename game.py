# ALTERAR PARA Q A ORDEM DE ANÁLISE COMECE SEMPRE PELO CARTEADOR
import random 
class Game:
    def __init__(self):
        self.n_players = 4
        self.state = {
            'deck' : [],
            'round' : 1,
            'n_sub_rounds' : 0,
            'n_sub_rounds' : 0,
            'current_dealer' : None,
            'players_lifes' : [7, 7, 7, 7],
            'players_alive': [True, True, True, True],
            'guesses' : [None, None, None, None],
            'cards_played' : [None, None, None, None],
            'points' : [0, 0, 0, 0],
            'vira' : None,
        }
# class Game:
#     def __init__(self):
#         self.n_players = 4
#         self.state = {
#             'deck' : [],
#             'round' : 1,
#             'n_sub_rounds' : 0,
#             'n_sub_rounds' : 0,
#             'current_dealer' : None,
#             'players_lifes' : [3, 3, 3, 3],
#             'players_alive': [True, True, True, True],
#             'guesses' : [None, None, None, None],
#             'cards_played' : [None, None, None, None],
#             'points' : [0, 0, 0, 0],
#             'vira' : None,
#         }
    
    def __str__(self):
        return f"Deck: {self.state['deck']}, Round: {self.state['round']}, Current Dealer: {self.state['current_dealer']}, Player Lifes: {self.state['players_lifes']}, Players Alive: {self.state['players_alive']}, Guesses: {self.state['guesses']}, Points: {self.state['points']}, Vira: {self.state['vira']}"

    # Carrega os guesses
    def load_guesses(self, guesses):
        self.state['guesses'] = guesses 

    def set_round(self, round):
        self.state['round'] = round
    
    def get_round(self):
        return self.state['round']
    
    def get_guesses(self):  
        return self.state['guesses']

    # Soma o n de subrodadas
    def increment_sub_rounds(self):
        self.state['n_sub_rounds'] += 1

    # Soma o n de rounds
    def increment_round(self):
        self.state['round'] += 1

    # Reseta o número de subrodadas
    def reset_sub_rounds(self):
        self.state['n_sub_rounds'] = 0

    # Reseta os palpites
    def reset_guesses(self):
        self.state['guesses'] = [None, None, None, None]

    # Atribui o dealer atual
    def set_current_dealer(self, dealer):
        self.state['current_dealer'] = dealer

    def set_state(self, state):
        self.state = state
    
    def get_state(self):
        return self.state
    
    def set_card_played(self, cards_played, card, index):
        cards_played[index] = card
        self.state['cards_played'] = cards_played
    
    def set_cards_played(self, cards_played):
        self.state['cards_played'] = cards_played

    def get_cards_played(self):
        return self.state['cards_played']
     
    def reset_card_played(self):
        self.state['cards_played'] = [None, None, None, None]

    # Inicilializa o baralho
    def initialize_deck(self):
        suits = ['Ouro', 'Espadas', 'Copas', 'Paus']
        ranks = ['4', '5', '6', '7', 'Q (Dama)', 'J (Valete)', 'K (Rei)', 'A', '2', '3']
        self.state['deck'] = [(rank, suit) for rank in ranks for suit in suits]

    # Embaralha o baralho
    def shuffle_deck(self):
        random.shuffle(self.state['deck'])

    # Força das cartas
    def card_strength(self, card):
        # if card == None:
        #     return -2 # Se a carta for None, é porque o jogador está morto
        suit_order = ['Ouro', 'Espadas', 'Copas', 'Paus']
        rank_order = ['4', '5', '6', '7', 'Q (Dama)', 'J (Valete)', 'K (Rei)', 'A', '2', '3']
        # manilhas
        manilha_index = 0 if self.state['vira'][0] == '3' else rank_order.index(self.state['vira'][0]) + 1
        if rank_order.index(card[0]) == manilha_index:
            return 10 + suit_order.index(card[1]) 
        return rank_order.index(card[0])

    # Embuchadas:
    def embuchadas(self, cards_played):
        for i in range(self.n_players):
            for j in range(i+1, self.n_players):
                if cards_played[i][0] == cards_played[j][0]:
                    return i, j

    # Da as cartas e separa o vira, e retorna um vetor com as cartas
    def draw_cards(self):
        n_players_alive = self.state['players_alive'].count(True)
        g_cards = [[] for _ in range(self.n_players)]  # Inicializa g_cards como lista de listas
        n_max_cards = int(40 / n_players_alive) - 1 # Número máximo de cards por player
        n_cards_to_give = 0 # Número de cartas a serem dadas
        if self.state['round'] > n_max_cards:
            n_cards_to_give = n_max_cards
        else:
            n_cards_to_give = self.state['round'] 
        for i in range(self.n_players):
            if self.state['players_alive'][i]:
                for _ in range(n_cards_to_give):
                    # print(f"[DEBUG] deck sendo dtr: {self.state['deck']}")
                    # print(f"Para : {i}")
                    g_cards[i].append(self.state['deck'].pop())
            else: # Se o jogador não estiver vivo, ele não recebe cartas
                g_cards[i] = None
        self.state['vira'] = self.state['deck'].pop() # Vira é a última carta removida do baralho
        return g_cards
    
    # Contabiliza as cartas jogadas
    # Vai receber o payload com todas as cartas jogadas na ordem correta + a carta do dealer
    # Contabiliza o vencedor da rodada
    def end_of_sub_round(self, cards_played):
        # Fazer um vetor com todas as forças das cartas
        cards_strength = [None, None, None, None]
        for i in range(self.n_players):
            if self.state['players_alive'][i] == False:
                cards_strength[i] = -2 # Se o jogador estiver morto, ele não tem força, -2 para diferençiar de embuchadas
                continue
            cards_strength[i] = self.card_strength(cards_played[i])

        # Verificar se houve embuchada
        for i in range(self.n_players-1):
            if cards_strength[i] == -1 or self.state['players_alive'][i] == False:
                continue # Para pular a verificação de embuchada para cartas já embuchadas
            for j in range(i+1, self.n_players):
                if self.state['players_alive'][j] == False:
                    continue
                if cards_played[i][0] == cards_played[j][0]:
                    cards_strength[i] = -1
                    cards_strength[j] = -1
                    break # Caso já tenha sido embuchada não precisa continuar a verificação
        self.state['points'][cards_strength.index(max(cards_strength))] += 1
        self.reset_card_played()
        return cards_strength.index(max(cards_strength))
    
    # Pega o próximo jogador VIVO para ser o dealer
    def next_dealer(self):
        n_dealer = (self.state['round'] - 1) % self.n_players 
        while not self.state['players_alive'][n_dealer]:
            n_dealer = (n_dealer + 1) % self.n_players
        return n_dealer

    def kill_player(self, index):
        self.state['players_alive'][index] = False
    # Determina o vencedor da rodada
    def determine_winner(self):
        for i in range(self.n_players):
            if self.state['players_lifes'][i] <= 0 and self.state['players_alive'][i]:
                self.kill_player(i)
            elif self.state['players_alive'][i] == False:
                self.state['players_lifes'][i] = -55 # Valor arbitrário para jogadores mortos
        players_alive = self.state['players_alive'].count(True)
        if players_alive == 1: # Se tem só um jogador vivo ele é o vencedor, só retorna o índice dele
            return self.state['players_alive'].index(True)
        elif players_alive > 1: # Se tiver mais de um jogador vivo
            return -1 # Continua o jogo
        else: # Se não tiver nenhum jogador vivo
            # Verifica se tem empate
            max_lifes = max(self.state['players_lifes'])
            if self.state['players_lifes'].count(max_lifes) > 1:
                return -2
            else:
                return self.state['players_lifes'].index(max_lifes)                    
            
    
    def reset_points(self):
        self.state['points'] = [0, 0, 0, 0]
    # Contabiliza os pontos feitos na rodada
    # Elimina um jogador que fique sem vidas    
    def end_of_round(self):
        for i in range(self.n_players):
            if self.state['players_alive'][i] == False:
                continue
            if self.state['points'][i] == self.state['guesses'][i]:
                continue
            else:
                self.state['players_lifes'][i] -= abs(self.state['points'][i] - self.state['guesses'][i])
        self.reset_guesses()
        return self.determine_winner() # Retorna o vencedor da rodada, ou -1 se não tiver vencedor, ou -2 se tiver empate