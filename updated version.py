import string
import secrets
import re
from cryptography.fernet import Fernet
from datetime import datetime

def generate_key():
    return Fernet.generate_key()

def load_key():
    # Replace with your actual key loading mechanism or a saved key
    return b'your_saved_key_here'  # Use generate_key() to create a key if none exists

def encrypt_password(password, key):
    cipher = Fernet(key)
    return cipher.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password, key):
    cipher = Fernet(key)
    return cipher.decrypt(encrypted_password.encode()).decode()

passwords_by_category = {
    "Social": [],
    "Work": [],
    "Banking": [],
}

def generate_password(length=12, include_symbols=True):
    characters = string.ascii_letters + string.digits
    if include_symbols:
        characters += string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

def check_password_strength(password):
    strength = {
        "Length": len(password) >= 8,
        "Upper": re.search(r"[A-Z]", password),
        "Lower": re.search(r"[a-z]", password),
        "Digit": re.search(r"\d", password),
        "Special": re.search(r"\W", password)
    }
    score = sum(strength.values())
    suggestions = [key for key, passed in strength.items() if not passed]
    return score, suggestions

def add_password(service, username, password, category, passwords_by_category, key):
    encrypted_password = encrypt_password(password, key)
    entry = {
        "service": service,
        "username": username,
        "password": encrypted_password,
        "last_modified": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    if category in passwords_by_category:
        passwords_by_category[category].append(entry)
    else:
        passwords_by_category[category] = [entry]

def retrieve_password(service, category, passwords_by_category, key):
    for entry in passwords_by_category.get(category, []):
        if entry["service"].lower() == service.lower():
            decrypted_password = decrypt_password(entry["password"], key)
            return {
                "service": entry["service"],
                "username": entry["username"],
                "password": decrypted_password,
                "last_modified": entry["last_modified"]
            }
    return None

def view_passwords_by_category(category, passwords_by_category, key):
    passwords = []
    for entry in passwords_by_category.get(category, []):
        decrypted_password = decrypt_password(entry["password"], key)
        passwords.append({
            "service": entry["service"],
            "username": entry["username"],
            "password": decrypted_password,
            "last_modified": entry["last_modified"]
        })
    return passwords

def search_passwords(query, passwords_by_category, key):
    results = []
    for category, entries in passwords_by_category.items():
        for entry in entries:
            if query.lower() in entry["service"].lower():
                decrypted_password = decrypt_password(entry["password"], key)
                results.append({
                    "service": entry["service"],
                    "username": entry["username"],
                    "password": decrypted_password,
                    "category": category,
                    "last_modified": entry["last_modified"]
                })
    return results

def menu():
    key = load_key()
    
    while True:
        print("\nPassword Manager Menu")
        print("1. Add a password")
        print("2. Retrieve a password")
        print("3. View passwords by category")
        print("4. Search passwords")
        print("5. Generate a new password")
        print("6. Check password strength")
        print("7. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            service = input("Enter service name: ")
            username = input("Enter username: ")
            password = input("Enter password (or type 'generate' to create one): ")
            if password.lower() == "generate":
                length = int(input("Enter password length: "))
                include_symbols = input("Include symbols (y/n): ").lower() == "y"
                password = generate_password(length, include_symbols)
                print("Generated password:", password)
            category = input("Enter category (e.g., Social, Work, Banking): ")
            add_password(service, username, password, category, passwords_by_category, key)
            print("Password added successfully.")

        elif choice == "2":
            category = input("Enter category: ")
            service = input("Enter service name: ")
            result = retrieve_password(service, category, passwords_by_category, key)
            if result:
                print("Service:", result["service"])
                print("Username:", result["username"])
                print("Password:", result["password"])
                print("Last Modified:", result["last_modified"])
            else:
                print("Password not found.")

        elif choice == "3":
            category = input("Enter category: ")
            results = view_passwords_by_category(category, passwords_by_category, key)
            if results:
                for entry in results:
                    print("\nService:", entry["service"])
                    print("Username:", entry["username"])
                    print("Password:", entry["password"])
                    print("Last Modified:", entry["last_modified"])
            else:
                print("No passwords found in this category.")

        elif choice == "4":
            query = input("Enter search query: ")
            results = search_passwords(query, passwords_by_category, key)
            if results:
                for entry in results:
                    print("\nService:", entry["service"])
                    print("Username:", entry["username"])
                    print("Password:", entry["password"])
                    print("Category:", entry["category"])
                    print("Last Modified:", entry["last_modified"])
            else:
                print("No matching passwords found.")

        elif choice == "5":
            length = int(input("Enter password length: "))
            include_symbols = input("Include symbols (y/n): ").lower() == "y"
            password = generate_password(length, include_symbols)
            print("Generated password:", password)

        elif choice == "6":
            password = input("Enter the password to check strength: ")
            score, suggestions = check_password_strength(password)
            print(f"Password Strength Score: {score}/5")
            if suggestions:
                print("Suggestions to improve:", ", ".join(suggestions))
            else:
                print("Your password is strong.")

        elif choice == "7":
            print("Exiting Password Manager.")
            break

        else:
            print("Invalid choice. Please try again.")

menu()
