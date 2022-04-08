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