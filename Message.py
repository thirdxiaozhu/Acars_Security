from ctypes import *

import multiprocessing


UPLINK = 0
DOWNLINK = 1

def kkk():
    import test
    p_conn, s_conn = multiprocessing.Pipe()
    tt = test.Test(s_conn)
    tt.start()
    _IQdata = p_conn.recv()


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
                ("total_len", c_int),
                ("complex_length", c_int),
                ("cpfsk", POINTER(c_ubyte)),
                ("complex_i8", POINTER(c_ubyte))]

    def __init__(self):
        self.complex_i8 = cast(create_string_buffer(96000*12*2), POINTER(c_ubyte))  #需要首先分配内存

class Message:
    NORMAL = 0
    CUSTOM = 1

    def __init__(self, message_tuple) -> None:
        self._timestamp = message_tuple[0]
        self._up_down = message_tuple[1]
        self._sec_level = message_tuple[2]
        self._mode = message_tuple[3]
        self._label = message_tuple[4]
        self._ARN = ("%7s" % message_tuple[5]).replace(" ", ".")
        self._UDBI = message_tuple[6]
        self._ACK = message_tuple[7]
        self._serial = message_tuple[8]
        self._flight = message_tuple[9]
        self._text = message_tuple[10]
        self._IQdata = None

    def setTimeStamp(self, timestamp):
        self._timestamp = timestamp

    def setMode(self, mode):
        self._mode = mode.encode()

    def setLabel(self, label):
        self._label = label.encode()

    def setArn(self, arn):
        self._ARN = ("%7s" % arn).replace(" ", ".").encode()

    def setUDbi(self, udbi):
        self._UDBI = udbi.encode()

    def setAck(self, ack):
        self._ACK = ack.encode()

    def setSerial(self, serial):
        self._serial = serial.encode()

    def setFlight(self, flight):
        self._flight = flight.encode()

    def setText(self, text):
        self._text = text.encode()

    def setSecurityLevel(self, lev):
        self._sec_level = lev

    def getSecurityLevel(self):
        return self._sec_level

    def getMsgTuple(self):
        return (self._timestamp, self._up_down, self._sec_level, self._mode, self._label, self._ARN, self._UDBI, self._ACK, self._serial, self._flight, self._text)

    def String(self):
        return self._text

    def setIQdata(self, iq):
        self._IQdata = iq

    def getIQdata(self):
        return self._IQdata


    def generateIQ(self):
        #handle = dll_test._handle
        dll_test = CDLL("/home/jiaxv/inoproject/Acars_Sim_C/build/libacarstrans.so")
        mf = message_format()

        mf.isUp = c_int(self._up_down)
        mf.mode = c_char(self._mode.encode())
        mf.arn = (c_ubyte*len(self._ARN)).from_buffer_copy(bytearray(self._ARN.encode()))
        mf.label = (c_ubyte*len(self._label)).from_buffer_copy(bytearray(self._label.encode()))
        mf.ack = c_char(self._ACK.encode())
        mf.udbi = c_char(self._UDBI.encode())
        mf.text = (c_ubyte*len(self._text)).from_buffer_copy(bytearray(self._text.encode()))
        mf.text_len = len(self._text)
        if self._up_down == DOWNLINK:
            mf.serial = (c_ubyte*len(self._serial)).from_buffer_copy(bytearray(self._serial.encode()))
            mf.flight = (c_ubyte*len(self._flight)).from_buffer_copy(bytearray(self._flight.encode()))
            mf.text_len = len(self._text) + len(self._serial) + len(self._flight)
            print("------", string_at(mf.serial, len(self._serial)))
            print("------", string_at(mf.flight, len(self._flight)))

        dll_test.mergeElements.argtypes = [c_void_p]
        dll_test.modulate.argtypes = [c_void_p]
        dll_test.mergeElements(byref(mf))
        dll_test.modulate(byref(mf))

        self._IQdata =  string_at(mf.complex_i8, mf.complex_length * 2)
        #print(self._IQdata[0:1000])

        #lsb = string_at(mf.lsb_with_crc_msg, mf.total_len)
        #print(lsb)
        #po = pointer(mf)
        #dll_test.mergeElements(po)
        #dll_test.modulate(po)

        ##try:
        ##    stdlib = CDLL("")
        ##except OSError:
        ##    # Alpine Linux.
        ##    stdlib = CDLL("libc.so")
        ##dll_close = stdlib.dlclose

        ##dll_close.argtypes = (c_void_p,)
        ##dll_close.restype = c_int
        ##dll_close(handle)
        #del dll_test

        #kkk()

        #import test
        #self.p_conn, self.s_conn = multiprocessing.Pipe()
        #tt = test.Test(self.s_conn)
        #tt.start()
        #self._IQdata = self.p_conn.recv()



        #print(self._IQdata[:200])