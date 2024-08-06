class Packet:
    def __init__(self, sender, message_type, message, verifier=False):
        self.sender = sender  # Quem envia a mensagem
        self.message_type = message_type  # Tipo da mensagem
        self.message = message  # Mensagem
        self.verifier = verifier  # Verificador de recebimento

    def __str__(self):
        return f"Sender: {self.sender}, Type: {self.message_type}, Message: {self.message}, Verifier: {self.verifier}"

class BroadcastPacket(Packet): 
    def __init__(self, sender, message_type, message, verifier=[False, False, False, False]):
        super().__init__(sender, message_type, message, verifier)

    def __str__(self):
        return f"Broadcast -> {super().__str__()}"

class UnicastPacket(Packet):
    def __init__(self, sender, dest, message_type, message, verifier=False):
        super().__init__(sender, message_type, message, verifier)
        self.dest = dest  # Para quem a mensagem está sendo enviada

    def __str__(self):
        return f"Unicast -> {super().__str__()}, Dest: {self.dest}"