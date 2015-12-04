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
