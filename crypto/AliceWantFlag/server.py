from elgamal import elgamal
import socketserver
from prikey import server_prikey , AlicePasswd
from pubkey import Alice_pubkey
from secret import Alice_flag , ctfer_flag
import random
import signal
from os import urandom
from Crypto.Util.number import long_to_bytes , bytes_to_long
from Crypto.Cipher import AES

MENU = "1. signup  2.signin"
XOR = lambda s1,s2 :bytes([x1^x2 for x1 , x2 in zip(s1,s2)])
def pad(m):
    m += bytes([16 - len(m) % 16] * (16 - len(m) % 16))
    return m

def unpad(m):
    padlen = m[-1]
    for i in range(1 , padlen + 1):
        if m[-i] != m[-1]:
            return b''
    return m[:-m[-1]]
    
class server(socketserver.BaseRequestHandler):
    
    def setup(self):
        self.pubkey = {}
        self.passwd = {}
        self.prikey = elgamal(server_prikey)
        self.pubkey[b'Alice'] = elgamal(Alice_pubkey)
        self.passwd[b'Alice'] = AlicePasswd

    def _recv(self):
        data = self.request.recv(1024)
        return data.strip()

    def _send(self, msg, newline=True):
        if isinstance(msg , bytes):
            msg += b'\n'
        else:
            msg += '\n'
            msg = msg.encode()
        self.request.sendall(msg)

    def enc_send(self, msg , usrid , enc_key = b''):
        if enc_key == b'':
            pubenc = self.pubkey[usrid]
            y1 , y2 = pubenc.encrypt(bytes_to_long(msg))
            self._send(str(y1) + ', ' + str(y2))
        else:
            assert len(enc_key) == 16
            aes = AES.new(enc_key , AES.MODE_ECB)
            self._send(aes.encrypt(pad(msg)))
    
    def dec_recv(self,  enc_key = b''):
        msg = self._recv()
        if enc_key == b'':
            c = [int(i) for i in msg.split(b', ')]
            m = self.prikey.decrypt(c)
            print(long_to_bytes(m))
            return long_to_bytes(m)
        else:
            assert len(enc_key) == 16
            aes = AES.new(enc_key , AES.MODE_ECB)
            return unpad(aes.decrypt(msg))
    def signup(self):
        if len(self.passwd) > 5:
            self._send('sorry, the number of users is out of limit')
            return 0
        self._send('please give me your name')
        userid = self._recv()
        if len(userid) > 20:
            self._send('your id can\'t be too long')
            return 0
        elif userid in self.passwd:
            self._send('the name has been used')
            return 0
        else:
            self._send('please give me your passwd(encrypted)')
            userpasswd = self.dec_recv()
            if len(userpasswd) > 11:
                self._send('your password can\'t be too long')
                return 0
            else:
                self.passwd[userid] = userpasswd
            self._send('please give me your publickey')
            userpubkey = self._recv()
            try:
                userpubkey = [int(i) for i in userpubkey[1:-1].split(b', ')]
            except:
                self._send('publickey format error')
                self.passwd.pop(userid)
                return 0
            self.pubkey[userid] = elgamal(userpubkey)
            self._send('sign up success')
            return 1
    def signin(self):
        self._send('please give me your name')
        userid = self._recv()
        if userid not in self.passwd:
            self._send('sorry the userid is not existed')
            return 0
        while 1:
            random.seed(urandom(8))
            r =random.getrandbits(8 * 11)
            self._send('please give me your passwd(encrypted and xored by r)')
            self._send(str(r))
            userdata = self.dec_recv()
            if bytes_to_long(userdata) == r ^ bytes_to_long(self.passwd[userid]):
                self._send('signin success')
                break
            else:
                self._send('password error')
        endkey = urandom(5)
        key = userdata + endkey
        self._send('now let\'s communicate with this key')
        self.enc_send(endkey , userid)
        return userid , key
    def handle(self):
        signal.alarm(240)
        key = b''
        userid = ''
        while 1:
            self._send(MENU)
            choice = self._recv()
            if choice == b'1':
                self.signup()
            elif choice == b'2':
                temp = self.signin()
                if temp != 0:
                    userid , key = temp
                    break
            else:
                self._send('error')
        msg = self.dec_recv(enc_key= key)
        if msg == b'I am a ctfer.Please give me flag':
            self.enc_send(b'ok, your flag is here ' + ctfer_flag , userid , enc_key= key)
        elif msg == b'I am Alice, Please give me true flag' and userid == b'Alice':
            self.enc_send(b'Hi Alice, your flag is ' + Alice_flag , userid , enc_key= key)
        return 0

    def finish(self):
        self.request.close()

class ForkedServer(socketserver.ForkingMixIn, socketserver.TCPServer):
    pass

if __name__ == "__main__":
    HOST, PORT = '0.0.0.0', 10001
    server = ForkedServer((HOST, PORT), server)
    server.allow_reuse_address = True
    server.serve_forever()
 
