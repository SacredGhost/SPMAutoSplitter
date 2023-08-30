from enum import Enum
from typing import Any
import dolphin_memory_engine as dme
import time

class Datatype(Enum):
    BYTE = 1
    HALFWORD = 2
    WORD = 3
    FLOAT = 4
    DOUBLE = 5
    STRING = 6
    BYTEARRAY = 7
    BOOL = 8
    VOIDPTR = 9

class MemoryWatch:
    def __init__(self, address: int, datatype: Datatype) -> None:
        self.address = address
        self.datatype = datatype
    
    @staticmethod
    def read_halfword(address:int) -> int:
        return (dme.read_byte(address) << 8) + dme.read_byte(address+1)

    @staticmethod
    def read_string(address:int) -> int:
        s = ""
        i = 0
        cur_char = ""
        while (cur_char := chr(dme.read_byte(address+i))) != '\0':
            s += cur_char
            i += 1
        return s
    
    @staticmethod
    def read_bool(address:int) -> bool:
        return not not dme.read_byte(address)

    @staticmethod
    def write_halfword(address:int, value:int) -> None:
        value %= 65536
        dme.write_byte(address, value >> 8)
        dme.write_byte(address+1, value & 0xff)

    @staticmethod
    def write_string(address:int, value:str) -> None:
        for i,e in enumerate(value):
            dme.write_byte(address+i, ord(e))
        dme.write_byte(address+len(value), 0) # add the null terminator at the end
    
    @staticmethod
    def write_bool(address:int, value:bool) -> None:
        dme.write_byte(address, int(value))
    
    _accessor_methods = {
        Datatype.BYTE: (dme.read_byte, dme.write_byte),
        Datatype.HALFWORD: (read_halfword, write_halfword),
        Datatype.WORD: (dme.read_word, dme.write_word),
        Datatype.FLOAT: (dme.read_float, dme.write_float),
        Datatype.DOUBLE: (dme.read_double, dme.write_double),
        Datatype.STRING: (read_string, write_string),
        Datatype.BOOL: (read_bool, write_bool),
        Datatype.VOIDPTR: (dme.read_word, dme.write_word),
    }

    def get_accessors(self):
        return MemoryWatch._accessor_methods[self.datatype]

    def read(self):
        if self.datatype == Datatype.BYTEARRAY:
            return dme.read_bytes(self.address, self.len)
        return self.get_accessors()[0](self.address)
    
    def write(self, value):
        if isinstance(value, Enum):
            value = value.value
        self.get_accessors()[1](self.address, value)

class ByteArrayMemoryWatch(MemoryWatch):
    def __init__(self, address: int, size: int = 0) -> None:
        super().__init__(address, Datatype.BYTEARRAY)
        self.size = size
    
    def read_all(self) -> bytes:
        return dme.read_bytes(self.address, self.size)
    
    def write_all(self, value: bytes):
        self.size = len(value)
        dme.write_bytes(self.address, value)

    def read(self, index: int, datatype: Datatype, length:int=-1):
        assert(index < self.size)
        if datatype == Datatype.BYTEARRAY:
            return dme.read_bytes(self.address + index, length)
        return MemoryWatch._accessor_methods[datatype][0](self.address + index)

class BitFieldMemoryWatch(MemoryWatch):
    def __init__(self, address: int, datatype: Datatype, bitmask: int = 0):
        super().__init__(address, datatype)
        self.bitmask = bitmask
    
    def read(self) -> bool:
        return self.get_accessors()[0](self.address) & self.bitmask == self.bitmask
    
    def write(self, value:bool) -> None:
        accessors = self.get_accessors()
        res = accessors[0](self.address)
        if value:
            res |= self.bitmask
        else:
            res &= ~self.bitmask
        accessors[1](self.address, res)

dme.hook()

if not dme.is_hooked():
    print(f'{"[" + "Console" + "]":>15} Not Hooked, waiting for connection to Dolphin')
    while not dme.is_hooked():
        time.sleep(0.01)
        dme.hook()
    print(f'{"[" + "Console" + "]":>15} Hooked')
    time.sleep(5) # Added a wait as it cannot read the addresses when dophin is still booting the game
else:
    print(f'{"[" + "Console" + "]":>15} Hooked')
    time.sleep(5)

game_region = chr(dme.read_byte(0x80000003))
game_revision = dme.read_byte(0x80000007)

def get_address(name: str) -> int:
    return watches[name]["addresses"][game_region][game_revision]

def get_watch(name: str) -> MemoryWatch:
    watch = watches[name]
    address = watch["addresses"][game_region][game_revision]
    if watch["datatype"] == Datatype.BYTEARRAY:
        return ByteArrayMemoryWatch(address, watch["size"])
    return MemoryWatch(address, watch["datatype"])

watches = {
    "GSWF_base_address" : {
        "addresses": {
            "E": [0x804e2694, 0x804e3f14, 0x804e4094],
            "P": [0x80525694, 0x80525694],
            "J": [0x804b7994, 0x804b8f94],
            "K": [0x8055cff4]
        },
        "datatype": Datatype.WORD
    },
    "evt_entry_count" : {
        "addresses": {
            "E": [0x804c9990, 0x804cb210, 0x804cb390],
            "P": [0x8050c990, 0x8050c990],
            "J": [0x8049ec90, 0x804a0290],
            "K": [0x80543878]
        },
        "datatype": Datatype.WORD
    },
    "evt_entries_ptr" : {
        "addresses": {
            "E": [0x804c9a20, 0x804cb2a0, 0x804cb420],
            "P": [0x8050ca20, 0x8050ca20],
            "J": [0x8049ed20, 0x804a0320],
            "K": [0x80543908]
        },
        "datatype": Datatype.WORD
    },
    "star_block_evt_script" : {
        "addresses": {
            "E": [0x803dbc84, 0x803dcfe4, 0x803dd1c4],
            "P": [0x8041b62c, 0x8041b62c],
            "J": [0x803b0f04, 0x803b2084],
            "K": [0x8044bd6c]
        },
        "datatype": Datatype.VOIDPTR
    },
    "pure_heart_evt_script" : {
        "addresses": {
            "E": [0x803cf298, 0x803d05f8, 0x803d0798],
            "P": [0x8040ec00, 0x8040ec00],
            "J": [0x803ab2c8, 0x803a5698],
            "K": [0x8043f340]
        },
        "datatype": Datatype.VOIDPTR
    },
    "door_close_evt_script" : {
        "addresses": {
            "E": [0x803d6048, 0x803d73a8, 0x803d7588],
            "P": [0x804159f0, 0x804159f0],
            "J": [0x803a4518, 0x803ac448],
            "K": [0x80446130]
        },
        "datatype": Datatype.VOIDPTR
    },
    "return_evt_script" : {
        "addresses": {
            "E": [0x80daeb48, 0x80d9c0e8, 0x80d9c2c8],
            "P": [0x80ddf2e8, 0x80ddf2e8],
            "J": [0x80dc9a68, 0x80db6d88],
            "K": [0x80df9090]
        },
        "datatype": Datatype.VOIDPTR
    },
    "CB_defeat_evt_script" : {
        "addresses": {
            "E": [0x80e0785c, 0x80df4dfc, 0x80df4fec],
            "P": [0x80e381ac, 0x80e381ac],
            "J": [0x80e2277c, 0x80e0fa9c],
            "K": [0x80e52164]
        },
        "datatype": Datatype.VOIDPTR
    },
    "EffTypeStats_curCount" : {
        "addresses": {
            "E": [0x804c893c, 0x804ca1bc, 0x804ca33c],
            "P": [0x8050b93c, 0x8050b93c],
            "J": [0x8049dc3c, 0x8049f23c],
            "K": [0x80542724]
        },
        "datatype": Datatype.WORD          
    },
    "SD_defeat_evt_script" : {
        "addresses": {
            "E": [0x80e0ca34, 0x80df9fd4, 0x80dfa1c4],
            "P": [0x80e3d38c, 0x80e3d38c],
            "J": [0x80e27954, 0x80e14c74],
            "K": [0x80e57344]
        },
        "datatype": Datatype.VOIDPTR
    },
    "credits_start_evt_script" : {
        "addresses": {
            "E": [0x80cfb5bc, 0x80ce8b3c, 0x80ce8d1c],
            "P": [0x80d2ae6c, 0x80d2ae6c],
            "J": [0x80d164dc, 0x80d037dc],
            "K": [0x80d449e4]
        },
        "datatype": Datatype.VOIDPTR
    },
    "text_opacity_1" : {
        "addresses": {
            "E": [0x80781c86, 0x807714e6, 0x80771666],
            "P": [0x807b2f26, 0x807b2f26],
            "J": [0x807877a6, 0x80776d86],
            "K": [0x807c1b46]
        },
        "datatype": Datatype.HALFWORD
    },
    "text_opacity_2" : { # Probably don't need this, just a one off thing that it allocated PAL here.
        "addresses": {
            "E": [0x80781c86, 0x807714e6, 0x80771666],
            "P": [0x807e7f26, 0x807e7f26],
            "J": [0x807877a6, 0x80776d86],
            "K": [0x807c1b46]
        },
        "datatype": Datatype.HALFWORD
    },
    "fps" : {
        "addresses": {
            "E": [0x804e2554, 0x804E3DD4, 0x804E3F54],
            "P": [0x80525554, 0x80525554],
            "J": [0x804B7854, 0x804B8E54],
            "K": [0x8055CEB4]
        },
        "datatype": Datatype.WORD
    },
    "frameCount" : {
        "addresses": {
            "E": [0x804e2564, 0x804E3DE4, 0x804E3F64],
            "P": [0x80525564, 0x80525564],
            "J": [0x804B7864, 0x804B8E64],
            "K": [0x8055CEC4]
        },
        "datatype": Datatype.WORD
    },
    "SequencePosition" : {
        "addresses" : {
            "E": [0x804E2690, 0x804E3F10, 0x804E4090],
            "P": [0x80525690, 0x80525690],
            "J": [0x804B7990, 0x804B8F90],
            "K": [0x8055CFF0]
        },
        "datatype": Datatype.WORD
    },
    "Mario_X" : {
        "addresses" : {
            "E": [0x804CD4B4, 0x804CED34, 0x804CEEB4],
            "P": [0x805104B4, 0x805104B4],
            "J": [0x804A27B4, 0x804A3DB4],
            "K": [0x80547D9C]
        },
        "datatype": Datatype.FLOAT
    },
    "CurrentMap" : {
        "addresses" : {
            "E": [0x804E2594, 0x804E3E14, 0x804E3F94],
            "P": [0x80525594, 0x80525594],
            "J": [0x804B7894, 0x804B8E94],
            "K": [0x8055CEF4]
        },
        "datatype": Datatype.STRING
    }
}