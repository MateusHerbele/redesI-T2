class Player:
    def __init__(self):
        self.lifes = 7
        self.cards = []
        self.vira = None
        self.guess = None
        self.index = None # Talvez remover, avaliar a necessidade
        self.card_played = None
        
    # Faz um palpite e guarda no objeto 
    # DA PARA IMPLEMENTAR PARA LIMITAR O PALPITE AO NÚMERO DA RODADA
    def make_a_guess(self, previous_guesses, g_round, n_playes_alive):
        sum_guesses = 0
        if previous_guesses != []:
            print(f"Palpites anteriores: ")
            for i in range(len(previous_guesses)):
                corrected_index = (self.index + i + 1) % n_playes_alive
                print(f"Jogador {corrected_index}: {previous_guesses[i]}")
                sum_guesses += previous_guesses[i]
            if len(previous_guesses) == n_playes_alive - 1:
                self.guess = int(input("Digite seu palpite: "))
                sum_guesses += self.guess
                while g_round == sum_guesses:
                    print(f"Seu palpite, em conjunto com os palpites anteriores, não pode ser igual ao número de cartas jogadas")
                    sum_guesses -= self.guess
                    self.guess = int(input("Digite seu palpite: "))
                    sum_guesses += self.guess
                return self.guess
            else:
                self.guess = int(input("Digite seu palpite: "))
                return self.guess

    # Escolhe uma carta para jogar e guarda no objeto
    def play_a_card(self, previous_cards):
        if previous_cards == []:
            print("Você é o primeiro a jogar, escolha uma carta: ")
            for i in range(len(self.cards)):
                print(f" {i+1}: {self.cards[i]}")
            card = int(input()) # adicionar verificação pra se o player não ta fazendo bosta e mandando coisa q não tem
            self.card_played = self.cards[card-1]
            self.cards.pop(card-1)
        else:
            print("Cartas jogadas anteriormente: ")
            for i in range(len(previous_cards)):
                print(f"Jogador {i}: {previous_cards[i]}")
            print("Escolha uma carta: ")
            for i in range(len(self.cards)):
                print(f" {i+1}: {self.cards[i]}")
            card = int(input())
            self.card_played = self.cards[card-1]
            self.cards.pop(card-1)

    def lose_lifes(self, number_of_lost_lifes):
        self.lifes -= number_of_lost_lifes

    def receive_cards(self, cards):
        self.cards = cards

    def receive_vira(self, vira):
        self.vira = vira

    def all_losers(self):
        print("Todos os jogadores perderam!")
    
    def winner(self, ):
            print("Você venceu!")
    
    def loser(self, winner):
        print(f"O jogador {winner} venceu!")