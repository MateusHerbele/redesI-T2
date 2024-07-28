class Package:
    # Formato da Mensagem:
    # Marcador de início
    # Destinatário
    # Remetente
    # Mensagens
    # Booleano para saber se recebeu a mensagem
    # Marcador de fim
    # Formato da Mensagem do bastão ? 

    # Construtor padrão
    def __init__(self, dest, sender, message, received=False):
        self.dest = dest
        self.sender = sender
        self.message = message
        self.received = received
        # self.encode('utf-8')

    # Método para mensagens de bastão
    # def token_message(self):
    #     return self.message == "token"
    
    # Método para mensagens de confirmação de recebimento da mensagem
    def received_message(self):
        return self.received == True 