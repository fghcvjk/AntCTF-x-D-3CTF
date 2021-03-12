from Crypto.Util.number import inverse
from random import randint

class elgamal:
    def __init__(self,key):
        self.p , self.q , self.g , self.y = key[:4]
        if len(key) == 5:
            self.x = key[4]
        else:
            self.x = None

    def encrypt(self,m):
        r = randint(1 , self.q)
        y1 = pow(self.g , r , self.p)
        y2 = m * pow(self.y , r , self.p) % self.p
        return y1 , y2

    def decrypt(self,c):
        if self.x != None:
           y1 , y2 = c
           m = y2 * inverse(pow(y1 , self.x , self.p), self.p) % self.p
           return m
        else:
            print('can\'t decrypt without private key')
            return -1
