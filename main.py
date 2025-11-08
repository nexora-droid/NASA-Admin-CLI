import hashlib
import getpass
import pwinput
import time
import firebase_admin
from firebase_admin import firestore, credentials
from datetime import datetime, timedelta

systemname = ""
active = True
USER_FILE = "users.txt"
cred = credentials.Certificate('firebasekey.json')
firebase_admin.initialize_app(cred)

db = firestore.client()
missions_collection = db.collection("missions")

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
def create_mission(name, launch_date):
    data = {
        "name": name,
        "launch_date": launch_date,
        "created_on": datetime.now()
    }
    missions_collection.document(name).set(data)
    print(f"Mission {name} created successfully! Predicted Launch Date: {launch_date}!")

def list_mission():
    docs = missions_collection.stream()
    three_days_ago = datetime.now()-timedelta(days=3)
    docs = missions_collection.where("created_on", ">=", three_days_ago).stream()
    print("\nMissions from last 3 days:\n")
    count = 0
    for doc in docs:
        mission = doc.to_dict()
        print(f"- {mission['name']}, --> Predicted Launch Date: {mission['launch_date']}")
        count += 1
    if count == 0:
        print("No missions created in the last 3 days.")




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
                  "create>\n"
                  "\tCreates a new mission\n"
                  "launch\n"
                  "\tLaunches mission (user-specific only)\n"
                  "list_missions\n"
                  "\tLists missions created by global users in the past 3 days\n")
        if commandline == "exit":
            isOn = False
        elif commandline == "status":
            global active
            print(f"Active: {active}")
        elif commandline == "create":
            mission_name = input("Mission name: ")
            launch_date = input("Predicted Launch date: ")
            create_mission(mission_name, launch_date)
        elif commandline == "list_missions":
            list_mission()
if __name__ == "__main__":
    load()
    loginsystem()