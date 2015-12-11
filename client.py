#!/usr/bin/python3
# -*- coding: utf-8 -*-

import requests
from Crypto.Cipher import AES
import hashlib
import hmac
from base64 import b64decode
import sys

SHARED_SECRET = ("Mein tolles langes Passwort, das total sicher ist. " +
                 "Das sieht man an den Sonderzeichen wie / (Slash) oder $ (Dollar). " +
                 "Außerdem enthält diese Passphrase einfach eine Menge Zeichen, " +
                 "die ein Angreifer erst mal erraten muss.").encode('utf-8')
SHARED_SALT = "pepper".encode('utf-8')
base_key = hashlib.pbkdf2_hmac('sha384', SHARED_SECRET, SHARED_SALT, 32000)
ENCRYPTION_KEY = base_key[:32]
ENCRYPTION_IV = base_key[32:48]


def remove_pkcs7_padding(data):
        return data[:-data[-1]]


def get_random(length=64):
    request = requests.get('http://127.0.0.1:8000/entropy/random?length=' + str(length))
    data = request.json()
    if hmac.new(ENCRYPTION_KEY,
                b64decode(data['encrypted_data']),
                hashlib.sha256).digest() != b64decode(data['hmac']):
        print("Wrong signature!")
        exit(1)
    cipher = AES.new(ENCRYPTION_KEY, AES.MODE_CBC, ENCRYPTION_IV)
    data = remove_pkcs7_padding(cipher.decrypt(b64decode(data['encrypted_data'])))
    return data

if __name__ == "__main__":
    sys.stdout.buffer.write(get_random())
