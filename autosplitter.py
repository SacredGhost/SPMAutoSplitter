import time
import configparser
from typing import Callable, Any
from watches import ByteArrayMemoryWatch, Datatype, get_address, get_watch
from keypresses import PressRelease, keyCodeMap

config = configparser.ConfigParser()
config.read('hotkeys.config')
key_code = config['SplitKey']['keyCode']

def do_split(delay):
    current_framecount = frame_count.read()
    while frame_count.read() < current_framecount + delay:
        time.sleep(1 / FPS)
    PressRelease(keyCodeMap[key_code], 100)
    frame_wait(ONESECOND_DELAY * 5)

def frame_wait(delay):
    current_framecount = frame_count.read()
    while frame_count.read() < current_framecount + delay:
        time.sleep(1 / FPS)


FPS = get_watch("fps").read()
SLEEP_TIME = 5 # Default: 5 seconds
STAR_BLOCK_SPLIT_DELAY = 240 # Default: 240 frames
PURE_HEART_SPLIT_DELAY = 727 # Default: 727 frames
ROCK_HEART_SPLIT_DELAY = 721 # Default: 721 frames
DOOR_CLOSE_SPLIT_DELAY = 0 # Default: 0 frames
CB_DOOR_CLOSE_SPLIT_DELAY = 84 # Default: 84 frames
RETURN_SPLIT_DELAY = 426 # Default: 426 frames
CB_DEFEAT_DELAY = 150 # Default: 150 frames
SD_DEFEAT_DELAY = 40 # Default: 40 frames
CREDITS_DELAY = 0 # DO NOT CHANGE
ONESECOND_DELAY = 60 # DO NOT CHANGE
SPLIT_MAPS = ("mac_02", "mac_12", "ls4_10")

EVT_ENTRY_SIZE = 0x1a8
EVT_ENTRY_SCRIPT_PTR_OFFSET = 0x198

STAR_BLOCK_EVT_SCRIPT = get_address("star_block_evt_script")
PURE_HEART_EVT_SCRIPT = get_address("pure_heart_evt_script")
DOOR_CLOSE_EVT_SCRIPT = get_address("door_close_evt_script")
RETURN_EVT_SCRIPT = get_address("return_evt_script")
CB_DEFEAT_EVT_SCRIPT = get_address("CB_defeat_evt_script")
SD_DEFEAT_EVT_SCRIPT = get_address("SD_defeat_evt_script")
CREDITS_START_SCRIPT = get_address("credits_start_evt_script")

evt_entry_count = get_watch("evt_entry_count").read()
evt_entries = ByteArrayMemoryWatch(get_watch("evt_entries_ptr").read(), evt_entry_count * EVT_ENTRY_SIZE)
frame_count = get_watch("frameCount")
sequence_position = get_watch("SequencePosition")
mariox = get_watch("Mario_X")
map = get_watch("CurrentMap")
effcurcount = get_watch("EffTypeStats_curCount")
textopacity1 = get_watch("text_opacity_1")
textopacity2 = get_watch("text_opacity_2")

text_box_count1 = 0
text_box_count2 = 0

current_map = map.read()
current_sequence = sequence_position.read()
current_effcurcount = effcurcount.read()
current_text_opacity_1 = textopacity1.read()
current_text_opacity_2 = textopacity2.read()

def findInStructArray(arr: ByteArrayMemoryWatch, struct_size: int, offset: int, to_find: list[int], to_find_datatype: Datatype, callback: Callable[[int], Any]):
    for i in range(arr.size // struct_size):
        val = arr.read(i * struct_size + offset, to_find_datatype)

        if val not in to_find:
            continue

        if callback is not None:
            callback(val)

def evt_entry_cb(script_ptr: int):
    global current_effcurcount
    global current_text_opacity_1
    global current_text_opacity_2
    global text_box_count1
    global text_box_count2

    if script_ptr == STAR_BLOCK_EVT_SCRIPT:
        print(f'{"[" + "Console" + "]":>15} Detected Star Block Hit')
        do_split(STAR_BLOCK_SPLIT_DELAY)

    if script_ptr == PURE_HEART_EVT_SCRIPT:
        print(f'{"[" + "Console" + "]":>15} Pure Heart Detected')
        if current_map == "wa1_27":
            do_split(ROCK_HEART_SPLIT_DELAY)
        else:
            do_split(PURE_HEART_SPLIT_DELAY)
    
    if script_ptr == RETURN_EVT_SCRIPT:
        print(f'{"[" + "Console" + "]":>15} Return Cutscene')
        do_split(RETURN_SPLIT_DELAY)

    if script_ptr == DOOR_CLOSE_EVT_SCRIPT and current_map in SPLIT_MAPS:
        mariopos = mariox.read()

        valid_door = True
        split_delay = DOOR_CLOSE_SPLIT_DELAY

        if current_sequence == 9 and (-490 <= mariopos <= -410):
            door_name = 'Chapter 1'
        elif current_sequence == 65 and (-340 <= mariopos <= -260):
            door_name = 'Chapter 2'
        elif current_sequence == 100 and (-190 <= mariopos <= -110):
            door_name = 'Chapter 3'
        elif current_sequence == 134 and (-40 <= mariopos <= 40):
            door_name = 'Chapter 4'
        elif current_sequence == 178 and (110 <= mariopos <= 190):
            door_name = 'Chapter 5'
        elif 222 <= current_sequence <= 224 and (260 <= mariopos <= 340):
            door_name = 'Chapter 6'
        elif current_sequence == 303 and (410 <= mariopos <= 490):
            door_name = 'Chapter 7'
        elif current_sequence in (356,357) and (-80 <= mariopos <= -80):
            door_name = 'Chapter 8'
        elif current_sequence == 409 and (1100 <= mariopos <= 1200):
            door_name = 'Bleck'
            split_delay = CB_DOOR_CLOSE_SPLIT_DELAY
        else:
            valid_door = False
        
        if (valid_door):
            print(f'{"[" + "Console" + "]":>15} Valid Door: Chapter {door_name} Door Detected')
            do_split(split_delay)

    if script_ptr == CB_DEFEAT_EVT_SCRIPT:
        print(f'{"[" + "Console" + "]":>15} Count Bleck Defeated')
        frame_wait(ONESECOND_DELAY *2)
        while current_effcurcount != 1:
            time.sleep(0.01)
            current_effcurcount = effcurcount.read()
        do_split(CB_DEFEAT_DELAY)

    if script_ptr == SD_DEFEAT_EVT_SCRIPT:
        print(f'{"[" + "Console" + "]":>15} Super Dimentio Defeated')
        do_split(SD_DEFEAT_DELAY)

    if script_ptr == CREDITS_START_SCRIPT:
        if current_map == "mac_22":
            print(f'{"[" + "Console" + "]":>15} Credits Detected')
            frame_wait(ONESECOND_DELAY *2)
            current_text_opacity_1 = textopacity1.read()
            current_text_opacity_2 = textopacity2.read()
            while current_text_opacity_1 != 255 and current_text_opacity_2 != 255:
                current_text_opacity_1 = textopacity1.read()
                current_text_opacity_2 = textopacity2.read()
            if current_text_opacity_1 == 255:
                current_text_opacity = current_text_opacity_1
                text_box_count = text_box_count1
                textopacity = textopacity1
            elif current_text_opacity_2 == 255:
                current_text_opacity = current_text_opacity_2
                text_box_count = text_box_count2
                textopacity = textopacity2  
            if current_text_opacity == 255:    
                text_box_count += 1
                while text_box_count <= 5:
                    if current_text_opacity == 255:
                        while current_text_opacity > 0:
                            current_text_opacity = textopacity.read()
                            pass
                    frame_wait(ONESECOND_DELAY *2)
                    current_text_opacity = textopacity.read()
                    text_box_count += 1
                while current_text_opacity != 0:
                    current_text_opacity = textopacity.read()
                do_split(CREDITS_DELAY)
                text_box_count = 0
                print(f'{"[" + "Console" + "]":>15} GG :)')

print(f'{"[" + "Console" + "]":>15} Auto Splitter Ready!')

found = False
while True:
    try:
        current_map = map.read()
        current_sequence = sequence_position.read()
        if current_map == "ls4_11":
            current_effcurcount = effcurcount.read()

        findInStructArray(evt_entries, EVT_ENTRY_SIZE, EVT_ENTRY_SCRIPT_PTR_OFFSET, [STAR_BLOCK_EVT_SCRIPT, PURE_HEART_EVT_SCRIPT, DOOR_CLOSE_EVT_SCRIPT, RETURN_EVT_SCRIPT, CB_DEFEAT_EVT_SCRIPT, SD_DEFEAT_EVT_SCRIPT, CREDITS_START_SCRIPT], Datatype.WORD, evt_entry_cb)
    except RuntimeError as e: # If dolphin is disconnected, should not error for any other reason
        print(e)
        time.sleep(1)
        continue