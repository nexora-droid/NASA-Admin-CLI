import hashlib
import getpass
import pwinput
import time

systemname = ""
active = True
USER_FILE = "users.txt"
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def user_exists(username):
    try:
        with open(USER_FILE, "r") as f:
            for line in f:
                stored_user, _ = line.strip().split(":")
                if stored_user == username:
                    return True
    except FileNotFoundError:
        return False
    return False

def check_password(username, password):
    hashed_password = hash_password(password)
    try:
        with open(USER_FILE, "r") as f:
            for line in f:
                stored_user, stored_pass = line.strip().split(":")
                if stored_user == username and stored_pass == hashed_password:
                    return True
    except FileNotFoundError:
        return False
    return False

def add_user(username, password):
    hashed_password = hash_password(password)
    with open(USER_FILE, "a") as f:
        f.write(username + ":" + hashed_password + "\n")

def load():
    max_dots = 3
    dots = 0
    increasing = True
    wait = 0
    while True:
        print("\rInitializing System" + "." * dots + " " * (max_dots - dots), end="", flush=True)
        time.sleep(0.5)

        if increasing:
            dots += 1
            if dots == max_dots:
                increasing = False
            wait += 1
        else:
            dots = 0
            if dots == 0:
                increasing = True
            wait += 1
        if wait == 13:
            print("\nSystem Initialized")
            break

def loginsystem():
    while True:
        name = input("Login Username: ")
        if user_exists(name):
            try:
                password = pwinput.pwinput(prompt="Password: ")
            except Exception:
                password = input("(visible): ")
            if check_password(name, password):
                print("Login Successful")
                global systemname
                systemname = name
                system()
                break
            else:
                print("Login Unsuccessful! (Incorrect password/username)")
        else:
            print("User does not exist, proceeding to account creation!")
            while True:
                try:
                    password = pwinput.pwinput(prompt="Create a Password: ")
                    confirm = pwinput.pwinput(prompt="Confirm Password: ")
                except Exception:
                    password = input("(visible) ")
                    confirm = input("(visible): ")
                if password != confirm:
                    print("Passwords do not match, try again!")
                elif password == "":
                    print("Password is empty, try again!")
                else:
                    add_user(name, password)
                    print("Account Created Successfully! You can now log in!")
                    break

def system():
    isOn = True
    print("Welcome Admin! Type help to view list of available commands")
    while isOn:
        commandline = input(f"/system/NASA/admin/{systemname}/ $ ").strip().lower()
        if commandline == "help":
            print("\n\nAvailable Commands:\n"
                  "help:\n"
                  "\tlists all commands available\n"
                  "exit:\n"
                  "\tExits program, and logs out. Re-run to start again.\n"
                  "status\n"
                  "\tShows system health, and uptime\n"
                  "---------\n"
                  "schedule\n"
                  "\tShows upcoming launch schedule\n"
                  "create <mission> <predicted_launch date>\n"
                  "\tCreates a new mission\n"
                  "launch <mission>\n"
                  "\tLaunches the mission\n")
        if commandline == "exit":
            isOn = False
        if commandline == "status":
            global active
            print(f"Active: {active}")
if __name__ == "__main__":
    load()
    loginsystem()