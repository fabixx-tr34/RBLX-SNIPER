import random
import string
import threading
import time
import webbrowser
import tkinter as tk
from tkinter import messagebox
 
import requests
import keyboard
import concurrent.futures
from colorama import Fore, Style, init
 
init()
 
 
class UsernameChecker:
 
    GITHUB_URL = "https://github.com/fabixx-tr34"
    THREAD_COUNT = 5
    HITS_FILE = "hits.txt"
 
    def __init__(self):
        self.name_length = 5
        self.is_paused = False
        self.run_signal = threading.Event()
        self.run_signal.set()
 
    # ---------- setup ----------
 
    def run(self):
        self._ask_to_open_github()
        self._print_banner()
 
        self.name_length = self._ask_username_length()
        print(Fore.CYAN + "You can press P to pause." + Style.RESET_ALL)
 
        self._launch_pause_listener()
 
        print(Fore.MAGENTA + f"Starting checker with {self.THREAD_COUNT} threads..." + Style.RESET_ALL)
        self._launch_workers()
 
        while True:
            time.sleep(1)
 
    def _ask_to_open_github(self):
        window = tk.Tk()
        window.withdraw()
        wants_to_open = messagebox.askyesno(
            "Checker",
            "Do you want to open the creator's website?"
        )
        if wants_to_open:
            webbrowser.open(self.GITHUB_URL)
        window.destroy()
 
    def _print_banner(self):
        print(Fore.MAGENTA + "=" * 40 + Style.RESET_ALL)
        print(Fore.MAGENTA + "        Username Checker" + Style.RESET_ALL)
        print(Fore.MAGENTA + "-" * 40 + Style.RESET_ALL)
        print(Fore.CYAN + "made by: " + self.GITHUB_URL + Style.RESET_ALL)
        print(Fore.MAGENTA + "=" * 40 + Style.RESET_ALL)
 
    # ---------- user input ----------
 
    def _ask_username_length(self):
        while True:
            raw_value = input(Fore.CYAN + "Username length (1-20): " + Style.RESET_ALL)
            if not raw_value.isdigit():
                print(Fore.RED + "Invalid number." + Style.RESET_ALL)
                continue
            value = int(raw_value)
            if value < 1 or value > 20:
                print(Fore.RED + "Enter a number between 1 and 20." + Style.RESET_ALL)
                continue
            return value
 
    def _ask_if_changing_length(self):
        while True:
            choice = input(Fore.CYAN + "Do you want to change the username length? (y/n): " + Style.RESET_ALL).strip().lower()
            if choice == "y":
                return True
            if choice == "n":
                return False
            print(Fore.RED + "Type y or n." + Style.RESET_ALL)
 
    # ---------- pausing ----------
 
    def _launch_pause_listener(self):
        thread = threading.Thread(target=self._pause_loop, daemon=True)
        thread.start()
 
    def _pause_loop(self):
        while True:
            keyboard.wait("p")
 
            if not self.is_paused:
                self.is_paused = True
                self.run_signal.clear()
                print(Fore.CYAN + "\n[PAUSED] Press p to continue." + Style.RESET_ALL)
                continue
 
            print(Fore.CYAN + "\n[RESUMING]" + Style.RESET_ALL)
            if self._ask_if_changing_length():
                self.name_length = self._ask_username_length()
 
            self.is_paused = False
            self.run_signal.set()
            print(Fore.CYAN + "[RUNNING]" + Style.RESET_ALL)
 
    # ---------- checking ----------
 
    def _launch_workers(self):
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.THREAD_COUNT)
        for _ in range(self.THREAD_COUNT):
            executor.submit(self._worker_loop)
        return executor
 
    def _worker_loop(self):
        while True:
            self.run_signal.wait()
            candidate = self._generate_username(self.name_length)
            self._check_username(candidate)
 
    @staticmethod
    def _generate_username(length):
        pool = string.ascii_letters + string.digits
        return "".join(random.choice(pool) for _ in range(length))
 
    def _check_username(self, username):
        endpoint = f"https://auth.roblox.com/v1/usernames/validate?Username={username}&Birthday=2000-01-01"
 
        try:
            response = requests.get(endpoint)
        except requests.exceptions.RequestException:
            return
 
        if response.status_code == 429:
            print(Fore.RED + "RATELIMIT: Waiting on " + username + Style.RESET_ALL)
            time.sleep(1)
            return
 
        result = response.json()
        status_code = result.get("code")
 
        if status_code == 0:
            print(Fore.GREEN + "VALID: " + username + Style.RESET_ALL)
            self._save_hit(username)
        elif status_code == 1:
            print(Fore.LIGHTBLACK_EX + "TAKEN: " + username + Style.RESET_ALL)
        elif status_code == 2:
            print(Fore.RED + "CENSORED: " + username + Style.RESET_ALL)
        else:
            print(Fore.YELLOW + f"Unknown ({status_code}): " + username + Style.RESET_ALL)
 
    def _save_hit(self, username):
        with open(self.HITS_FILE, "a") as f:
            f.write(username + "\n")
 
 
if __name__ == "__main__":
    checker = UsernameChecker()
    checker.run()
