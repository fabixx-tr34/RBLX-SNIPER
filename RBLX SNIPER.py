import concurrent.futures
import random
import string
import threading
import time
import tkinter as tk
import webbrowser
from tkinter import messagebox
 
import keyboard
import requests
from colorama import Fore, Style, init
 
init()
 
GITHUB_URL = "https://github.com/fabixx-tr34"
THREAD_COUNT = 5
HITS_FILE = "hits.txt"
REQUEST_TIMEOUT = 5
MAX_RETRIES = 3
 
name_length = 5
is_paused = False
run_signal = threading.Event()
run_signal.set()
file_lock = threading.Lock()
 
session = requests.Session()
 
 
def main():
    global name_length
 
    show_creator_popup()
    print_banner()
 
    name_length = ask_username_length()
    print(Fore.LIGHTMAGENTA_EX + "You can press P to pause." + Style.RESET_ALL)
 
    threading.Thread(target=pause_listener, daemon=True).start()
 
    print(Fore.MAGENTA + f"Starting checker with {THREAD_COUNT} threads..." + Style.RESET_ALL)
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=THREAD_COUNT)
    for _ in range(THREAD_COUNT):
        executor.submit(worker)
 
    while True:
        time.sleep(1)
 
 
def show_creator_popup():
    window = tk.Tk()
    window.withdraw()
    if messagebox.askyesno("Checker", "Do you want to open the creator's website?"):
        webbrowser.open(GITHUB_URL)
    window.destroy()
 
 
def print_banner():
    print(Fore.MAGENTA + "=" * 40 + Style.RESET_ALL)
    print(Fore.MAGENTA + "        Username Checker" + Style.RESET_ALL)
    print(Fore.MAGENTA + "-" * 40 + Style.RESET_ALL)
    print(Fore.LIGHTMAGENTA_EX + "made by: " + GITHUB_URL + Style.RESET_ALL)
    print(Fore.MAGENTA + "=" * 40 + Style.RESET_ALL)
 
 
def ask_username_length():
    while True:
        raw_value = input(Fore.LIGHTMAGENTA_EX + "Username length (1-20): " + Style.RESET_ALL)
        if not raw_value.isdigit():
            print(Fore.RED + "Invalid number." + Style.RESET_ALL)
            continue
        value = int(raw_value)
        if not (1 <= value <= 20):
            print(Fore.RED + "Enter a number between 1 and 20." + Style.RESET_ALL)
            continue
        return value
 
 
def ask_if_changing_length():
    while True:
        choice = input(Fore.LIGHTMAGENTA_EX + "Do you want to change the username length? (y/n): " + Style.RESET_ALL).strip().lower()
        if choice in ("y", "n"):
            return choice == "y"
        print(Fore.RED + "Type y or n." + Style.RESET_ALL)
 
 
def pause_listener():
    global is_paused, name_length
 
    while True:
        keyboard.wait("p")
 
        if not is_paused:
            is_paused = True
            run_signal.clear()
            print(Fore.LIGHTMAGENTA_EX + "\n[PAUSED] Press p to continue." + Style.RESET_ALL)
            continue
 
        print(Fore.LIGHTMAGENTA_EX + "\n[RESUMING]" + Style.RESET_ALL)
        if ask_if_changing_length():
            name_length = ask_username_length()
 
        is_paused = False
        run_signal.set()
        print(Fore.LIGHTMAGENTA_EX + "[RUNNING]" + Style.RESET_ALL)
 
 
def worker():
    while True:
        run_signal.wait()
        candidate = generate_username(name_length)
        check_username(candidate)
 
 
def generate_username(length):
    pool = string.ascii_letters + string.digits
    return "".join(random.choice(pool) for _ in range(length))
 
 
def check_username(username, attempt=1):
    endpoint = f"https://auth.roblox.com/v1/usernames/validate?Username={username}&Birthday=2000-01-01"
 
    try:
        response = session.get(endpoint, timeout=REQUEST_TIMEOUT)
    except requests.exceptions.RequestException:
        if attempt < MAX_RETRIES:
            check_username(username, attempt + 1)
        return
 
    if response.status_code == 429:
        print(Fore.RED + "RATELIMIT: Waiting on " + username + Style.RESET_ALL)
        time.sleep(1)
        if attempt < MAX_RETRIES:
            check_username(username, attempt + 1)
        return
 
    try:
        result = response.json()
    except ValueError:
        print(Fore.YELLOW + "Bad response for: " + username + Style.RESET_ALL)
        return
 
    status_code = result.get("code")
 
    if status_code == 0:
        print(Fore.GREEN + "VALID: " + username + Style.RESET_ALL)
        save_hit(username)
    elif status_code == 1:
        print(Fore.LIGHTBLACK_EX + "TAKEN: " + username + Style.RESET_ALL)
    elif status_code == 2:
        print(Fore.RED + "CENSORED: " + username + Style.RESET_ALL)
    else:
        print(Fore.YELLOW + f"Unknown ({status_code}): " + username + Style.RESET_ALL)
 
 
def save_hit(username):
    with file_lock:
        with open(HITS_FILE, "a") as f:
            f.write(username + "\n")
 
 
main()
