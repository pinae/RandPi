from django.conf import settings
from django.http import HttpResponse
import os
from base64 import b64encode
import json
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
import hmac


def index(request):
    return HttpResponse("statistics")


def get_available_entropy():
    if os.path.isfile(os.path.join(os.sep, "proc", "sys", "kernel", "random", "entropy_avail")):
        with open(os.path.join(os.sep, "proc", "sys", "kernel", "random", "entropy_avail"), 'r') as f:
            entropy_avail = int(f.read())
        return entropy_avail
    else:
        return -1


def add_pkcs7_padding(data):
        """
        Adds PKCS7 padding so it can be divided into full blocks of 16 bytes.
        :param bytes data: data without padding
        :return: padded data
        :rtype: bytes
        """
        length = 16 - (len(data) % 16)
        data += bytes([length])*length
        return data


def create_encrypted_response(data):
    cipher = AES.new(settings.ENCRYPTION_KEY, AES.MODE_CBC, settings.ENCRYPTION_IV)
    encrypted_data = cipher.encrypt(add_pkcs7_padding(data))
    signature = hmac.new(settings.ENCRYPTION_KEY, encrypted_data, SHA256).digest()
    return HttpResponse(json.dumps({
        "encrypted_data": str(b64encode(encrypted_data), encoding='utf-8'),
        "hmac": str(b64encode(signature), encoding='utf-8')
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
    with open(os.path.join(os.sep, 'dev', 'hwrng'), 'rb') as f:
        data = f.read(length)
    return create_encrypted_response(data)
