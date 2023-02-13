from ctypes import *

import multiprocessing
from select import select


MODE_DSP = 220
MODE_CMU = 210

SIGN_IS_VALID = 1
SIGN_IS_NOT_VALID = -1
MSG_WITH_NO_SIGN = 0


class message_format(Structure):
    _fields_ = [
                ("isUp", c_int),
                ("mode", c_ubyte),
                ("arn", POINTER(c_ubyte)),
                ("ack", c_ubyte),
                ("label", POINTER(c_ubyte)),
                ("udbi", c_ubyte),
                ("serial", POINTER(c_ubyte)),
                ("flight", POINTER(c_ubyte)),
                ("text", POINTER(c_ubyte)),
                ("crc", POINTER(c_ubyte)),
                ("suffix", c_ubyte),
                ("text_len", c_int),
                ("lsb_with_crc_msg", POINTER(c_ubyte)),
                ("total_len", c_int),
                ("complex_length", c_int),
                ("cpfsk", POINTER(c_ubyte)),
                ("complex_i8", POINTER(c_ubyte))]

    def __init__(self):
        self.complex_i8 = cast(create_string_buffer(96000*12*2), POINTER(c_ubyte))  #需要首先分配内存
        self.crc = cast(create_string_buffer(2), POINTER(c_ubyte))

class Message:
    NORMAL = 0
    CUSTOM = 1

    ETX = "\x03"
    ETB = "\x17"

    def __init__(self, message_tuple) -> None:
        print(message_tuple)
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
        self._crc = message_tuple[11] if message_tuple[11] is not None else "\x00\x00"
        self._suffix = message_tuple[12]
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

    def getText(self):
        return self._text

    def setSecurityLevel(self, lev):
        self._sec_level = lev

    def getSecurityLevel(self):
        return self._sec_level

    def getMsgTuple(self):
        return (self._timestamp, self._up_down, self._sec_level, self._mode, self._label, self._ARN, self._UDBI, self._ACK, self._serial, self._flight, self._text, self._crc, self._suffix)

    def String(self):
        return self._text

    def setIQdata(self, iq):
        self._IQdata = iq

    def getIQdata(self):
        return self._IQdata
    
    def getCRC(self):
        return self._crc

    def getCRC_ASCII(self):
        return self._crc.decode("latin1")


    def generateIQ(self):
        dll_test = CDLL("bin/libacarstrans.so")
        mf = message_format()

        mf.isUp = c_int(0 if self._up_down == MODE_DSP else 1)
        mf.mode = c_ubyte(ord(self._mode.encode("latin1")))
        mf.arn = (c_ubyte*len(self._ARN)).from_buffer_copy(bytearray(self._ARN.encode()))
        mf.label = (c_ubyte*len(self._label)).from_buffer_copy(bytearray(self._label.encode()))
        mf.ack = c_ubyte(ord(self._ACK.encode("latin1")))
        mf.udbi = c_ubyte(ord(self._UDBI.encode("latin1")))
        mf.text = (c_ubyte*len(self._text)).from_buffer_copy(bytearray((self._text + "\n").encode()))
        mf.crc = (c_ubyte* 2 ).from_buffer_copy(bytearray((self._crc).encode("latin1")))
        mf.suffix = c_ubyte(ord(self._suffix.encode("latin1")))
        mf.text_len = c_int(len(self._text))
        if self._up_down == MODE_CMU:
            mf.serial = (c_ubyte*len(self._serial)).from_buffer_copy(bytearray(self._serial.encode()))
            mf.flight = (c_ubyte*len(self._flight)).from_buffer_copy(bytearray(self._flight.encode()))

        dll_test.mergeElements.argtypes = [c_void_p]
        dll_test.modulate.argtypes = [c_void_p]
        dll_test.mergeElements(byref(mf))
        dll_test.modulate(byref(mf))

        self._IQdata = string_at(mf.complex_i8, mf.complex_length * 2)
        self._crc = string_at(mf.crc, 2)


class ReceivedMessage(Message):
    def __init__(self, message_tuple) -> None:
        super().__init__(message_tuple)
        self._origin_text = message_tuple[11]
        self._sign_text = message_tuple[12]
        self._sign_valid = message_tuple[13]
        self._cipher_text = message_tuple[14]

    def getOriginText(self):
        return self._origin_text

    def getCipherText(self):
        return self._cipher_text

    def getSignText(self):
        return self._sign_text

    def getSignValid(self):
        return self._sign_valid

    def getCipherLen(self):
        return len(self._cipher_text)

    def getSignLen(self):
        return len(self._sign_text)

    def getMsgTuple(self):
        tuple = super().getMsgTuple()
        tuple = (tuple + (self._cipher_text, self._sign_text))

        return tuple