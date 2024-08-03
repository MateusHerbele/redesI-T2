import sys
import termios

def clear_input_buffer():
    termios.tcflush(sys.stdin, termios.TCIFLUSH)

def wait_for_user_input():
    while True:
        user_input = input("Digite 'sim' para iniciar a comunicação: ").strip().lower()
        if user_input == "sim":
            break
        else:
            print("Entrada inválida. Por favor, digite 'sim' para iniciar a comunicação.")