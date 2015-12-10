from django.conf import settings
from django.http import HttpResponse
import os
from base64 import b64encode
import json
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import modes, algorithms, Cipher
from cryptography.hazmat.primitives import hashes, hmac, padding


def index(request):
    return HttpResponse("statistics")


def get_available_entropy():
    if os.path.isfile(os.path.join(os.sep, "proc", "sys", "kernel", "random", "entropy_avail")):
        with open(os.path.join(os.sep, "proc", "sys", "kernel", "random", "entropy_avail"), 'r') as f:
            entropy_avail = int(f.read())
        return entropy_avail
    else:
        return -1


def create_encrypted_response(data):
    backend = default_backend()
    cipher = Cipher(algorithms.AES(settings.ENCRYPTION_KEY), modes.CBC(settings.ENCRYPTION_IV), backend=backend)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data)
    padded_data += padder.finalize()
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    h = hmac.HMAC(settings.ENCRYPTION_KEY, hashes.SHA256(), backend=backend)
    h.update(encrypted_data)
    return HttpResponse(json.dumps({
        "encrypted_data": str(b64encode(encrypted_data), encoding='utf-8'),
        "hmac": str(b64encode(h.finalize()), encoding='utf-8')
    }))


def urandom(request):
    try:
        length = int(request.GET.get('length', '64'))
    except TypeError:
        return HttpResponse(json.dumps({
            "error": "Illegal length value."
        }))
    if length > 2048:
        return HttpResponse(json.dumps({
            "error": "A length above 2048 Bytes is not supported."
        }))
    if length < 1:
        return HttpResponse(json.dumps({
            "error": "Length is too small."
        }))
    data = os.urandom(length)
    return create_encrypted_response(data)


def random(request):
    try:
        length = int(request.GET.get('length', '64'))
    except TypeError:
        return HttpResponse(json.dumps({
            "error": "Illegal length value."
        }))
    if length > 2048:
        return HttpResponse(json.dumps({
            "error": "A length above 2048 Bytes is not supported."
        }))
    if length < 1:
        return HttpResponse(json.dumps({
            "error": "Length is too small."
        }))
    with open(os.path.join(os.sep, 'dev', 'random'), 'rb') as f:
        data = f.read(length)
    return create_encrypted_response(data)


def hwrandom(request):
    return HttpResponse("hwrandom")
