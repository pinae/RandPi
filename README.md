# RandPi
Entropy-As-A-Service Server for the raspberry pi. Uses Django 1.9.

Usage
=====

Send requests to `http://domain.tld/entropy/` to get statistics (entropy amount available, etc.). 

Encrypted random numbers come from `http://domain.tld/entropy/random`, `http://domain.tld/entropy/urandom` or 
`http://domain.tld/entropy/hwrandom`. Random returns bytes from /dev/random which blocks if the entropy count
is low. Urandom returns bytes from /dev/urandom which does not block. Hwrandom returns bytes from the hardware
RNG which is probably very slow. 

There is no sanity-check for data from hwrandom. Be careful that the hardware may be errorous. If in doubt use 
random because Linux whitens the inserted entropy.

Installation
============

You probably need `sudo apt-get install python3-dev libffi-dev`.

On Raspbian `pyvenv` is missing. You can fix this by installing a new version of Python:

    wget https://www.python.org/ftp/python/3.5.1/Python-3.5.1.tgz
    tar xzf Python-3.5.1.tgz
    cd Python-3.5.1/
    sudo apt-get install libssl-dev openssl
    ./configure
    make -j 5
    sudo make install

Clone the git repository: `git clone https://github.com/pinae/RandPi.git`

Enter the directory: `cd RandPi`

Use `pyvenv` to create a virtualenv: `pyvenv venv`
Activate it with: `source venv/bin/activate`

After that you can install all requirements at once with: `sudo pip install -r requirements.txt`

UWsgi
-----
Install: `sudo apt-get install uwsgi uwsgi-plugin-python3`

Create a configuration for the RandPi-app in `/etc/uwsgi/apps-available/RandPi.ini`:

    [uwsgi]
    vhost = true
    gid = www-data
    uid = www-data
    plugins = python3
    socket = /tmp/RandPi.sock
    master = true
    enable-threads = true
    processes = 1
    wsgi-file = /var/www/vhost/RandPi/RandPi/RandPi/wsgi.py
    virtualenv = /var/www/vhost/RandPi/venv
    chdir = /var/www/vhost/RandPi/RandPi
    touch-reload = /var/www/vhost/RandPi/RandPi/reload
    
Do not forget to activate the app with a symlink: 
`ln -s /etc/uwsgi/apps-available/RandPi.ini /etc/uwsgi/apps-enabled/RandPi.ini`

Touch the reload file: `touch /var/www/vhost/RandPi/RandPi/reload`
