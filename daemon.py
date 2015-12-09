#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
from client import get_random


while True:
    random_bytes = get_random(64)
    with open("/dev/random", 'wb') as f:
        f.write(random_bytes)
    time.sleep(1)
