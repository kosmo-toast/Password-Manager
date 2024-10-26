from cryptography.fernet import Fernet
import json
import os

KEY_FILE = 'encryption.key'
DATA_FILE = 'passwords.json'

def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as key_file:
            key_file.write(key)
    else:
        with open(KEY_FILE, 'rb') as key_file:
            key = key_file.read()
    return key

key = load_key()
fernet = Fernet(key)

def add_password(service, username, password):
    encrypted_password = fernet.encrypt(password.encode()).decode()
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            data = json.load(file)
    else:
        data = {}

    data[service] = {'username': username, 'password': encrypted_password}
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file)

    print(f"Password for '{service}' added successfully!")

def get_password(service):
    if not os.path.exists(DATA_FILE):
        print("No saved passwords found.")
        return

    with open(DATA_FILE, 'r') as file:
        data = json.load(file)

    if service in data:
        encrypted_password = data[service]['password']
        password = fernet.decrypt(encrypted_password.encode()).decode()
        print(f"Service: {service}\nUsername: {data[service]['username']}\nPassword: {password}")
    else:
        print(f"No password found for '{service}'")

def list_services():
    if not os.path.exists(DATA_FILE):
        print("No saved passwords found.")
        return

    with open(DATA_FILE, 'r') as file:
        data = json.load(file)

    print("Saved services:")
    for service in data.keys():
        print(f"- {service}")

def main():
    while True:
        print("\nPassword Manager")
        print("1. Add new password")
        print("2. Retrieve a password")
        print("3. List all services")
        print("4. Exit")

        choice = input("Choose an option: ")

        if choice == '1':
            service = input("Enter the service name: ")
            username = input("Enter the username: ")
            password = input("Enter the password: ")
            add_password(service, username, password)
        elif choice == '2':
            service = input("Enter the service name: ")
            get_password(service)
        elif choice == '3':
            list_services()
        elif choice == '4':
            print("Exiting Password Manager.")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
