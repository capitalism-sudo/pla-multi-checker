class Xorshift32:
    def __init__(self, seed: int) -> None:
        pop_count = bin(seed).count('1')
        for _ in range(pop_count):
            seed = Xorshift32.xorshift_advance(seed)
        
        self.seed = seed
        self.counter = 0

    def next(self) -> int:
        result = (self.seed >> (self.counter << 3)) & 0xFF

        if self.counter == 3:
            self.seed = Xorshift32.xorshift_advance(self.seed)
            self.counter = 0
        else:
            self.counter += 1

        return result

    def next32(self) -> int:
        return self.next() | (self.next() << 8) | (self.next() << 16) | (self.next() << 24)

    @staticmethod
    def xorshift_advance(key: int) -> int:
        key ^= (key << 2) & 0xFFFFFFFF
        key ^= key >> 15
        key ^= (key << 13) & 0xFFFFFFFF
        return key

class Xorshift:
    def __init__(self, state0, state1, state2, state3):
        self.seed = [state0,state1,state2,state3]
    
    @property
    def state(self):
        return (self.seed[3] << 96) | (self.seed[2] << 64) | (self.seed[1] << 32) | self.seed[0]

    def next(self):
        t = self.seed[0]
        s = self.seed[3]

        t ^= (t << 11) & 0xFFFFFFFF
        t ^= t >> 8
        t ^= s ^ (s >> 19)

        self.seed = self.seed[1:4] + [t]

        return t
    
    def previous(self):
        t = self.seed[2] >> 19 ^ self.seed[2] ^ self.seed[3]
        t ^= t >> 8
        t ^= t << 11 & 0xFFFFFFFF
        t ^= t << 22 & 0xFFFFFFFF
        self.seed = [t] + self.seed[0:3]
    
    def rand(self,max=0x7FFFFFFF,min=None):
        if min is None:
            min = 0
            if max == 0x7FFFFFFF:
                min = -0x7FFFFFFF - 1
        return (self.next() % (max-min)) + min
    
    def randrange_float(self,min,max):
        t = (self.rand() & 0x7fffff) / 8388607.0
        return t * min + (1.0 - t) * max

    def alt_next(self):
        return ((self.next() % 0xFFFFFFFF) - 0x80000000) & 0xFFFFFFFF
    
    def alt_rand(self, maximum):
        return self.alt_next() % maximum
    
    def advance(self,adv):
        for _ in range(adv):
            self.alt_next()

        return self
    
    def __str__(self):
        return f"S[0]: {self.seed[0]:08X}  S[1]: {self.seed[1]:08X}  S[2]: {self.seed[2]:08X}  S[3]: {self.seed[3]:08X}"

    def current(self):
        return [self.seed[0], self.seed[1], self.seed[2], self.seed[3]]