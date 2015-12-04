from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("statistics")


def urandom(request):
    return HttpResponse("urandom")


def random(request):
    return HttpResponse("random")


def hwrandom(request):
    return HttpResponse("hwrandom")
