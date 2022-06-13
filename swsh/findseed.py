import numpy as np
from functools import reduce
from pla.rng import XOROSHIRO

def get_rotl(n,size=64):
    rotl = np.identity(64,dtype="uint8")
    return np.roll(rotl,-n,axis=0)

def get_shift(n,size=64):
    return np.eye(size,k=n,dtype="uint8")

def get_trans():
    tl = get_rotl(24)^np.identity(64,dtype="uint8")^get_shift(16)
    tr = np.identity(64,dtype="uint8")^get_shift(16)
    bl = get_rotl(37)
    br = get_rotl(37)

    trans = np.block([[tl,tr],[bl,br]])
    
    return trans

def get_mat():
    t = np.identity(128,dtype="uint8")
    t_ = get_trans()

    s = np.zeros((128,128),"uint8")
    for i in range(128):
        s[i] = (t[63]+t[127])%2
        t = t@t_%2
    return s


def list2bitvec(lst):
    bitvec = reduce(lambda p,q: (int(p)<<1)|int(q),lst)
    return bitvec

def gauss_jordan(mat,observed):
    r,c = mat.shape
    assert r==c
    #def square mat size
    n = r
    bitmat = [list2bitvec(mat[i]) for i in range(r)]

    res = [d for d in observed]
    #forward elimination
    pivot = 0
    for i in range(n):
        isfound = False
        for j in range(i,n):
            if isfound:
                check = 1<<(n-i-1)
                if bitmat[j]&check==check:
                    bitmat[j] ^= bitmat[pivot]
                    res[j] ^= res[pivot]
            else:
                check = 1<<(n-i-1)
                if bitmat[j]&check==check:
                    isfound = True
                    bitmat[j],bitmat[pivot] = bitmat[pivot],bitmat[j]
                    res[j],res[pivot] = res[pivot],res[j]
        if isfound:
            pivot += 1
    
    #backward assignment
    for i in range(1,n)[::-1]:
        check = 1<<(n-i-1)
        for j in range(i)[::-1]:
            if bitmat[j]&check==check:
                bitmat[j] ^= bitmat[i]
                res[j] ^= res[i]

    return res
    
def motions2state(motions, mat=get_mat()):
    state = list2bitvec(gauss_jordan(mat,motions))
    return state >> 64, state & 0xFFFFFFFFFFFFFFFF

def motions2seed(motions, mat=get_mat()):
    state = list2bitvec(gauss_jordan(mat,motions))
    return (state >> 64) | ((state & 0xFFFFFFFFFFFFFFFF) << 64)

def generate_sequence(s0, s1, min, max):

    rng = XOROSHIRO(int(s0,16), int(s1,16))

    for _ in range(min):
        rng.next()
    
    result = ''

    for _ in range(max):
        result += str(rng.next() & 0x1)

    #print(f"String: {result}")

    return result

def find_swsh_seed(motions):
    s0, s1 = motions2state(motions)

    print("Found Seeds")
    print(f"{s0:X}, {s1:X}")

    return {"s0": f"{s0:X}", "s1": f"{s1:X}"}

def update_swsh_seed(s0, s1, motions, min, max):

    AdvanceString = generate_sequence(s0, s1, min, max)
    result = []

    advancelength = len(AdvanceString)
    motionslength = len(motions)

    i = 0
    while (i < advancelength):
        print(f"I: {i}")
        index = AdvanceString.find(motions, i)
        if index == -1:
            break
        result.append(index)
        i = index + 1
    
    print(f"Possible Results: {len(result)}")
    if len(result) == 1:
        num = result[0] + len(motions) + min
        print(f"Advances: {num}, inputs {motionslength}")

        rng = XOROSHIRO(int(s0,16), int(s1,16))

        for i in range(num):
            rng.next()

        state0 = f"{rng.seed[0]:X}"
        state1 = f"{rng.seed[1]:X}"

        print(f"State found: S0 {state0}, S1 {state1}")
    else:
        num = 0
        state0 = "0"
        state1 = "0"

    return { "adv": num, "count": len(result), "s0": state0, "s1": state1}