from sage.all import *
import random
class MyCurve:
    def __init__(self, p, D , u):
        self.p = p
        self.R = GF(self.p)
        self.u = self.R(u)
        self.D = self.R(D)
        self.zero = (u, 0)

    def check_point(self, P):
        x, y = P
        return (x**2 - self.D*y**2 - self.u**2 == 0)

    def add(self, P1, P2):
        x1, y1 = P1
        x2, y2 = P2
        if x1 - self.u == 0:
            return P2
        elif x2 - self.u == 0:
            return P1
        m1 = y1 / (x1 - self.u)
        m2 = y2 / (x2 - self.u)

        m3 = (self.D * m1 * m2 + 1) /((m1 + m2) * self.D)
        
        x3 = self.u * (self.D * m3 **2 + 1) / (self.D * m3 **2 - 1)
        y3 = 2 * self.u * m3 / (self.D * m3 **2 - 1)
        
        P3 = (int(x3), int(y3))
        assert self.check_point(P3)
        return P3

    def mul(self, n, P):
        Q = self.zero

        while n:
            if n & 1:
                Q = self.add(Q, P)
            P = self.add(P, P)
            n >>= 1
        return Q

    def lift_x(self, x):
        y2 = (x**2 - self.u**2) / self.D
        y = int(y2.sqrt())
        P = (x, y)
        assert self.check_point(P)
        return P

    def getPoint(self):
        while 1:
            x = random.randint(1 , self.p)
            try:
                return self.lift_x(x)
            except:
                pass
