import socketserver
from Crypto.PublicKey import RSA
from Crypto.Util.number import getPrime , bytes_to_long
from Curve import MyCurve
from hashlib import sha256
import os
import string
import random
import signal
from secret import flag

BIT = 2048
p = 9688074905643914060390149833064012354277254244638141162997888145741631958242340092013958501673928921327767591959476890238698855704376126231923819603296257

class Task(socketserver.BaseRequestHandler):

    def proof_of_work(self):
        random.seed(os.urandom(8))
        proof = ''.join([random.choice(string.ascii_letters+string.digits) for _ in range(20)])
        _hexdigest = sha256(proof.encode()).hexdigest()
        self.send(f"sha256(XXXX+{proof[4:]}) == {_hexdigest}".encode())
        self.send(b'Give me XXXX: ')
        x = self.recv()
        if len(x) != 4 or sha256(x+proof[4:].encode()).hexdigest() != _hexdigest:
            self.send('wrong')
            return False
        return True

    def recv(self):
        data = self.request.recv(1024)
        return data.strip()

    def send(self, msg, newline=True):
        if isinstance(msg , bytes):
            msg += b'\n'
        else:
            msg += '\n'
            msg = msg.encode()
        self.request.sendall(msg)

    def key_gen(self , bit):
        key = RSA.generate(bit)
        return key

    def ot(self , point):
        x , y = point
        random.seed(os.urandom(8))

        key = self.key_gen(BIT)
        self.send('n = ' + str(key.n))
        self.send('e = ' + str(key.e))
        x0 = random.randint(1 , key.n)
        x1 = random.randint(1 , key.n)
        self.send("x0 = " + str(x0))
        self.send("x1 = " + str(x1))

        self.send("v = ")
        v = int(self.recv())
        m0_ = (x + pow(v - x0, key.d, key.n)) % key.n
        m1_ = (y + pow(v - x1, key.d, key.n)) % key.n
        self.send("m0_ = " + str(m0_))
        self.send("m1_ = " + str(m1_))
    def handle(self):
        signal.alarm(180)
        if not self.proof_of_work():
            return 0
        e = bytes_to_long(os.urandom(32))
        u = random.randint(1 , p)
        D = random.randint(1 , p)
        curve = MyCurve(p , D , u)
        self.send('p = ' + str(p))
        self.send('D = ' + str(D))
        for i in range(3):
            G = curve.getPoint()
            self.ot(G)
            P = curve.mul(e , G)
            self.ot(P)
            self.send("do you know my e?")
            guess = int(self.recv())
            if guess == e:
                self.send("oh no!")
                self.send(flag)
                return 0
            else:
                self.send("Ha, I know you can't get it.")

class ForkedServer(socketserver.ForkingMixIn, socketserver.TCPServer):
    pass

if __name__ == "__main__":
    HOST, PORT = '0.0.0.0', 10000
    server = ForkedServer((HOST, PORT), Task)
    server.allow_reuse_address = True
    server.serve_forever()
 
