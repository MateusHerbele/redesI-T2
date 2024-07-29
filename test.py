from game import Game

game = Game()
game.initialize_deck()
print(f"Printando deck: {game.state['deck']}")
game.shuffle_deck()
print(f"Printando deck: {game.state['deck']}")
print(f"Printando cartas: {game.draw_cards()}")