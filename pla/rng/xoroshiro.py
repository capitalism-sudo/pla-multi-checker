"""Xoroshiro Random Number Generator"""
class XOROSHIRO:
    """Xoroshiro Random Number Generator"""
    ulongmask = 2 ** 64 - 1
    uintmask = 2 ** 32 - 1

    def __init__(self, seed0, seed1 = 0x82A2B175229D6A5B):
        self.seed = [seed0, seed1]

    def reseed(self, seed0, seed1 = 0x82A2B175229D6A5B):
        """Reseed rng without creating a new object"""
        self.seed = [seed0, seed1]

    @property
    def state(self):
        """Return the full state of the rng as read from memory"""
        seed0, seed1 = self.seed
        return seed0 | (seed1 << 64)

    @staticmethod
    def rotl(number, k):
        """Rotate number left by k"""
        return ((number << k) | (number >> (64 - k))) & XOROSHIRO.ulongmask

    def next(self):
        """Generate the next random number and advance the rng"""
        seed0, seed1 = self.seed
        result = (seed0 + seed1) & XOROSHIRO.ulongmask
        seed1 ^= seed0
        self.seed = [XOROSHIRO.rotl(seed0, 24) ^ seed1 ^ ((seed1 << 16) & XOROSHIRO.ulongmask),
                     XOROSHIRO.rotl(seed1, 37)]
        return result

    def previous(self):
        """Generate the previous random number and advance the rng backwards"""
        seed0, seed1 = self.seed
        seed1 = XOROSHIRO.rotl(seed1, 27)
        seed0 = (seed0 ^ seed1 ^ (seed1 << 16)) & XOROSHIRO.ulongmask
        seed0 = XOROSHIRO.rotl(seed0, 40)
        seed1 ^= seed0
        self.seed = [seed0,seed1]
        return (seed0 + seed1) & XOROSHIRO.ulongmask

    def nextuint(self):
        """Generate the next random number as a uint"""
        return self.next() & XOROSHIRO.uintmask

    @staticmethod
    def get_mask(maximum):
        """Get the bit mask for rand(maximum)"""
        maximum -= 1
        for i in range(6):
            maximum |= maximum >> (1 << i)
        return maximum

    def rand(self, maximum = uintmask):
        """Generate a random number in the range of [0,maximum)"""
        mask = XOROSHIRO.get_mask(maximum)
        res = self.next() & mask
        while res >= maximum:
            res = self.next() & mask
        return res

    def quickrand1(self,mask): # 0~mask rand(mask + 1)
        return self.next() & mask

    def quickrand2(self,max,mask): # 0~max-1 rand(max)
        res = self.next() & mask
        while res >= max:
            res = self.next() & mask
        return res

    def rand_count(self, N = uintmask):
        mask = XOROSHIRO.get_mask(N)
        res = self.next() & mask
        count = 1
        while res >= N:
            res = self.next() & mask
            count += 1
        return res, count

    @staticmethod
    def find_seeds(ec,pid):
        solver = z3.Solver()
        start_s0 = z3.BitVecs('start_s0', 64)[0]

        sym_s0 = start_s0
        sym_s1 = 0x82A2B175229D6A5B

        # EC call
        result = ec
        sym_s0, sym_s1, condition = sym_xoroshiro128plus(sym_s0, sym_s1, result)
        solver.add(condition)

        # Blank call
        sym_s0, sym_s1 = sym_xoroshiro128plusadvance(sym_s0, sym_s1)

        # PID call
        result = pid
        sym_s0, sym_s1, condition = sym_xoroshiro128plus(sym_s0, sym_s1, result)
        solver.add(condition)
        
        models = get_models(solver)
        return [ model[start_s0].as_long() for model in models ]

    @staticmethod
    def find_seeds_arceus(ec,pid,rolls):
        solver = z3.Solver()
        start_s0 = z3.BitVecs('start_s0', 64)[0]

        sym_s0 = start_s0
        sym_s1 = 0x82A2B175229D6A5B

        # EC call
        result = ec
        sym_s0, sym_s1, condition = sym_xoroshiro128plus(sym_s0, sym_s1, result)
        solver.add(condition)

        # SIDTID call
        sym_s0, sym_s1 = sym_xoroshiro128plusadvance(sym_s0, sym_s1)

        # Initial PID rolls
        for _ in range(rolls-1):
            sym_s0, sym_s1, condition = sym_xoroshiro128plus(sym_s0, sym_s1, result)

        # PID call
        result = pid
        sym_s0, sym_s1, condition = sym_xoroshiro128plus(sym_s0, sym_s1, result)
        solver.add(condition)
        
        models = get_models(solver)
        return [ model[start_s0].as_long() for model in models ]

def sym_xoroshiro128plus(sym_s0, sym_s1, result):
    sym_r = (sym_s0 + sym_s1) & 0xFFFFFFFFFFFFFFFF  
    condition = (sym_r & 0xFFFFFFFF) == result

    sym_s0, sym_s1 = sym_xoroshiro128plusadvance(sym_s0, sym_s1)

    return sym_s0, sym_s1, condition

def sym_xoroshiro128plusadvance(sym_s0, sym_s1):
    s0 = sym_s0
    s1 = sym_s1
    
    s1 ^= s0
    sym_s0 = z3.RotateLeft(s0, 24) ^ s1 ^ (s1 << 16)
    sym_s1 = z3.RotateLeft(s1, 37)

    return sym_s0, sym_s1

def get_models(s):
    result = []
    while s.check() == z3.sat:
        m = s.model()
        result.append(m)
        
        # Constraint that makes current answer invalid
        d = m[0]
        c = d()
        s.add(c != m[d])

    return result

class XOROSHIRO_BDSP:

    ulongmask = 2 ** 64 - 1
    uintmask = 2 ** 32 - 1

    @staticmethod
    def splitmix(seed, state):
        seed += state
        seed = 0xBF58476D1CE4E5B9 * (seed ^ (seed >> 30))
        seed = 0x94D049BB133111EB * (seed ^ (seed >> 27))

        return seed ^ (seed >> 31)

    """
    def __init__(self,seed):

        s0 = XOROSHIRO_BDSP.splitmix(seed, 0x9E3779B97F4A7C15)
        s1 = XOROSHIRO_BDSP.splitmix(seed, 0x3C6EF372FE94F82A)

        self.seed = [s0, s1]
    """

    
    def __init__(self, seed):

        
        s0 = (seed - 0x61C8864680B583EB) & XOROSHIRO_BDSP.ulongmask
        s1 = (seed + 0x3C6EF372FE94F82A) & XOROSHIRO_BDSP.ulongmask

        s0 = ((s0 ^ (s0 >> 30)) * 0xBF58476D1CE4E5B9) & XOROSHIRO_BDSP.ulongmask
        s1 = ((s1 ^ (s1 >> 30)) * 0xBF58476D1CE4E5B9) & XOROSHIRO_BDSP.ulongmask

        s0 = ((s0 ^ (s0 >> 27)) * 0x94D049BB133111EB) & XOROSHIRO_BDSP.ulongmask
        s1 = ((s1 ^ (s1 >> 27)) * 0x94D049BB133111EB) & XOROSHIRO_BDSP.ulongmask
        

        s0 = s0 ^ (s0 >> 31)
        s1 = s1 ^ (s1 >> 31)
        
        self.seed = [s0, s1]
    

    @staticmethod
    def rotl(number, k):
        """Rotate number left by k"""
        return ((number << k) | (number >> (64 - k))) & XOROSHIRO_BDSP.ulongmask

    def next_u64(self):
        seed0,seed1 = self.seed
        result = (seed0 + seed1) & XOROSHIRO_BDSP.ulongmask

        seed1 ^= seed0
        seed0 = (self.rotl(seed0,24) ^ seed1 ^ (seed1 << 16)) & XOROSHIRO_BDSP.ulongmask
        seed1 = self.rotl(seed1,37)

        self.seed = [seed0, seed1]

        return result

    def next(self):
        result = self.next_u64()
        return result >> 32

    @staticmethod
    def getMask(x):
        x -= 1
        for i in range(6):
            x |= x >> (1 << i)
        return x

    def rand(self, N = uintmask):
        return self.next() % N
    
    """
    def rand(self, N = uintmask):
        mask = XOROSHIRO_BDSP.getMask(N)
        res = self.next() & mask
        while res >= N:
            res = self.next() & mask
        return res
    """