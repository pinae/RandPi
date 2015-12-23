#!/usr/bin/python3
# -*- coding: utf-8 -*-

from django.conf.urls import url
from . import views

urlpatterns = [
    url('^$', views.index, name='index'),
    url('static/(.*)$', views.static, name='static'),
    url('^statistics', views.statistics, name='statistics'),
    url('^random', views.random, name='random'),
    url('^urandom', views.urandom, name='urandom'),
    url('^hwrandom', views.hwrandom, name='hwrandom'),
]
