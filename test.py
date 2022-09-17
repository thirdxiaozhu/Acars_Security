from concurrent.futures import process
from ctypes import *
from ctypes import Structure
import multiprocessing
from time import time

import Util
dll_test = CDLL("/home/jiaxv/inoproject/Acars_Sim_C/build/libacarstrans.so")
#dll_test.initUplinkMessage.restype = c_char_p
#dll_test.test.restype = c_wchar

class message_format(Structure):
    _fields_ = [("isUp", c_int),
                ("mode", c_char),
                ("arn", POINTER(c_ubyte)),
                ("ack", c_char),
                ("label", POINTER(c_ubyte)),
                ("udbi", c_char),
                ("serial", POINTER(c_ubyte)),
                ("flight", POINTER(c_ubyte)),
                ("text", POINTER(c_ubyte)),
                ("text_len", c_int),
                ("lsb_with_crc_msg", POINTER(c_ubyte)),
                ("total_length", c_int),
                ("complex_length", c_int),
                ("cpfsk", POINTER(c_float)),
                ("complex_i8", POINTER(c_ubyte))]
    def __init__(self):
        self.complex_i8 = cast(create_string_buffer(96000*12*2), POINTER(c_ubyte))  #需要首先分配内存

#dll_test.test.restype = POINTER(message_format)
#dll_test.test.restype = POINTER(uplink_message)

class Test(multiprocessing.Process):
    def __init__(self, s_conn):
        super().__init__()
        self.son_conn = s_conn

    def run(self):

        mode = "2".encode()
        label = "23".encode()
        ARN = "SP-LDE"
        ARN = ("%7s" % ARN).replace(" ", ".").encode()
        UBI = "A".encode()
        ACK = "A".encode()
        text = "Hello_World".encode()
        #text = "aaaa".encode()


        upm = message_format()

        upm.isUp = c_int(0)
        upm.mode = c_char(mode)
        ARN = bytearray(ARN)
        upm.arn = (c_ubyte*len(ARN)).from_buffer_copy(ARN)
        label = bytearray(label)
        upm.label = (c_ubyte*len(label)).from_buffer_copy(label)
        upm.ack = c_char(ACK)
        upm.udbi = c_char(UBI)
        text = bytearray(text)
        upm.text = (c_ubyte*len(text)).from_buffer_copy(text)
        upm.text_len = len(text)
        #print(string_at(upm.text, len(text)))

        u = pointer(upm)

        dll_test.mergeElements(u)
        dll_test.modulate(u)
        #aaa = string_at(upm.complex_i8, upm.complex_length * 2)
        #lsb = string_at(upm.lsb_with_crc_msg, upm.total_length)
        cpfsk = string_at(upm.cpfsk, upm.total_length)

        self.son_conn.send(cpfsk)


if __name__ == "__main__":
    p_conn, s_conn = multiprocessing.Pipe()
    tt = Test(s_conn)
    tt.start()
    p_conn.recv()


