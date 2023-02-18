from pickle import BINSTRING
import time
import Util



def payloadEncode(text):
    bins = []
    for i in text:
        ch_int = ord(i)
        if ch_int == 124:
            bin = "111111"
        else:
            bin = Util.intToBin(ord(i)-32)
            bin = bin[2:]
        bins.append(bin)

    bins_str = "".join(bins)

    pad_len =  len(bins_str) % 8
    if pad_len != 0:
        bins_str += "".join(["0" for i in range(8-pad_len)])


    charas = []
    for i in Util.cut_list(bins_str, 8):
        charas.append(chr(int(i, 2)))

    return "".join(charas).encode("latin1")

def payloadDecode(todecode):
    bins = []
    for i in todecode.decode("latin1"):
        bins.append("{:08b}".format(ord(i)).replace("0b", ""))

    bins_str = "".join(bins)

    bin_list = Util.cut_list(bins_str, 6)

    while len(bin_list[-1]) < 6 or bin_list[-1] == "000000":
        bin_list = bin_list[:-1]

    ret = []
    for i in bin_list:
        if i == "111111":
            ret.append(chr(124))
        else:
            ret.append(chr(int(i, 2) + 32))

    return "".join(ret)

def messageEncode(text):
    bins = []
    for i in text:
        bin = Util.intToBin(i)
        bins.append(bin)

    bins_str = "".join(bins)
    processed_len = 0

    encoded = []

    while len(bins_str) != processed_len:
        temp = bins_str[processed_len: processed_len+8]
        if len(temp) < 6:
            #if not temp.__contains__("1"):
            #    break
            toappend = "".join(["0" for i in range(6-len(temp))])
            bins_str += toappend
            temp += toappend
        ascii = int(temp, 2)

        if len(temp) == 8:
            if ascii ==124 or ascii < 96 or ascii >= 127:
                temp = temp[:-2]
                ascii = Util.getMessageTableElement(int(temp[2:], 2), int(temp[0:2], 2))
                processed_len += 6
            else:
                processed_len += 8
        else:
            ascii = Util.getMessageTableElement(int(temp[2:], 2), int(temp[0:2], 2))
            processed_len += 6

        encoded.append(chr(ascii))


    return "".join(encoded)

def messageDecode(text):
    #encoded = text.encode()
    bins = []
    for i in text:
        bin = Util.intToBin(ord(i))
        bins.append(bin)

    decoded = []
    for chara in bins:
        ascii = int(chara,2)
        if ascii == 124 or ascii < 96 or ascii >= 127 :
            if ascii == 124:
                decoded.append("111111")
            else:
                msg_dec_bin = Util.intToBin(ascii-32)
                decoded.append(msg_dec_bin[2:])
        else:
            decoded.append(chara)

    bins_str = "".join(decoded)
    bin_list = Util.cut_list(bins_str, 8)
    #if bin_list[-1].__contains__("1"):
    if len(bin_list[-1]) >= 6:
        bin_list[-1] = bin_list[-1] + "".join(["0" for j in range(8-len(bin_list[-1]))])
    else:
        bin_list = bin_list[:-1]

    bins_str = bins_str[:len(bins_str) - len(bins_str) % 8]
    
    charas = []
    for i in bin_list:
        charas.append(chr(int(i, 2)))
    return "".join(charas).encode("latin1")


def encode_test(text):
    ts = payloadEncode(text)
    print(ts, len(ts))
    re = payloadDecode(ts)
    print(re, len(re))


if __name__ == "__main__":
    pass
    #encode_test()
    #_8bits = "\x03"
    #_8bits = "\x7c"
    #_8bits = '30%O%G2R*G2#X9M@NAG1BF8Y7LA2J3J%S7A0AKFNJ8BKT4#3PP3NAEEI%XGQAZVJE1MWHA#1KONQ2PPWW2T@MGYCT0BUVNZT*EXIW5ZA6YPJDVHE%J3X10180@V8L#DOE@M7IVDOQE*OZSEO4%5GNH11*H2F20T%PL05V#*VP5C7UK3V#U4VV3TZMU4VV3TZMU4VV3TZMU4VV3TZMAC'
    #_8bits = "||||||||"
    ss = b'0\x82\x01\xcf0\x82\x01r\xa0\x03\x02\x01\x02\x02\x14\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x000\x0c\x06\x08*\x81\x1c\xcfU\x01\x83u\x05\x000e1\x0b0\t\x06\x03U\x04\x06\x13\x02CN1\x0f0\r\x06\x03U\x04\x07\x13\x06DongLi1\x100\x0e\x06\x03U\x04\x08\x13\x07TianJin1\r0\x0b\x06\x03U\x04\n\x13\x04CAUC1\x0f0\r\x06\x03U\x04\x0b\x13\x06AnQuan1\x130\x11\x06\x03U\x04\x03\x13\nDspDefault0\x1e\x17\r230216213059Z\x17\r240216133059Z0e1\x0b0\t\x06\x03U\x04\x06\x13\x02CN1\x0f0\r\x06\x03U\x04\x07\x13\x06DongLi1\x100\x0e\x06\x03U\x04\x08\x13\x07TianJin1\r0\x0b\x06\x03U\x04\n\x13\x04CAUC1\x0f0\r\x06\x03U\x04\x0b\x13\x06AnQuan1\x130\x11\x06\x03U\x04\x03\x13\nDspDefault0Y0\x13\x06\x07*\x86H\xce=\x02\x01\x06\x08*\x81\x1c\xcfU\x01\x82-\x03B\x00\x04\xbaT2x\x0bC\xf3&\xb7[U7\x03\xd2H\t\x0fDBE\xf2\x0f\xb8\xe2\xa6\xae\x0c\x1a\xd6t\xdfg\xee\xbc^;\xc3\xa7_H\xb5\xfe\xad(\xb1R\x07\xba\xceD<\xd5OP\xd3\xf8\xde\x9cT\xae[\xcf\xa7\x0e0\x0c\x06\x08*\x81\x1c\xcfU\x01\x83u\x05\x00\x03I\x000F\x02!\x00\xb5\xc8`\xb1x\x1c\x9b\xaaA }B\xa6\xd1\x81\xc83aq\xb0\xb9\xc4s\x0b6W\xf5\xc2\x88\x02\x91\xea\x02!\x00\xfd\xa0\x1b\xc3.~\x1f\xdc\xaf\xf9W\xa8\x07@\x94UucH\xbdG\xfdA\x13\xb4\x0f\x997\xdc\x89x\xd3'
    #print(_8bits, end="\n\n")
    #ss = payloadEncode(_8bits)
    #print(ss, end="\n\n")
    aa = messageEncode(ss)
    print(aa, end="\n\n")
    tt = messageDecode(aa)
    print(tt, end="\n\n")
    #mm = payloadDecode(tt)
    #print(mm.encode("latin1"))