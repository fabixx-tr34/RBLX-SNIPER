import concurrent.futures
import random
import string
import threading
import time
import tkinter as tk
import webbrowser
from tkinter import messagebox
import requests
import keyboard
from colorama import Fore, Style, init

init()

GITHUB_URL = "https://github.com/fabixx-tr34"
GUNSLOL_URL = "https://guns.lol/fabiiix"
THREADS = 5
TIMEOUT = 5
MAX_RETRIES = 3
HITS_FILE = "hits.txt"

is_paused = False
run_signal = threading.Event()
run_signal.set()
file_lock = threading.Lock()

def show_creator_popup():
    window = tk.Tk()
    window.withdraw()
    if messagebox.askyesno("Checker", "Do you want to open the creator's GitHub?"):
        webbrowser.open(GITHUB_URL)
    window.destroy()

def banner():
    print(f"{Fore.MAGENTA}{'='*40}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}   Roblox Username Checker{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'-'*40}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTMAGENTA_EX}made by: {GITHUB_URL}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTMAGENTA_EX}guns.lol: {GUNSLOL_URL}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*40}{Style.RESET_ALL}")

def get_valid_length():
    while True:
        try:
            val = int(input(f"{Fore.LIGHTMAGENTA_EX}Longitud (1-20): {Style.RESET_ALL}"))
            if 1 <= val <= 20: return val
        except ValueError: pass
        print(f"{Fore.RED}Número inválido.{Style.RESET_ALL}")

def worker(name_len):
    session = requests.Session()
    while True:
        run_signal.wait()
        pool = string.ascii_letters + string.digits
        user = "".join(random.choice(pool) for _ in range(name_len))
        
        url = "https://auth.roblox.com/v1/usernames/validate"
        params = {"Username": user, "Birthday": "2000-01-01"}
        
        for _ in range(MAX_RETRIES):
            try:
                resp = session.get(url, params=params, timeout=TIMEOUT)
                if resp.status_code == 429:
                    time.sleep(1)
                    continue
                
                data = resp.json()
                code = data.get("code")
                
                if code == 0:
                    print(f"{Fore.GREEN}[+] VALID: {user}{Style.RESET_ALL}")
                    with file_lock:
                        with open(HITS_FILE, "a") as f: f.write(f"{user}\n")
                elif code == 1:
                    print(f"{Fore.LIGHTBLACK_EX}[-] TAKEN: {user}{Style.RESET_ALL}")
                break 
            except:
                time.sleep(0.5)

def main():
    show_creator_popup()
    banner()
    name_len = get_valid_length()
    
    def listen():
        global is_paused
        while True:
            keyboard.wait("p")
            is_paused = not is_paused
            if is_paused: run_signal.clear(); print("\n[PAUSADO]")
            else: run_signal.set(); print("\n[REANUDANDO]")
            time.sleep(0.5)
            
    threading.Thread(target=listen, daemon=True).start()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
        for _ in range(THREADS):
            executor.submit(worker, name_len)

if __name__ == "__main__":
    main()
