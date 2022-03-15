def create_distortion(reader):
    reader.write_main_int(0x24672A4, 0x5280010A, 4)
    reader.write_main_int(0x24672A4, 0x7100052A, 4)
