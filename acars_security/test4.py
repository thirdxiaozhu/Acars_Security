from ctypes import *
import Message
dll_test = CDLL("bin/libacarstrans.so")
class Hackrf_devs(Structure):
    _fields_ = [
        ("is_repeat", c_bool),
        ("serial_number", POINTER(c_ubyte)),
        ("path", POINTER(c_ubyte)),
        ("vga_p", c_int),
        ("freq_p", c_int64),
        ("data", POINTER(c_ubyte))]


serial = "1c3"


#msg = Message.Message((None, 210, 1, "2", "QQ", "B-919A",
#                               "2", "\x15", "CA1234", "HFLASHKJAFHKFHAAOIFHAFA", "M01A", None, Message.Message.ETX))

msg = Message.Message((None, 220, 1, "2", "QQ", "B-919A",
                               "A", "\x15", None, "GREQ*20NJSCXP*EJRD5M@W%FXGD7GVNYKK7A3PTUTR64256GII#V8B6VBF24XV4TCREMI@ZV#2EK9L6#Y6TMY5YY7EPNUIX#3AMJ@YLWD0NTMU0R", None, None, Message.Message.ETX))
msg.generateIQ()
iq = msg._IQdata
hd = Hackrf_devs()
hd.is_repeat = c_bool(False)
hd.serial_number = (c_ubyte*len(serial)).from_buffer_copy(bytearray(serial.encode("latin1")))
hd.vga_p = c_int(20)
hd.freq_p = c_int64(131450000)
hd.data = (c_ubyte * (len(iq))).from_buffer_copy(bytearray(iq))

dll_test.Transmit.argtypes = [c_void_p]
a = dll_test.Transmit(byref(hd))
print(a)



