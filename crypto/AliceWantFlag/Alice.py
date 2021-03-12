import socket
from elgamal import elgamal
from pubkey import server_pubkey
from prikey import Alice_prikey , AlicePasswd
from Crypto.Util.number import long_to_bytes , bytes_to_long
from Crypto.Cipher import AES
import socketserver , signal
def pad(m):
    m += bytes([16 - len(m) % 16] * (16 - len(m) % 16))
    return m

def unpad(m):
    return m[:-m[-1]]
    
class Alice:
    def __init__(self , ip , port):
        self.pridec = elgamal(Alice_prikey)
        self.pubenc = elgamal(server_pubkey)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((ip, port))
    
    def _recv(self):
        data = self.s.recv(1024)
        return data.strip()

    def _send(self, msg):
        if isinstance(msg , str):
            msg = msg.encode()
        self.s.send(msg)

    def enc_send(self, msg , enc_key = b''):
        if enc_key == b'':
            y1 , y2 = self.pubenc.encrypt(bytes_to_long(msg))

            self._send(str(y1) + ', ' + str(y2))
        else:
            assert len(enc_key) == 16
            aes = AES.new(enc_key , AES.MODE_ECB)
            self._send(aes.encrypt(pad(msg)))
    
    def dec_recv(self,  enc_key = b''):
        msg = self._recv()
        if enc_key == b'':
            c = [int(i) for i in msg.split(b', ')]
            m = self.pridec.decrypt(c)
            return long_to_bytes(m)
        else:
            assert len(enc_key) == 16
            aes = AES.new(enc_key , AES.MODE_ECB)
            return unpad(aes.decrypt(msg))

    def main(self):
        firstmsg = self._recv()
        if firstmsg != b'1. signup  2.signin':
            return 0
        self._send('2')
        self._recv()
        self._send('Alice')
        self._recv()
        r = int(self._recv())
        userdata = long_to_bytes(bytes_to_long(AlicePasswd) ^ r)
        self.enc_send(userdata)
        self._recv()
        self._recv()
        endkey = self.dec_recv()
        key = userdata + endkey
        self.enc_send(b'I am a ctfer.Please give me flag' , enc_key= key)
        return self.dec_recv(enc_key= key)

class Task(socketserver.BaseRequestHandler):
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
    
    def handle(self):
        signal.alarm(60)
        self._send('Hello, I am Alice, can you tell me the address of the server?\nIn return, I will give you the ctf_flag')
        try:
            addr = self._recv()
            ip, port = [x.strip() for x in addr.split(b':')]
            
            port = int(port)
        except:
            ip, port = '0.0.0.0', 10001
        a = Alice(ip , port)
        msg = a.main()
        self._send(b'Thanks, here is your flag')
        self._send(msg)

class ForkedServer(socketserver.ForkingMixIn, socketserver.TCPServer):
    pass

if __name__ == "__main__":
    HOST, PORT = '0.0.0.0', 10003
    server = ForkedServer((HOST, PORT), Task)
    server.allow_reuse_address = True
    server.serve_forever()
 