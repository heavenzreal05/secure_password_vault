import getpass
import string
import os
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
import base64
import json
import sys


users = {}
if os.path.exists('user_file.json'):
    with open('user_file.json', 'r') as file:
        users = json.load(file)

def create_account():
    print("==========CREATING ACCOUNT==================")
    print("________Username_And_Password_Format_________")
    print("Username: Username characters should be alphanumeric (a-z, A-Z, 0-9) only"
                    "Username characters should be between 4 and 13")
    print("Password: Password should contain special characters"
                    "Password characters should be between 9 and 15 ")
    #taking username and password from the user
    username = input("Enter Username: ")
    password = getpass.getpass("Enter password: ")
    if not (4 <= len(username) <= 13):
        print("Wrong Username Format")
        return
    if not username.isalnum():
        print("Wrong Username Format")
        return
    if not (9 <= len(password) <= 15):
        print("Wrong Password Format")
        return
    if not any(char in string.punctuation for char in password):
        print("Wrong Password Format")
        return
    #generating random salt
    salt = os.urandom(32)
    #creating a kdf object
    kdf_object = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000)
    #creating a master cryptographic key
    hash_password = kdf_object.derive(password.encode())
    #saving details in json format
    users[username] = {
        "Salt": salt.hex(),
        "Password": hash_password.hex()
    }
    #storing the salt and the cryptographic key in a file
    with open('user_file.json', 'w') as file:
        json.dump(users, file, indent=4)
    
def authenticate_user():
    print("===============LOGING IN========================")
    #taking username and password
    user_name = input("Enter Username: ")
    pass_word = getpass.getpass("Enter Password: ")
    #opening the file with the salt and cryptographic key
    try:
        with open('user_file.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}
    #valdating username
    if user_name not in data:
        print("Wrong Password or Username")
        return None
    details = data[user_name]
    '''extracting the salt created in create_account() function so that it is used to salt the currrect password
    and compare it to the saved cryptographic key'''
    login_salt = bytes.fromhex(details['Salt'])
    new_kdf_object = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=login_salt,
        iterations=100000)
    #creating a new cryptographic key from the the login password
    new_password_salt = new_kdf_object.derive(pass_word.encode())
    #comparing the new salted password with the stored salted password
    if new_password_salt.hex() == details['Password']:
        print("Username and Password Found\nLogin Successfull")
        return user_name, login_salt, pass_word
    else:
        print("Wrong Password or Username")
        return None
#this function is meant to add a new credentials to the vault
def save_details(username, salt, password):
    '''enter the service name (eg google.com) enter the service username and then the password'''
    print("=======ADDING NEW SERVICE========")
    service = input("Enter Service Name: ")
    service_username = input("Enter Service Username: ")
    service_password = getpass.getpass("Enter Service Password: ")
    #saving the credentials in json format
    services = {}
    services[service] = {
        "Username": service_username,
        "Password": service_password
    }
    json_string = json.dumps(services)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000)
    derived_key = kdf.derive(password.encode())
    fernet_key =base64.urlsafe_b64encode(derived_key)
    cipher = Fernet(fernet_key)
    encryption = cipher.encrypt(json_string.encode())
    filename = f'{username}_vault.txt'
    with open(filename, 'wb') as file:
        file.write(encryption)
    
def show_details(username, salt, password):
    print("=====DISPLAYING AVAILABLE SERVCES=======")
    kdf = PBKDF2HMAC(
       algorithm=hashes.SHA256(),
       length=32,
       salt=salt,
       iterations=100000
       )
    filename = f'{username}_vault.txt'
    if not os.path.exists(filename):
        print(f"File Not Found {filename}")
        return
    with open(filename, 'rb') as file:
        data = file.read()
    fernet_key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    cipher = Fernet(fernet_key)
    decryption = cipher.decrypt(data) 
    print(json.loads(decryption.decode()))

if __name__ == "__main__":
    print("Enter 1 to create account\nEnter 2 to login")
    try:
        choice = int(input("Enter choice: "))
        if choice == 1:
            create_account()
        elif choice == 2:
            login_data = authenticate_user()
            if login_data:
                username, salt, password =login_data
                print("Enter 1 to add new service\nEnter 2 view available service")
                try:
                    choose = int(input("Enter Choice: "))
                    if choose == 1:
                        save_details(username, salt, password)
                    elif choose == 2:
                        show_details(username, salt, password)
                    else:
                        print("Wrong Choice")
                except ValueError:
                    print("Enter Numbers only")
        else:
            print("Wrong Choice")
    except ValueError:
        print("Enter numbers only")
       




