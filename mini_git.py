import shutil
import os
import sys
import json
import hashlib
from datetime import datetime

# Storage directory
MINIGIT_DIR = ".minigit"
DATA_FILE = os.path.join(MINIGIT_DIR, "commits.json")


# Create storage if it does not exist
def initialize():

    os.makedirs(MINIGIT_DIR, exist_ok=True)

    if not os.path.exists(DATA_FILE):
        data = {
            "staged": {},
            "commits": []
        }

        with open(DATA_FILE, "w") as file:
            json.dump(data, file, indent=4)


# Load stored data
def load_data():

    with open(DATA_FILE, "r") as file:
        return json.load(file)


# Save stored data
def save_data(data):

    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)


# Add command
def add_file(filename):

    if not os.path.isfile(filename):
        print("File not found!")
        return

    data = load_data()

    with open(filename, "r") as file:
        content = file.read()

    data["staged"][filename] = content

    save_data(data)

    print(filename, "staged successfully!")


# Commit command
def commit_changes(message):

    data = load_data()

    if not data["staged"]:
        print("Nothing to commit!")
        return

    commit_date = datetime.now().isoformat(timespec="seconds")

    commit_content = {
        "date": commit_date,
        "message": message,
        "file_contents": data["staged"]
    }

    # Generate short commit ID
    hash_input = json.dumps(
        commit_content,
        sort_keys=True
    )

    commit_id = hashlib.sha1(
        hash_input.encode()
    ).hexdigest()[:7]

    commit_content["id"] = commit_id

    data["commits"].append(commit_content)

    # Clear staged files after commit
    data["staged"] = {}

    save_data(data)

    print("Commit created successfully!")
    print("Commit ID:", commit_id)


# Log command
def show_log():

    data = load_data()

    commits = data["commits"]

    if not commits:
        print("No commits found!")
        return

    print("\nCommit History")
    print("--------------------")

    for commit in reversed(commits):

        print("Commit:", commit["id"])
        print("Date:", commit["date"])
        print("Message:", commit["message"])
        print("--------------------")


def push(remote_folder):

    data = load_data()

    os.makedirs(remote_folder, exist_ok=True)

    # Store every commit using its commit ID
    for commit in data["commits"]:

        commit_id = commit["id"]

        file_path = os.path.join(
            remote_folder,
            commit_id + ".json"
        )

        with open(file_path, "w") as file:
            json.dump(commit, file, indent=4)

    # Store commit order
    history_file = os.path.join(
        remote_folder,
        "history.json"
    )

    with open(history_file, "w") as file:
        json.dump(
            [commit["id"] for commit in data["commits"]],
            file,
            indent=4
        )

    print("Push successful!")
    print("Total commits pushed:", len(data["commits"]))


def pull(remote_folder):

    if not os.path.isdir(remote_folder):
        print("Remote folder not found!")
        return

    history_file = os.path.join(
        remote_folder,
        "history.json"
    )

    if not os.path.exists(history_file):
        print("No remote commits found!")
        return

    with open(history_file, "r") as file:
        commit_ids = json.load(file)

    data = load_data()

    existing_ids = {
        commit["id"] for commit in data["commits"]
    }

    for commit_id in commit_ids:

        if commit_id not in existing_ids:

            file_path = os.path.join(
                remote_folder,
                commit_id + ".json"
            )

            with open(file_path, "r") as file:
                commit = json.load(file)

            data["commits"].append(commit)

    # Save downloaded commits
    save_data(data)

    # Restore latest file contents
    if data["commits"]:

        latest_commit = data["commits"][-1]

        for filename, content in latest_commit["file_contents"].items():

            with open(filename, "w") as file:
                file.write(content)

    print("Pull successful!")
    print("Total commits downloaded:", len(data["commits"]))


# Main program
initialize()

if len(sys.argv) < 2:
    print("Usage: python mini_git.py [add|commit|log]")
    sys.exit()

command = sys.argv[1]

if command == "add":

    if len(sys.argv) < 3:
        print("Please provide a filename.")
    else:
        add_file(sys.argv[2])

elif command == "commit":

    if len(sys.argv) < 3:
        print("Please provide a commit message.")
    else:
        message = " ".join(sys.argv[2:])
        commit_changes(message)

elif command == "log":

    show_log()


elif command == "push":

    if len(sys.argv) < 3:
        print("Please provide remote folder.")
    else:
        push(sys.argv[2])

elif command == "pull":

    if len(sys.argv) < 3:
        print("Please provide remote folder.")
    else:
        pull(sys.argv[2])

else:
    print("Invalid command!")


