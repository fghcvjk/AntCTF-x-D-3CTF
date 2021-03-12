from Crypto.Util.number import *
from gmpy2 import *
from random import *

def elgamal_key(qsize , psize):
    q = getPrime(qsize)
    x = randint(2 , q-1)
    k = getPrime(psize-qsize)
    while 1:
        if is_prime(k*q + 1):
            break
        else:
            k += 1
    p = k * q + 1
    while 1:
        g = randint(1 , p)
        g = pow(g , k , p)
        if g != 1:
            break
    y = pow(g , x , p)
    pubkey = (p , q , g , y)
    prikey = (p ,q , g ,y , x)
    return pubkey , prikey 

server_pubkey , server_prikey = elgamal_key(190 , 512)
Alice_pubkey , Alice_prikey = elgamal_key(190 , 512)
f1 = open('./prikey.py' , 'w')
f2 = open('./pubkey.py' , 'w')
f2.write('server_pubkey = '+str(server_pubkey) + '\n')
f2.write('Alice_pubkey = '+str(Alice_pubkey) + '\n')
f1.write('server_prikey = ' + str(server_prikey) + '\n')
f1.write('Alice_prikey = ' + str(Alice_prikey) + '\n')