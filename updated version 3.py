import json
import os
import base64
from cryptography.fernet import Fernet
import re

passwords_by_category = {}
key = None

def generate_key():
    global key
    if os.path.exists("key.key"):
        with open("key.key", "rb") as key_file:
            key = key_file.read()
    else:
        key = Fernet.generate_key()
        with open("key.key", "wb") as key_file:
            key_file.write(key)

def encrypt_password(password):
    cipher = Fernet(key)
    encrypted_password = cipher.encrypt(password.encode())
    return encrypted_password

def decrypt_password(encrypted_password):
    cipher = Fernet(key)
    decrypted_password = cipher.decrypt(encrypted_password).decode()
    return decrypted_password

def add_password(service, username, password, category):
    encrypted_password = encrypt_password(password)
    if category not in passwords_by_category:
        passwords_by_category[category] = []
    passwords_by_category[category].append({
        "service": service,
        "username": username,
        "password": base64.b64encode(encrypted_password).decode(),
        "category": category
    })
    save_passwords()

def save_passwords():
    with open("passwords.json", "w") as file:
        json.dump(passwords_by_category, file, indent=4)

def load_passwords():
    global passwords_by_category
    if os.path.exists("passwords.json"):
        with open("passwords.json", "r") as file:
            try:
                data = json.load(file)
                for category, entries in data.items():
                    if isinstance(entries, list):
                        passwords_by_category[category] = [
                            {
                                "service": entry["service"],
                                "username": entry["username"],
                                "password": base64.b64decode(entry["password"].encode()),
                                "category": entry["category"]
                            }
                            for entry in entries if isinstance(entry, dict)
                        ]
            except json.JSONDecodeError:
                print("Error: passwords.json file is not in valid JSON format.")
            except KeyError as e:
                print(f"Error: Missing expected key in JSON data - {e}")

def view_passwords_by_category(category):
    if category in passwords_by_category:
        for entry in passwords_by_category[category]:
            decrypted_password = decrypt_password(entry["password"])
            print(f"Service: {entry['service']}, Username: {entry['username']}, Password: {decrypted_password}")
    else:
        print("No passwords found for this category.")

def search_passwords(service_name):
    found = False
    for category, entries in passwords_by_category.items():
        for entry in entries:
            if entry["service"] == service_name:
                decrypted_password = decrypt_password(entry["password"])
                print(f"Service: {entry['service']}, Username: {entry['username']}, Password: {decrypted_password}, Category: {category}")
                found = True
    if not found:
        print("No passwords found for the specified service.")

def generate_password(length=12):
    import random
    import string
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password

def check_password_strength(password):
    strength = {
        "length": len(password) >= 12,
        "uppercase": bool(re.search(r"[A-Z]", password)),
        "lowercase": bool(re.search(r"[a-z]", password)),
        "digits": bool(re.search(r"[0-9]", password)),
        "special": bool(re.search(r"[@$!%*?&]", password))
    }
    score = sum(1 for value in strength.values() if value)
    suggestions = []
    if not strength["length"]:
        suggestions.append("Increase length to at least 12 characters.")
    if not strength["uppercase"]:
        suggestions.append("Add at least one uppercase letter.")
    if not strength["lowercase"]:
        suggestions.append("Add at least one lowercase letter.")
    if not strength["digits"]:
        suggestions.append("Add at least one digit.")
    if not strength["special"]:
        suggestions.append("Add at least one special character.")
    strength_label = "Weak" if score <= 2 else "Medium" if score == 3 else "Strong"
    return score, suggestions, strength_label

def menu():
    load_passwords()
    generate_key()
    while True:
        print("\nPassword Manager Menu:")
        print("1. Add a new password")
        print("2. View passwords by category")
        print("3. Search passwords")
        print("4. Check password strength")
        print("5. Generate a new password")
        print("6. Exit")
        choice = input("Choose an option: ")
        if choice == "1":
            service = input("Enter service name: ")
            username = input("Enter username: ")
            password = input("Enter password (or type 'generate' to create one): ")
            if password == "generate":
                password = generate_password()
                print(f"Generated password: {password}")
            category = input("Enter category (e.g., Social, Work, Banking): ")
            add_password(service, username, password, category)
        elif choice == "2":
            category = input("Enter category to view passwords: ")
            view_passwords_by_category(category)
        elif choice == "3":
            service_name = input("Enter service name to search for: ")
            search_passwords(service_name)
        elif choice == "4":
            password = input("Enter the password to check strength: ")
            score, suggestions, strength_label = check_password_strength(password)
            print(f"Password strength: {strength_label} (Score: {score}/5)")
            if suggestions:
                print("Suggestions to improve strength:")
                for suggestion in suggestions:
                    print(f"- {suggestion}")
        elif choice == "5":
            length = int(input("Enter desired length for generated password: "))
            password = generate_password(length)
            print(f"Generated password: {password}")
        elif choice == "6":
            break
        else:
            print("Invalid option. Please try again.")

menu()
