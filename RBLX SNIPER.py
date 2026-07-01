import requests
import time
import random
import string
import threading
import keyboard
import concurrent.futures
import tkinter as tk
from tkinter import messagebox
import webbrowser
from colorama import Fore, Style, init

init()

paused = False
username_length = 5
lock = threading.Event()
lock.set()

CREATOR_URL = "https://github.com/fabixx-tr34"


def show_creator_popup():
    root = tk.Tk()
    root.withdraw()
    answer = messagebox.askyesno(
        "Checker",
        "Do you want to open the creator's website?"
    )
    if answer:
        webbrowser.open(CREATOR_URL)
    root.destroy()


def ask_length():
    while True:
        entry = input(Fore.CYAN + "Username length (1-20): " + Style.RESET_ALL)
        if not entry.isdigit():
            print(Fore.RED + "Invalid number." + Style.RESET_ALL)
            continue
        num = int(entry)
        if num < 1 or num > 20:
            print(Fore.RED + "Enter a number between 1 and 20." + Style.RESET_ALL)
            continue
        return num


def ask_change_length():
    while True:
        opt = input(Fore.CYAN + "Do you want to change the username length? (y/n): " + Style.RESET_ALL).strip().lower()
        if opt == "y":
            return True
        if opt == "n":
            return False
        print(Fore.RED + "Type y or n." + Style.RESET_ALL)


def control_pause():
    global paused, username_length
    while True:
        keyboard.wait("p")
        if not paused:
            paused = True
            lock.clear()
            print(Fore.CYAN + "\n[PAUSED] Press p to continue." + Style.RESET_ALL)
            continue
        print(Fore.CYAN + "\n[RESUMING]" + Style.RESET_ALL)
        if ask_change_length():
            username_length = ask_length()
        paused = False
        lock.set()
        print(Fore.CYAN + "[RUNNING]" + Style.RESET_ALL)


def gen_username(length):
    chars = string.ascii_letters + string.digits
    name = ""
    for i in range(length):
        name += random.choice(chars)
    return name


def check_username(username):
    url = "https://auth.roblox.com/v1/usernames/validate?Username=" + username + "&Birthday=2000-01-01"
    try:
        res = requests.get(url)
    except requests.exceptions.RequestException:
        return
    if res.status_code == 429:
        print(Fore.RED + "RATELIMIT: Waiting on " + username + Style.RESET_ALL)
        time.sleep(1)
        return
    data = res.json()
    code = data.get("code")
    if code == 0:
        print(Fore.GREEN + "VALID: " + username + Style.RESET_ALL)
        file = open("hits.txt", "a")
        file.write(username + "\n")
        file.close()
        return
    if code == 1:
        print(Fore.LIGHTBLACK_EX + "TAKEN: " + username + Style.RESET_ALL)
        return
    if code == 2:
        print(Fore.RED + "CENSORED: " + username + Style.RESET_ALL)
        return
    print(Fore.YELLOW + "Unknown (" + str(code) + "): " + username + Style.RESET_ALL)


def checker_loop():
    global username_length
    while True:
        lock.wait()
        name = gen_username(username_length)
        check_username(name)


def print_banner():
    print(Fore.MAGENTA + "=" * 40 + Style.RESET_ALL)
    print(Fore.MAGENTA + "        Username Checker" + Style.RESET_ALL)
    print(Fore.MAGENTA + "-" * 40 + Style.RESET_ALL)
    print(Fore.CYAN + "made by: " + CREATOR_URL + Style.RESET_ALL)
    print(Fore.MAGENTA + "=" * 40 + Style.RESET_ALL)


def main():
    global username_length

    show_creator_popup()
    print_banner()

    username_length = ask_length()
    print(Fore.CYAN + "You can press P to pause." + Style.RESET_ALL)

    pause_thread = threading.Thread(target=control_pause, daemon=True)
    pause_thread.start()

    threads = 5
    print(Fore.MAGENTA + "Starting checker with " + str(threads) + " threads..." + Style.RESET_ALL)
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=threads)
    for i in range(threads):
        executor.submit(checker_loop)

    # Keep main thread alive so the pause listener and workers keep running
    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
