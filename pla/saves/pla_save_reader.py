from pla.rng import Xorshift32

STATIC_XORPAD = [
            0xA0, 0x92, 0xD1, 0x06, 0x07, 0xDB, 0x32, 0xA1, 0xAE, 0x01, 0xF5, 0xC5, 0x1E, 0x84, 0x4F, 0xE3,
            0x53, 0xCA, 0x37, 0xF4, 0xA7, 0xB0, 0x4D, 0xA0, 0x18, 0xB7, 0xC2, 0x97, 0xDA, 0x5F, 0x53, 0x2B,
            0x75, 0xFA, 0x48, 0x16, 0xF8, 0xD4, 0x8A, 0x6F, 0x61, 0x05, 0xF4, 0xE2, 0xFD, 0x04, 0xB5, 0xA3,
            0x0F, 0xFC, 0x44, 0x92, 0xCB, 0x32, 0xE6, 0x1B, 0xB9, 0xB1, 0x2E, 0x01, 0xB0, 0x56, 0x53, 0x36,
            0xD2, 0xD1, 0x50, 0x3D, 0xDE, 0x5B, 0x2E, 0x0E, 0x52, 0xFD, 0xDF, 0x2F, 0x7B, 0xCA, 0x63, 0x50,
            0xA4, 0x67, 0x5D, 0x23, 0x17, 0xC0, 0x52, 0xE1, 0xA6, 0x30, 0x7C, 0x2B, 0xB6, 0x70, 0x36, 0x5B,
            0x2A, 0x27, 0x69, 0x33, 0xF5, 0x63, 0x7B, 0x36, 0x3F, 0x26, 0x9B, 0xA3, 0xED, 0x7A, 0x53, 0x00,
            0xA4, 0x48, 0xB3, 0x50, 0x9E, 0x14, 0xA0, 0x52, 0xDE, 0x7E, 0x10, 0x2B, 0x1B, 0x77, 0x6E
        ]

HASH_SIZE = 0x20

BLOCKTYPE_SIZE = {
    3: 1, # Bool3
    8: 1, # Byte
    9: 2, #UInt16
    10: 4, #UInt32
    11: 8, #UInt64
    12: 1, #SByte
    13: 2, #Int16
    14: 4, #Int32
    15: 8, #Int64
    16: 4, #Single
    17: 8, #Double
}

SAVE_KEYS = {
    'pokedex': 0x02168706,
    'key_items': 0x59A4D0C3
}

MAX_SPECIES = 981
VALID_FILESIZES = [0x136dde, 0x13ad06]
POKEDEX_BLOCK_SIZE = 0x1e460

def read_research(data):
    # check the data is the right size
    if len(data) not in VALID_FILESIZES:
        return {'error': "The file you chose isn't the right size for a PLA save file"}

    # decrypt the bytes
    crypt_static_xorpad_bytes(data)

    offset = 0

    shinycharm = False
    research_entries = []

    # find the right blocks
    while offset < len(data) - HASH_SIZE:
        key, offset, blockdata = read_block(data, offset)

        if key == SAVE_KEYS['pokedex']:
            research_entries, error = read_pokedex(blockdata)
            if research_entries is None:
                return error

        elif key == SAVE_KEYS['key_items']:
            shinycharm, error = has_shinycharm(blockdata)
            if shinycharm is None:
                return error
            break
    
    return { 'shinycharm': shinycharm, 'research_entries': research_entries }

def crypt_static_xorpad_bytes(data):
    """Decrypts the save data in place using the static xorpad"""
    for i in range(len(data) - HASH_SIZE):
        data[i] ^= STATIC_XORPAD[i % len(STATIC_XORPAD)]

def read_block(data, offset):
    # Read the save block key
    key = int.from_bytes(data[offset:offset + 4], byteorder='little')

    # Use it to initialise the xorshift for decryption
    rng = Xorshift32(key)
    
    blocktype = data[offset+4] ^ rng.next()
    offset += 5

    if key in SAVE_KEYS.values():
        # we're only interested in reading two blocks here, both of which are objects (type 4)
        num_bytes = int.from_bytes(data[offset:offset + 4], byteorder='little') ^ rng.next32()
        blockdata = data[offset + 4:offset + 4 + num_bytes]
        
        for i in range(num_bytes):
            blockdata[i] ^= rng.next()
        
        return key, offset + 4 + num_bytes, blockdata
    
    # For every other block, we just want the block length

    if blocktype <= 3:
        # A block that represents a boolean value (specified by the type)
        # (or some kind of error block with an invalid code)
        return key, offset, None
    
    if blocktype == 4:
        # An object
        num_bytes = int.from_bytes(data[offset:offset + 4], byteorder='little') ^ rng.next32()
        return  key, offset + 4 + num_bytes, None
    
    if blocktype == 5:
        # An array of bytes
        num_entries = int.from_bytes(data[offset:offset + 4], byteorder='little') ^ rng.next32()
        array_type = data[offset + 4] ^ rng.next()
        return key, offset + 5 + num_entries * BLOCKTYPE_SIZE[array_type], None
    
    if blocktype >= 8 and blocktype <= 17:
        # A single data value
        return key, offset + BLOCKTYPE_SIZE[blocktype], None
    
    # If this point is reached, there's been an error, but we can try and continue
    return key, offset, None

def read_pokedex(blockdata):
    if len(blockdata) != POKEDEX_BLOCK_SIZE:
        return None, {'error': 'There was a problem checking your pokedex research levels'}

    return [read_research_entry(blockdata, 0x70 + (0x58 * i)) for i in range(MAX_SPECIES)], None

def read_research_entry(data, offset):
    flags = int.from_bytes(data[offset:offset+4], byteorder='little')
    research_rate = int.from_bytes(data[offset+0x08:offset+0x08+2], byteorder='little')
    return {
        'complete': research_rate >= 100,
        'perfect': flags & (1 << 2) != 0
    }
        
def has_shinycharm(blockdata):
    """Returns if the file has a shiny charm and any error"""
    if len(blockdata) < 400:
        return None, { 'error': 'There was a problem checking if you have the shiny charm'}

    for i in range(0, 400, 4):
        index = int.from_bytes(blockdata[i:i+2], byteorder='little')
        
        if index == 632:
            count = int.from_bytes(blockdata[i+2:i+4], byteorder='little')
            if count > 0:
                return True, None
    return False, None

def rolls_from_research(research, natdex_number):
    if research[natdex_number]['perfect']:
        return 3
    elif research[natdex_number]['complete']:
        return 1
    else:
        return 0

