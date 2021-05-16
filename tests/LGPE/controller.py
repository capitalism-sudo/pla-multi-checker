import json
import signal
import sys

# Go to root of PyNXReader
sys.path.append('../../')

from inputs import get_gamepad
from nxreader import LGPEReader

config = json.load(open("../../config.json"))
b = LGPEReader(config["IP"])

def signal_handler(signal, frame): #CTRL+C handler
    b.close()

signal.signal(signal.SIGINT, signal_handler)

while True:
    events = get_gamepad()
    for event in events:
        if event.ev_type != "Sync" and event.ev_type != "ABS_X" and event.ev_type != "ABS_Y":
            key = ""
            typ = ""
            if event.code == "BTN_EAST":
                key = "A"
                typ = "BTN"
            elif event.code == "BTN_SOUTH":
                key = "B"
                typ = "BTN"
            elif event.code == "BTN_WEST":
                key = "Y"
                typ = "BTN"
            elif event.code == "BTN_NORTH":
                key = "X"
                typ = "BTN"
            elif event.code == "BTN_MODE":
                key = "HOME"
                typ = "BTN"
            elif event.code == "BTN_TR" or event.code == "BTN_TL":
                key = "R"
                typ = "BTN"
            elif event.code == "BTN_SELECT" or event.code == "BTN_START":
                key = "PLUS"
                typ = "BTN"
            elif event.code == "ABS_HAT0X" or event.code == "ABS_HAT0Y":
                typ = "STICK"
                x = y = None
                if event.code == "ABS_HAT0X":
                    x = event.state * 0x7FFF
                else:
                    y = event.state * -0x7FFF
                b.moveRightStick(x,y)
            elif event.code == "ABS_X" or event.code == "ABS_Y":
                typ = "STICK"
                x = y = None
                if event.code == "ABS_X":
                    if event.state > 0x7000:
                        x = 0x7FFF
                    elif event.state < -0x7000:
                        x = -0x7FFF
                    else:
                        x = 0
                    
                else:
                    if event.state > 0x7000:
                        y = -0x7FFF
                    elif event.state < -0x7000:
                        y = 0x7FFF
                    else:
                        y = 0
                b.moveRightStick(x,y)
            if key != "":
                if typ == "DPAD":
                    if event.state == 1 or event.state == -1:
                        b.press(key)
                    else:
                        if key == "DUP" or key == "DDOWN":
                            b.release("DUP")
                            b.release("DDOWN")
                        else:
                            b.release("DLEFT")
                            b.release("DRIGHT")
                elif typ != "STICK":
                    if event.state == 1:
                        b.press(key)
                    else:
                        b.release(key)
                        b.release(key)