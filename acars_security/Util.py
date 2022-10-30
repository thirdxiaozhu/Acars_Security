import threading
import sys

TABEL_FOR_8BIT = [
    ["<NUL>", "<DLE>", " ", "0", "@", "P", "`", "p"],
    ["<SOH>", "<DC1>", "!", "1", "A", "Q", "a", "q"],
    ["<STX>", "<DC2>", "\"", "2", "B", "R", "b", "r"],
    ["<ETX>", "<DC3>", "#", "3", "C", "S", "c", "s"],
    ["<EOT>", "<DC4>", "$", "4", "D", "T", "d", "t"],
    ["<ENQ>", "<NAK>", "%", "5", "E", "U", "e", "u"],
    ["<ACK>", "<SYN>", "&", "6", "F", "V", "f", "v"],
    ["<BEL>", "<ETB>", "'", "7", "G", "W", "g", "w"],
    ["<BS>", "<CAN>", "(", "8", "H", "X", "h", "x"],
    ["<HT>", "<EM>", ")", "9", "I", "Y", "i", "y"],
    ["<LF>", "<SUB>", "*", ":", "J", "Z", "j", "z"],
    ["<VT>", "<ESC>", "+", ";", "K", "[", "k", "{"],
    ["<FF>", "<FS>", ",", "<", "L", "\\", "l", "|"],
    ["<CR>", "<GS>", "-", "=", "M", "]", "m", "}"],
    ["<SO>", "<RS>", ".", ">", "N", "^", "n", "~"],
    ["<SI>", "<US>", "/", "?", "O", "_", "o", "<DEL>"],
]

TABEL_FOR_6BIT = [
    [" ", "0", "@", "P"],
    ["!", "1", "A", "Q"],
    ["\"", "2", "B", "R"],
    ["#", "3", "C", "S"],
    ["$", "4", "D", "T"],
    ["%", "5", "E", "U"],
    ["&", "6", "F", "V"],
    ["'", "7", "G", "W"],
    ["(", "8", "H", "X"],
    [")", "9", "I", "Y"],
    ["*", ":", "J", "Z"],
    ["+", ";", "K", "["],
    [",", "<", "L", "\\"],
    ["-", "=", "M", "]"],
    [".", ">", "N", "^"],
    ["/", "?", "O", "|"],
]

PAYLOAD_TABEL = [
    [" ", "0", "@", "P"],
    ["!", "1", "A", "Q"],
    ["\"", "2", "B", "R"],
    ["#", "3", "C", "S"],
    ["$", "4", "D", "T"],
    ["%", "5", "E", "U"],
    ["&", "6", "F", "V"],
    ["'", "7", "G", "W"],
    ["(", "8", "H", "X"],
    [")", "9", "I", "Y"],
    ["*", ":", "J", "Z"],
    ["+", ";", "K", "["],
    [",", "<", "L", "\\"],
    ["-", "=", "M", "]"],
    [".", ">", "N", "^"],
    ["/", "?", "O", "|"],
]

MESSAGE_TABEL = [
    [" ", "0", "@", "P"],
    ["!", "1", "A", "Q"],
    ["\"", "2", "B", "R"],
    ["#", "3", "C", "S"],
    ["$", "4", "D", "T"],
    ["%", "5", "E", "U"],
    ["&", "6", "F", "V"],
    ["'", "7", "G", "W"],
    ["(", "8", "H", "X"],
    [")", "9", "I", "Y"],
    ["*", ":", "J", "Z"],
    ["+", ";", "K", "["],
    [",", "<", "L", "\\"],
    ["-", "=", "M", "]"],
    [".", ">", "N", "^"],
    ["/", "?", "O", "|"],
]

TABLE_FOR_CRC16_CCITT = [
        0x0000, 0x1189, 0x2312, 0x329b, 0x4624, 0x57ad, 0x6536, 0x74bf, 0x8c48, 0x9dc1, 0xaf5a,
        0xbed3, 0xca6c, 0xdbe5, 0xe97e, 0xf8f7, 0x1081, 0x0108, 0x3393, 0x221a, 0x56a5, 0x472c, 0x75b7, 0x643e,
        0x9cc9, 0x8d40, 0xbfdb, 0xae52, 0xdaed, 0xcb64, 0xf9ff, 0xe876, 0x2102, 0x308b, 0x0210, 0x1399, 0x6726,
        0x76af, 0x4434, 0x55bd, 0xad4a, 0xbcc3, 0x8e58, 0x9fd1, 0xeb6e, 0xfae7, 0xc87c, 0xd9f5, 0x3183, 0x200a,
        0x1291, 0x0318, 0x77a7, 0x662e, 0x54b5, 0x453c, 0xbdcb, 0xac42, 0x9ed9, 0x8f50, 0xfbef, 0xea66, 0xd8fd,
        0xc974, 0x4204, 0x538d, 0x6116, 0x709f, 0x0420, 0x15a9, 0x2732, 0x36bb, 0xce4c, 0xdfc5, 0xed5e, 0xfcd7,
        0x8868, 0x99e1, 0xab7a, 0xbaf3, 0x5285, 0x430c, 0x7197, 0x601e, 0x14a1, 0x0528, 0x37b3, 0x263a, 0xdecd,
        0xcf44, 0xfddf, 0xec56, 0x98e9, 0x8960, 0xbbfb, 0xaa72, 0x6306, 0x728f, 0x4014, 0x519d, 0x2522, 0x34ab,
        0x0630, 0x17b9, 0xef4e, 0xfec7, 0xcc5c, 0xddd5, 0xa96a, 0xb8e3, 0x8a78, 0x9bf1, 0x7387, 0x620e, 0x5095,
        0x411c, 0x35a3, 0x242a, 0x16b1, 0x0738, 0xffcf, 0xee46, 0xdcdd, 0xcd54, 0xb9eb, 0xa862, 0x9af9, 0x8b70,
        0x8408, 0x9581, 0xa71a, 0xb693, 0xc22c, 0xd3a5, 0xe13e, 0xf0b7, 0x0840, 0x19c9, 0x2b52, 0x3adb, 0x4e64,
        0x5fed, 0x6d76, 0x7cff, 0x9489, 0x8500, 0xb79b, 0xa612, 0xd2ad, 0xc324, 0xf1bf, 0xe036, 0x18c1, 0x0948,
        0x3bd3, 0x2a5a, 0x5ee5, 0x4f6c, 0x7df7, 0x6c7e, 0xa50a, 0xb483, 0x8618, 0x9791, 0xe32e, 0xf2a7, 0xc03c,
        0xd1b5, 0x2942, 0x38cb, 0x0a50, 0x1bd9, 0x6f66, 0x7eef, 0x4c74, 0x5dfd, 0xb58b, 0xa402, 0x9699, 0x8710,
        0xf3af, 0xe226, 0xd0bd, 0xc134, 0x39c3, 0x284a, 0x1ad1, 0x0b58, 0x7fe7, 0x6e6e, 0x5cf5, 0x4d7c, 0xc60c,
        0xd785, 0xe51e, 0xf497, 0x8028, 0x91a1, 0xa33a, 0xb2b3, 0x4a44, 0x5bcd, 0x6956, 0x78df, 0x0c60, 0x1de9,
        0x2f72, 0x3efb, 0xd68d, 0xc704, 0xf59f, 0xe416, 0x90a9, 0x8120, 0xb3bb, 0xa232, 0x5ac5, 0x4b4c, 0x79d7,
        0x685e, 0x1ce1, 0x0d68, 0x3ff3, 0x2e7a, 0xe70e, 0xf687, 0xc41c, 0xd595, 0xa12a, 0xb0a3, 0x8238, 0x93b1,
        0x6b46, 0x7acf, 0x4854, 0x59dd, 0x2d62, 0x3ceb, 0x0e70, 0x1ff9, 0xf78f, 0xe606, 0xd49d, 0xc514, 0xb1ab,
        0xa022, 0x92b9, 0x8330, 0x7bc7, 0x6a4e, 0x58d5, 0x495c, 0x3de3, 0x2c6a, 0x1ef1, 0x0f78
]



base = [str(x) for x in range(10)] + [chr(x) for x in range(ord('A'), ord('A') + 6)]


# hex2dec
# 十六进制 to 十进制
def hex2dec(string_num):
    return str(int(string_num.upper(), 16))


# dec2bin
# 十进制 to 二进制: bin()
def dec2bin(string_num):
    num = int(string_num)
    mid = []
    while True:
        if num == 0: break
        num, rem = divmod(num, 2)
        mid.append(base[rem])

    return ''.join([str(x) for x in mid[::-1]])


# hex2tobin
# 十六进制 to 二进制: bin(int(str,16))
def hex2bin(string_num):
    if string_num == '0':
        return '0'
    return dec2bin(hex2dec(string_num.upper()))


def indexto8bit(row, col):
    #return TABEL_FOR_8BIT[row][col]
    return int(col << 4) + int(row)


def indexTo6bit(row, col):
    return TABEL_FOR_6BIT[row][col]

def intTo6bit(index):
    return index - 32


def hex2byte(source):
    value = []
    for i in range(len(source)):
        if i % 2 == 0:
            if i != len(source):
                value.append(((int(hex2bin(source[i])) << 4) & 0xF0) + int(hex2bin(source[i + 1]), 2))
            else:
                value.append((int(hex2bin(source[i])) << 4) & 0xFF)


    return value


def getCRC16(message):
    ret = []
    crc_reg = 0x0000
    for i in message:
        crc_reg = TABLE_FOR_CRC16_CCITT[(crc_reg ^ i) & 0xFF] ^ (crc_reg >> 8)
    print(crc_reg)
    
    crc_string = "{:016b}".format(crc_reg).replace("0b","")[::-1]

    print(crc_string)
    print(int(crc_string[:8],2))
    print(int(crc_string[8:],2))
    ret.append(chr(int(crc_string[:8],2)))
    ret.append(chr(int(crc_string[8:],2)))

    return ret


def loadCode(origin):
    print(type(origin))
    length = len(origin)
    res = []
    for i in range(length):
        temp = i % 4
        if temp == 0:
            if i != length - 1:
                res.append(((origin[i] & 0x3f) << 2) + ((origin[i + 1] & 0x30) >> 4))
            else:
                res.append((origin[i] & 0x3f) << 2)
        elif temp == 1:
            if i != length - 1:
                res.append(((origin[i] & 0x0f) << 4) + ((origin[i + 1] & 0x3c) >> 2))
            else:
                res.append((origin[i] & 0x0f) << 4)
        elif temp == 2:
            if i != length - 1:
                res.append(((origin[i] & 0x03) << 6) + (origin[i + 1] & 0x3f))
            else:
                res.append((origin[i] & 0x03) << 6)

    return res


def deLoadCode(origin):
    length = len(origin)
    res = []
    for i in range(length):
        temp = i % 3
        if temp == 0:
            res.append((origin[i] >> 2) & 0x3f)
        elif temp == 1:
            res.append(((origin[i - 1] << 4) & 0x30) + ((origin[i] >> 4) & 0x0f))
        elif temp == 2:
            res.append(((origin[i - 1] << 2) & 0x3c) + ((origin[i] >> 6) & 0x03))
            if (origin[i] & 0x3f) != 0:
                res.append((origin[i]) & 0x3f)

    return res


def to6Bit(c):
    c = ord(c)
    if 97 <= c <= 102:
        c -= 32
    return ((c >> 4) - 2) * 16 + (c & 0x0f)


def byteString2Ascii(s):
    ret = []
    for i in s:
        ret.append(ord(i))
    return ret


def XNOR(pre, cur):
    pre = int(pre,2)
    cur = int(cur,2)
    #res = 0 if pre != cur else 1

    #print(pre, cur, res)

    return 0 if pre != cur else 1

def filter(b,a,x):
        y = []
        y.append(b[0] * x[0])
        for i in range(1,len(x)):
            y.append(0)
            for j in range(len(b)):
                if i >= j :
                    y[i] = y[i] + b[j] * x[i - j ]
                    #j += 1
            for l in range(len(b)-1 ):
                if i >l:
                    y[i] = (y[i] - a[l+1] * y[i -l-1])
                    #l += 1
            #i += 1
        return y

#def int8_to_unsigned_hex(integer):
#    if integer < 0:
#        integer = 128-integer
#    return chr(integer).encode('latin1')

def intToBin(number):
    if(number>=0):
        b=bin(number)
        b = '0' * (8+2 - len(b)) + b
    else:
        b=2**(8)+number
        b=bin(b)
        b = '1' * (8+2 - len(b)) + b    #注意这里算出来的结果是补码
    b=b.replace("0b",'')
    b=b.replace('-','')

    return b

def int8_to_unsigned_hex(integer):
    return chr(integer).encode('latin1')


class KThread(threading.Thread):
    def __init__(self, *args, **keywords):
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False

    def start(self):
        self.__run_backup = self.run
        self.run = self.__run
        threading.Thread.start(self)

    def __run(self):
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, why, arg):
        if why == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, why, arg):
        if self.killed:
            if why == 'line':
                raise SystemExit()
        return self.localtrace

    def kill(self):
        self.killed = True


def cut_list(lists, cut_len):
    """
    将列表拆分为指定长度的多个列表
    :param lists: 初始列表
    :param cut_len: 每个列表的长度
    :return: 一个二维数组 [[x,x],[x,x]]
    """
    res_data = []
    if len(lists) > cut_len:
        for i in range(int(len(lists) / cut_len)):
            cut_a = lists[cut_len * i:cut_len * (i + 1)]
            res_data.append(cut_a)

        last_data = lists[int(len(lists) / cut_len) * cut_len:]
        if last_data:
            res_data.append(last_data)
    else:
        res_data.append(lists)

    return res_data

def getMessageTableElement(row, col):
    #print(row, col, MESSAGE_TABEL[row][col])
    return ord(MESSAGE_TABEL[row][col])