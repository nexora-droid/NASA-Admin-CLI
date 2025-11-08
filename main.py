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
SIM_RATIO = 4

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
        "created_on": datetime.now(),
        "user": systemname,
        "launched": False
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
        print(f"- {mission['name']}, --> Predicted Launch Date: {mission['launch_date']}, --> By User: {mission['user']}")
        count += 1
    if count == 0:
        print("No missions created in the last 3 days.")


def launch_mission(mission_name):
    doc_ref = missions_collection.document(mission_name)
    doc = doc_ref.get()
    if not doc.exists:
        print(f"Mission {mission_name} does not exist")
        return
    mission = doc.to_dict()
    if mission["launched"] == True:
        print(f"Mission {mission_name} is already launched!")
        return
    start_time = datetime.now()
    doc_ref.update({
        "launched": True,
        "start_time": start_time,
        "progress": 0,
        "fuel": 100
    })
    print(f"Mission {mission_name} launched!")

def check_progress(mission_name):
    doc_ref = missions_collection.document(mission_name)
    doc = doc_ref.get()
    if not doc.exists:
        print(f"Mission {mission_name} does not exist")
        return
    mission=doc.to_dict()
    if mission["user"] != systemname:
        print(f"You can only view your own missions!")
        return
    if not mission.get("launched"):
        print(f"Mission has not been launched yet!")
        return
    start_time = mission.get('start_time')
    if hasattr(start_time, "to_datetime"):
        start_time = start_time.to_datetime()
    elapsed_realminutes = (datetime.now() - start_time).total_seconds()/60
    flight_minutes = elapsed_realminutes * SIM_RATIO
    total_flighttime = 120
    progress = min((flight_minutes / total_flighttime)*100, 100)
    fuel = max(100 - progress, 0)
    print(f'Mission Info\n'
          f'Mission Name: {mission_name}\n'
          f'Progress: {progress:.2f}%\n'
          f'Fuel Remaining: {fuel:.2f}%\n')
    doc_ref.update({
        "progress": progress,
        "fuel": fuel
    })

def delete_mission(mission_name):
    doc_ref = missions_collection.document(mission_name)
    if not doc_ref.get().exists:
        print(f"Mission {mission_name} does not exist")
        return
    doc_ref.delete()
    print(f"Mission {mission_name} deleted!")

def summary(mission_name):
    docs = missions_collection.where("user", "==", systemname).stream()
    for docs in docs:
        mission = docs.to_dict()
        print(f"Mission {mission['name']}, --> By User: {mission['user']}, --> Launched: {mission['launched']}")
def update(mission_name, new_date):
    doc_ref = missions_collection.document(mission_name)
    if not doc_ref.get().exists:
        print(f"Mission {mission_name} does not exist")
        return
    doc_ref.update({"launch_date": new_date})
    print(f"Mission date changed to {new_date}")
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
                  "\tLists missions created by global users in the past 3 days\n"
                  "progress\n"
                  "\tCheck progress of your mission\n"
                  "delete\n"
                  "\tDeletes or cancels mission\n"
                  "summary\n"
                  "\tSummarizes a given mission\n"
                  "update\n"
                  "\tUpdates predicated launch date")
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
        elif commandline== "launch":
            mission_name = input("Mission name: ")
            launch_mission(mission_name)
        elif commandline == "delete":
            mission_name = input("Mission name: ")
            delete_mission(mission_name)
        elif commandline == "update":
            mission_name = input("Mission name: ")
            new_date = input("New mission date: ")
            update(mission_name, new_date)
if __name__ == "__main__":
    load()
    loginsystem()