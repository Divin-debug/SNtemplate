from colorama import Fore, init
from datetime import datetime
import requests, ctypes, threading
import os, time, random, string

init(convert = True)
os.system("cls")

class data:

    def __init__(self):
        self.lock = threading.Lock()
        self.now = datetime.now()
        self.date = self.now.strftime("%d-%m-%Y")
        self.checking = True
        self.serials = []
        self.invalid = 0
        self.valid = 0
    
    def _message(self, message, text, color, new_line = False):
        s = ""
        if new_line:
            s = "\n"
        s += f"{Fore.WHITE}[{color}{message}{Fore.WHITE}] {text}"
        return s
    
    def _safe_print(self, arg: str):
        self.lock.acquire()
        print(arg)
        self.lock.release()
    
    def _output(self, serial_number: str, status: bool):
        if status:
            self._safe_print(
                self._message("VALID", f"  Serial Number: {serial_number}", Fore.GREEN)
            )
            if not os.path.exists("Results/"):
                 os.makedirs("Results/")
            with open(f"Results/Valid {self.date}.txt", "a") as f:
                f.write(serial_number + "\n")
            self.valid += 1
        else:
            self.invalid += 1
            self._safe_print(
                self._message("INVALID", f"Serial Number: {serial_number}", Fore.RED)
            )
        self._update_title()
    
    def _update_title(self):
        remaining = len(self.serials) - (self.valid + self.invalid)
        ctypes.windll.kernel32.SetConsoleTitleW(f"Divin SN Checker Template | Valid: {self.valid} | Invalid: {self.invalid} | Checked: {self.valid + self.invalid} | Remaining: {remaining} | Developed by Tide")
    
    def _check_serial(self, serial_number: str, capture: bool = False):
        if len(serial_number) < 7:
            return self._output(serial_number, True)
        session = requests.Session()
        r = session.get("/api/v4/mse/getproducts?productId=" + serial_number).json() #put here your request link
        if r == []:
            return self._output(serial_number, False)
        if capture:
            serial_number = serial_number + " | " + r[0]["Name"] #put here the id of the object name if you want to capture it
        self._output(serial_number, True)
    
    def _load_serials(self):
        if not os.path.exists("serials.txt"):
            os.system("cls")
            print(self._message("Error", "File serials.txt not found", Fore.RED, True))
            time.sleep(5)
            os._exit(0)
        with open("serials.txt", "r") as f:
            for line in f.readlines():
                line = line.replace("\n", "")
                self.serials.append(line)

    def _main(self):
        os.system("cls")
        ctypes.windll.kernel32.SetConsoleTitleW("SN Checker Template | Developed by Divin")
        print(self._message("1", "Check serials from a list", Fore.GREEN, True))
        print(self._message("2", "Generate random serials and check", Fore.GREEN))
        option = int(input(f"\n{Fore.GREEN}> {Fore.WHITE}"))

        if option == 1:
            self._start_checking(True)

        elif option == 2:
            amount = int(input(self._message("Console", "Amount of serials to generate: ", Fore.GREEN, True)))
            self._start_checking(False, amount)

    def _start_checking(self, check_from_file, amount = None):
        capture = str(input(self._message("Console", "Capture model name? (y/n): ", Fore.GREEN, True)))
        threads = int(input(self._message("Console", "Threads: ", Fore.GREEN))); print()
        if capture.lower() == "y":
            capture = True
        elif capture.lower() == "n":
            capture = False
        else:
            self._main()
        if threads > 20:
            threads = 20
        if check_from_file:
            self._load_serials()
        else:
            for i in range(amount):
                generated_sn = ("").join(random.choices(string.digits, k = 7))
                self.serials.append(generated_sn)

        counter = 0
        def thread_starter():
            self._check_serial(self.serials[counter], capture)
        
        while self.checking:
            if threading.active_count() <= threads:
                try:
                    threading.Thread(target = thread_starter).start()
                    counter += 1
                except:
                    pass
                if counter >= len(self.serials):
                    self.checking = None
 
if __name__ == "__main__":
    obj = data()
    obj._main()
    input()
