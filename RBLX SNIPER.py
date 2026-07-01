import requests
import time
import random
import string
import threading
import keyboard
import concurrent.futures
from colorama import Fore, Style, init

init()

pausado = False
largo_user = 5
lock = threading.Event()
lock.set()


def pedir_largo():
    while True:
        entrada = input(Fore.CYAN + "Longitud del usuario (1-20): " + Style.RESET_ALL)
        if not entrada.isdigit():
            print(Fore.RED + "Numero invalido." + Style.RESET_ALL)
            continue
        num = int(entrada)
        if num < 1 or num > 20:
            print(Fore.RED + "Pon un numero entre 1 y 20." + Style.RESET_ALL)
            continue
        return num


def cambiar_largo():
    while True:
        opc = input(Fore.CYAN + "Quieres cambiar el largo del usuario? (y/n): " + Style.RESET_ALL).strip().lower()
        if opc == "y":
            return True
        if opc == "n":
            return False
        print(Fore.RED + "Escribe y o n." + Style.RESET_ALL)


def controlar_pausa():
    global pausado, largo_user
    while True:
        keyboard.wait("p")
        if not pausado:
            pausado = True
            lock.clear()
            print(Fore.CYAN + "\n[PAUSADO] Presiona p para continuar." + Style.RESET_ALL)
            continue

        print(Fore.CYAN + "\n[REANUDANDO]" + Style.RESET_ALL)
        if cambiar_largo():
            largo_user = pedir_largo()
        pausado = False
        lock.set()
        print(Fore.CYAN + "[CORRIENDO]" + Style.RESET_ALL)


def gen_user(length):
    chars = string.ascii_letters + string.digits
    nombre = ""
    for i in range(length):
        nombre += random.choice(chars)
    return nombre


def check_user(username):
    url = "https://auth.roblox.com/v1/usernames/validate?Username=" + username + "&Birthday=2000-01-01"
    try:
        res = requests.get(url)
    except requests.exceptions.RequestException:
        return

    if res.status_code == 429:
        print(Fore.RED + "RATELIMIT: Esperando en " + username + Style.RESET_ALL)
        time.sleep(1)
        return

    data = res.json()
    code = data.get("code")

    if code == 0:
        print(Fore.GREEN + "VALIDO: " + username + Style.RESET_ALL)
        archivo = open("hits.txt", "a")
        archivo.write(username + "\n")
        archivo.close()
        return

    if code == 1:
        print(Fore.LIGHTBLACK_EX + "USADO: " + username + Style.RESET_ALL)
        return

    if code == 2:
        print(Fore.RED + "CENSURADO: " + username + Style.RESET_ALL)
        return

    print(Fore.YELLOW + "Desconocido (" + str(code) + "): " + username + Style.RESET_ALL)


def loop_checker():
    global largo_user
    while True:
        lock.wait()
        name = gen_user(largo_user)
        check_user(name)


def main():
    global largo_user
    largo_user = pedir_largo()
    print(Fore.CYAN + "Puedes presionar P para pausar." + Style.RESET_ALL)

    hilo_pausa = threading.Thread(target=controlar_pausa, daemon=True)
    hilo_pausa.start()

    hilos = 5
    print(Fore.MAGENTA + "Iniciando checker con " + str(hilos) + " hilos..." + Style.RESET_ALL)

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=hilos)
    for i in range(hilos):
        executor.submit(loop_checker)


if __name__ == "__main__":
    main()
