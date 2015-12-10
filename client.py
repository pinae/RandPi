#!/usr/bin/python3
# -*- coding: utf-8 -*-

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, hmac, padding
from cryptography.hazmat.primitives.ciphers import modes, algorithms, Cipher
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.exceptions import InvalidSignature
from base64 import b64decode
import sys

SHARED_SECRET = "Mein tolles langes Passwort, das total sicher ist. " + \
                "Das sieht man an den Sonderzeichen wie / (Slash) oder $ (Dollar). " + \
                "Außerdem enthält diese Passphrase einfach eine Menge Zeichen, die ein Angreifer erst mal erraten muss."
SHARED_SALT = "pepper"
backend = default_backend()
pbkdf2 = PBKDF2HMAC(
    algorithm=hashes.SHA384(),
    length=48,
    salt=SHARED_SALT.encode('utf-8'),
    iterations=32000,
    backend=backend
)
base_key = pbkdf2.derive(SHARED_SECRET.encode('utf-8'))
DECRYPTION_KEY = base_key[:32]
DECRYPTION_IV = base_key[32:48]


def get_random(length=64):
    request = requests.get('http://127.0.0.1:8000/entropy/random?length=' + str(length))
    data = request.json()
    h = hmac.HMAC(DECRYPTION_KEY, hashes.SHA256(), backend=backend)
    h.update(b64decode(data['encrypted_data']))
    try:
        h.verify(b64decode(data['hmac']))
    except InvalidSignature:
        print("Wrong signature!")
        exit(1)
    cipher = Cipher(algorithms.AES(DECRYPTION_KEY), modes.CBC(DECRYPTION_IV), backend=backend)
    decrypter = cipher.decryptor()
    padded_data = decrypter.update(b64decode(data['encrypted_data'])) + decrypter.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(padded_data)
    data += unpadder.finalize()
    return data

if __name__ == "__main__":
    sys.stdout.buffer.write(get_random())
