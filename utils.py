import sys

NETWORK_ADDRESSES = [
    (("127.0.0.1", 21254), 0), # 0
    (("127.0.0.1", 21255), 1), # 1
    (("127.0.0.1", 21256), 2), # 2 
    (("127.0.0.1", 21257), 3)  # 3
]

def get_addresses():
    identification = int(sys.argv[1])
    return NETWORK_ADDRESSES[identification], NETWORK_ADDRESSES[(identification + 1) % 4]

def wait_for_user_input():
    while True:
        user_input = input("Digite 'sim' para iniciar a comunicação: ").strip().lower()
        if user_input == "sim":
            break
        else:
            print("Entrada inválida. Por favor, digite 'sim' para iniciar a comunicação.")