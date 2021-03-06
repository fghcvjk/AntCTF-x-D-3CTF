from collections import namedtuple

PublicKey = namedtuple('PublicKey', ['n', 'b'])
SecretKey = namedtuple('SecretKey', ['p', 'q', 'A'])


def gen_key():
    p = random_prime(2^512, lbound=2^511)
    q = random_prime(2^512, lbound=2^511)
    n = p * q

    a11, a12, a21 = [random_prime(2^100) for _ in range(3)]
    a22 = random_prime(2^100)
    while a11 * a22 == a12 * a21:
        a22 = random_prime(2^100)
    A = Matrix(ZZ, [[a11, a12], [a21, a22]])

    a1 = crt([a11, a21], [p, q])
    a2 = crt([a12, a22], [p, q])
    b = a1 * inverse_mod(a2, n) % n

    PK = PublicKey(n, b)
    SK = SecretKey(p, q, A)

    return (PK, SK)

def encrypt(m, pk):
    assert 0 < m < 2^400
    r = randint(0, 2^400-1)
    c = (pk.b*m + r) % pk.n
    return c

def decrypt(c, sk):
    a2 = crt([sk.A[0,1], sk.A[1,1]], [sk.p, sk.q])
    s1 = a2 * c % sk.p
    s2 = a2 * c % sk.q
    m, r = sk.A.solve_right(vector([s1, s2]))
    return m

def test(pk, sk, num=3):
    for _ in range(num):
        m = randint(0, 2^400-1)
        c = encrypt(m, pk)
        mm = decrypt(c, sk)
        assert m == mm


if __name__ == '__main__':
    from hashlib import sha256
    from secret import m, FLAG

    assert FLAG == 'd3ctf{%s}' % sha256(int(m).to_bytes(50, 'big')).hexdigest()

    PK, SK = gen_key()
    test(PK, SK)

    c = encrypt(m, PK)

    print(f"PK = {PK}")
    print(f"c = {c}")


"""
PK = PublicKey(n=69804507328197961654128697510310109608046244030437362639637009184945533884294737870524186521509776189989451383438084507903660182212556466321058025788319193059894825570785105388123718921480698851551024108844782091117408753782599961943040695892323702361910107399806150571836786642746371968124465646209366215361, b=65473938578022920848984901484624361251869406821863616908777213906525858437236185832214198627510663632409869363143982594947164139220013904654196960829350642413348771918422220404777505345053202159200378935309593802916875681436442734667249049535670986673774487031873808527230023029662915806344014429627710399196)
c = 64666354938466194052720591810783769030566504653409465121173331362654665231573809234913985758725048071311571549777481776826624728742086174609897160897118750243192791021577348181130302572185911750797457793921069473730039225991755755340927506766395262125949939309337338656431876690470938261261164556850871338570
"""
