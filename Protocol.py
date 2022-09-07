from re import S

from sympy import re
import Util


class Protocol:
    HEAD_LEN = 4
    SOH_LEN = 1
    MODE_LEN = 1
    ARN_LEN = 7
    TAK_LEN = 1
    LABEL_LEN = 2
    DUBI_LEN = 1
    STX_LEN = 1
    SUFFIX_LEN = 1
    BCS_LEN = 2
    BCSSUF_LEN = 1

    head = [0x2b, 0x2a, 0x16, 0x16]
    soh = 0x01
    stx = 0x02
    suffix = 0x03
    bcssuf = 0x7f
    #crc = [chr(0xFB), chr(0xD3)]

    def __init__(self, mode, arn, label, id, dubi, tak):
        self.protocol = []
        self.mode = mode
        self.arn = arn
        self.label = label
        self.id = id
        self.dubi = dubi
        self.tak = tak
        self.fore = self.getFore()
        self.crcStream = []


    def getLength(self):
        return self.SOH_LEN + self.MODE_LEN + self.ARN_LEN + self.TAK_LEN + self.LABEL_LEN + self.DUBI_LEN + \
               self.STX_LEN + self.SUFFIX_LEN + self.BCS_LEN + self.BCSSUF_LEN

    def getArn(self):
        #return ("%7s" % self.arn).replace(" ", ".")
        return self.arn

    def getTak(self):
        return ord(self.tak) if self.tak != "" else 0x15

    def getMode(self):
        return ord(self.mode)

    def getDubi(self):
        return ord(self.dubi)

    def getFore(self):
        fore = []
        fore.extend(self.head)
        fore.append(self.soh)
        fore.append(self.getMode())
        fore.extend(Util.byteString2Ascii(self.getArn()))
        fore.append(self.getTak())
        fore.extend(Util.byteString2Ascii(self.label))
        fore.append(self.getDubi())
        fore.append(self.stx)
        return fore


    def getTail(self):
        tail = []
        tail.extend(self.processTextToLSB([self.suffix]))
        print(self.crcStream[5:])
        tail.extend(Util.getCRC16(self.crcStream[5:]))  #14同步byte + SOH
        tail.extend(self.processTextToLSB([self.bcssuf]))

        return tail


    def processTextToLSB(self, text):
        ret = []

        for i in range(len(text)):
            temp = ("%7s" % bin(text[i]).replace('0b', '')).replace(" ", "0")
            oddSum = 0
            for r in temp:
                oddSum = oddSum + 1 if r == "1" else oddSum 

            oddParity = oddSum % 2

            temp = "1" + temp if oddParity == 0 else "0" + temp

            ret.append(chr(int(temp[::-1],2)))
            self.crcStream.append(int(hex(int(temp,2)),16))

        return ret
        

    def getContentData(self, text):
        message = []
        message.extend(self.processTextToLSB(self.fore))
        message.extend(self.processTextToLSB(text))
        message.extend(self.getTail())
        return message

