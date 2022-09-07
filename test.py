from ctypes import *
from ctypes import Structure
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
                ("msg", POINTER(c_ubyte)),
                ("lsb_with_crc_msg", POINTER(c_ubyte)),
                ("total_len", c_int),
                ("complex_length", c_int),
                ("complex_i8", POINTER(c_ubyte))]

#dll_test.test.restype = POINTER(message_format)
#dll_test.test.restype = POINTER(uplink_message)

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
#print(string_at(upm.msg, 100))
#print(string_at(upm.lsb_with_crc_msg, upm.total_len))
dll_test.modulate(u)
#print(upm.total_len)

#s = [50, 174, 211, 208, 173, 76, 196, 69, 193, 50, 179, 193, 2, 79, 206, 206, 176, 49, 76, 79, 176, 50, 196, 205, 47, 42, 42, 50, 185, 50, 176, 52, 49, 69, 76, 76, 88, 69, 208, 87, 193, 50, 176, 52, 49, 176, 176, 50, 56, 131]
#print(s)
#print(Util.getCRC16(s))
#c = dll_test.test(u)
#print(c)
#dll_test.test2(c)
