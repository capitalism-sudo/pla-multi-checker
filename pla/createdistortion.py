from app import APP_MODE, AppMode
from time import sleep

def create_distortion(reader):
    reader.write_main_int(0x024A0428, 0x5280010A, 4)
    
    # If this is being run locally, pause execution to improve distortion spawning
    if APP_MODE != AppMode.WEB:
        sleep(0.6)

    reader.write_main_int(0x024A0428, 0x7100052A, 4)
