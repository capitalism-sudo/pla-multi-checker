import struct

def teleport_to_spawn(reader, coords):
    """Teleports user to point"""
    playerloc = "[[[[[[main+42D4720]+18]+48]+1F0]+18]+370]+90"
    
    if len(coords) != 3:
        print(f"Error teleporting: expected 3 coordinates, but instead got {len(coords)}: {coords}")
        return "error", f"Expected 3 coordinates, but instead got {len(coords)}: {coords}"

    cordarray = [coords[0], coords[1], coords[2]]

    print(f"Teleporting to {cordarray}")
    position_bytes = struct.pack('fff', *cordarray)
    reader.write_pointer(playerloc,f"{int.from_bytes(position_bytes,'big'):024X}")
    return "success", f"Player teleported to {cordarray}"