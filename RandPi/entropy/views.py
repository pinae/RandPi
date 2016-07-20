from django.conf import settings
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
import os
from base64 import b64encode
import json
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
import hmac
from binascii import unhexlify


def get_available_entropy():
    if os.path.isfile(os.path.join(os.sep, "proc", "sys", "kernel", "random", "entropy_avail")):
        with open(os.path.join(os.sep, "proc", "sys", "kernel", "random", "entropy_avail"), 'r') as f:
            entropy_avail = int(f.read())
        return entropy_avail
    else:
        return -1


def get_entropy_pool_size():
    if os.path.isfile(os.path.join(os.sep, "proc", "sys", "kernel", "random", "poolsize")):
        with open(os.path.join(os.sep, "proc", "sys", "kernel", "random", "poolsize"), 'r') as f:
            poolsize = int(f.read())
        return poolsize
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


def create_encrypted_response(data, nonce):
    iv = os.urandom(16)
    cipher = AES.new(settings.ENCRYPTION_KEY, AES.MODE_CBC, iv)
    encrypted_data = cipher.encrypt(add_pkcs7_padding(data))
    signature = hmac.new(settings.HMAC_KEY, encrypted_data + nonce, SHA256).digest()
    return HttpResponse(json.dumps({
        "iv": str(b64encode(iv), encoding='utf-8'),
        "encrypted_data": str(b64encode(encrypted_data), encoding='utf-8'),
        "hmac": str(b64encode(signature), encoding='utf-8')
    }))


class RequestProblem(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return "RequestProblem: " + self.message


def get_length_and_nonce(request):
    if 'nonce' not in request.POST:
        raise RequestProblem("You have to supply a nonce.")
    try:
        length = int(request.POST.get('length', '64'))
    except TypeError:
        raise RequestProblem("Illegal length value.")
    if length > 2048:
        raise RequestProblem("A length above 2048 Bytes is not supported.")
    if length < 1:
        raise RequestProblem("Length is too small.")
    try:
        nonce = unhexlify(request.POST['nonce'])
    except:
        raise RequestProblem("The nonce must consist of a hexadecimal number with a even count of digits.")
    if len(nonce) < length / 2:
        raise RequestProblem("The nonce has to be at least as long as the requested bytes. " +
                             "For the default length of 64 bytes: 64 hexadecimal characters.")
    return length, nonce


@csrf_exempt
def urandom(request):
    try:
        length, nonce = get_length_and_nonce(request)
    except RequestProblem as problem:
        return HttpResponse(json.dumps({
            "error": problem.message
        }))
    data = os.urandom(length)
    return create_encrypted_response(data, nonce)


@csrf_exempt
def random(request):
    try:
        length, nonce = get_length_and_nonce(request)
    except RequestProblem as problem:
        return HttpResponse(json.dumps({
            "error": problem.message
        }))
    with open(os.path.join(os.sep, 'dev', 'random'), 'rb') as f:
        data = f.read(length)
    return create_encrypted_response(data, nonce)


@csrf_exempt
def hwrandom(request):
    try:
        length, nonce = get_length_and_nonce(request)
    except RequestProblem as problem:
        return HttpResponse(json.dumps({
            "error": problem.message
        }))
    if os.path.exists(os.path.join(os.sep, 'dev', 'hwrandom')):
        with open(os.path.join(os.sep, 'dev', 'hwrandom'), 'rb') as device:
            data = device.read(length)
        return create_encrypted_response(data, nonce)
    if os.path.exists(os.path.join(os.sep, 'dev', 'hwrng')):
        with open(os.path.join(os.sep, 'dev', 'hwrng'), 'rb') as device:
            data = device.read(length)
        return create_encrypted_response(data, nonce)
    else:
        return HttpResponse(json.dumps({
            "error": "No hardware random device found."
        }))


def statistics(request):
    return HttpResponse(json.dumps({
        "pool_size": get_entropy_pool_size(),
        "available": get_available_entropy()
    }))


def index(request):
    return HttpResponse("""<!DOCTYPE html>
    <html>
      <head>
        <meta charset="UTF-8">
        <script src="static/angular2-polyfills.min.js"></script>
        <script src="static/Rx.umd.min.js"></script>
        <script src="static/angular2-all.umd.min.js"></script>
        <script src="static/app.component.js"></script>
        <script src="static/boot.js"></script>
      </head>
      <body>
        <my-app>Loading ...</my-app>
      </body>
    </html>""", content_type='text/html')


def static(request, filename):
    if os.path.exists(os.path.join("entropy", "static", filename)):
        with open(os.path.join("entropy", "static", filename), 'r') as f:
            return HttpResponse(f.read(), content_type='application/javascript')
    else:
        raise Http404("The file " + filename + " was not found.")
