import time
import hashlib
import getpass

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

def system():
    while True:
        name = input("Login Username: ")
        if user_exists(name):
            try:
                password = getpass.getpass(prompt="Password: ")
            except Exception:
                password = input("Password (visible): ")
            if check_password(name, password):
                print("Login Successful")
                break
            else:
                print("Login Unsuccessful! (Incorrect password/username")
        else:
            print("User does not exist, proceeding to account creation!")
            while True:
                try:
                    password = getpass.getpass(prompt="Create a Password: ")
                    confirm = getpass.getpass(prompt="Confirm Password: ")
                except Exception:
                    password = input("Password (visible): ")
                    confirm = input("Confirm Password (visible): ")
                if password != confirm:
                    print("Passwords do not match, try again!")
                elif password == "":
                    print("Password is empty, try again!")
                else:
                    add_user(name, password)
                    print("Account Created Successfully! You can now log in!")
                    break

if __name__ == "__main__":
    load()
    system()