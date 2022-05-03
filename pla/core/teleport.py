import struct

def teleport_to_spawn(reader, coords):
    """Teleports user to point"""
    print("teleporting")
    cordarray = []
    playerloc = "[[[[[[main+42D4720]+18]+48]+1F0]+18]+370]+90"
    for i in coords:
        cordarray.append(coords[i])

    print(f"Teleporting to {cordarray}")
    position_bytes = struct.pack('fff', *cordarray)
    reader.write_pointer(playerloc,f"{int.from_bytes(position_bytes,'big'):024X}")