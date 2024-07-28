# import player from Player

# ALTERAR PARA Q A ORDEM DE ANÁLISE COMECE SEMPRE PELO CARTEADOR
import random 
class Game:
    def __init__(self):
        self.n_players = 4
        self.state = {
            'deck' : [],
            'round' : 0,
            'current_dealer' : None,
            'player_lifes' : [7, 7, 7, 7],
            'players_alive': [True, True, True, True],
            'guesses' : [],
            'points' : [],
            'vira' : None
        }
    
    # Inicilializa o baralho
    def initialize_deck(self):
        suits = ['O', 'E', 'C', 'P']
        ranks = ['4', '5', '6', '7', 'Q', 'J', 'K', 'A', '2', '3']
        self.state['deck'] = [{'suit': suit, 'rank': rank} for suit in suits for rank in ranks]

    # Embaralha o baralho
    def shuffle_deck(self):
        random.shuffle(self.state['deck'])

    # Força das cartas
    def card_strength(card, vira):
        suit_order = ['O', 'E', 'C', 'P']
        rank_order = ['4', '5', '6', '7', 'Q', 'J', 'K', 'A', '2', '3']
        # manilhas
        manilha_index = 1 if vira['rank'] == '3' else rank_order.index(vira['rank']) + 1
        if rank_order.index(card['rank']) == manilha_index:
            return 10 + suit_order.index(card['suit']) 
        return rank_order.index(card['rank'])

    # Embuchadas:
    def embuchadas(self, cards_played):
        for i in range(self.n_players):
            for j in range(i+1, self.n_players):
                if cards_played[i]['rank'] == cards_played[j]['rank']:
                    return i, j

    # Da as cartas e separa o vira, e retorna um vetor com as cartas
    def draw_cards(self):
        n_players_alive = self.state['players_alive'].count(True)
        n_cards = (n_players_alive / 52) - 1
        g_cards = [] # Grupo de cartas 0 - n_players -> players / n_players + 1 -> vira
        for i in range(self.n_players):
            if self.players_alive[i]:
                g_cards[i] = self.state['deck'].pop(n_cards) # Carta dos players
            else:
                g_cards[i] = None
        self.state['vira'] = self.state['deck'].pop() # Vira
        g_cards.append(self.state['vira'])
        return g_cards

    # Contabiliza as cartas jogadas
    # Vai receber o payload com todas as cartas jogadas na ordem correta + a carta do dealer
    # Contabiliza o vencedor da rodada
    def end_of_sub_round(self, cards_played):
        vira = self.state['vira']
        # Fazer um vetor com todas as forças das cartas
        cards_strength = []
        for i in range(self.n_players):
            cards_strength[i] = card_strength(cards_played[i], vira)

        # Verificar se houve embuchada
        for i in range(self.n_players-1):
            if cards_strength[i] == -1:
                continue # Para pular a verificação de embuchada para cartas já embuchadas
            # GUILHERME : DA PRA OTIMIZAR ISSO IMPEDINDO QUE VERIFIQUE CARTAS EMBUCHADAS GUARDANDO O INDICE DAS CARTAS EMBUCHADAS
            for j in range(i+1, self.n_players):
                if cards_played[i]['rank'] == cards_played[j]['rank']:
                    cards_strength[i] = -1
                    cards_strength[j] = -1
                    break # Caso já tenha sido embuchada não precisa continuar a verificação
        
        self.points[cards_strength.index(max(cards_strength))] += 1
    
    def kill_player(self, index):
        self.state['players_alive'][index] = False
    # Determina o vencedor da rodada
    def determine_winner(self):
        players_alive = 0 # Contador de jogadores vivos

        for i in range(self.n_players):
            if self.players_lifes[i] > 0:
                players_alive += 1
            else:
                self.kill_player(i) # Se o jogador não tiver mais vidas, ele é eliminado
        if players_alive == 1: # Se tem só um jogador vivo ele é o vencedor, só retorna o índice dele
            return self.players_lifes.index(max(self.players_lifes))
        elif players_alive == 0: # Se não tem ninguém vivo
            # E não tiver empates, o jogador com mais pontos é o vencedor
            if self.points.count(max(self.points)) == 1:
                return self.points.index(max(self.points))
            else:
                return -2 # Se tiver empate, não tem vencedor
        else:
            return -1 # Se tiver mais de um jogador vivo, não tem vencedor e continua o jogo
            
    # Contabiliza os pontos feitos na rodada
    # Elimina um jogador que fique sem vidas    
    def end_of_round(self):
        for i in range(self.n_players):
            if self.points[i] == self.guesses[i]:
                continue
            else:
                self.players_lifes[i] -= abs(self.points[i] - self.guesses[i])
        
        possible_winner = self.determine_winner() # Verifica se tem um vencedor
        if possible_winner == -1:
            self.state['round'] += 1
            self.state['current_dealer'] = (self.state['current_dealer'] + 1) % self.n_players
        elif possible_winner == -2:
            return -1
        else:
            return possible_winner
        
  
                    

