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


if __name__ == "__main__":
    pass
    #encode_test()
    #_8bits = "\x03"
    #_8bits = "\x7c"
    #_8bits = '30%O%G2R*G2#X9M@NAG1BF8Y7LA2J3J%S7A0AKFNJ8BKT4#3PP3NAEEI%XGQAZVJE1MWHA#1KONQ2PPWW2T@MGYCT0BUVNZT*EXIW5ZA6YPJDVHE%J3X10180@V8L#DOE@M7IVDOQE*OZSEO4%5GNH11*H2F20T%PL05V#*VP5C7UK3V#U4VV3TZMU4VV3TZMU4VV3TZMU4VV3TZMAC'
    #_8bits = "||||||||"
    ss =  b'G0E\x02!\x00\xcd9\x13\xfbH\xb2\xcbb\xdf\xbb\xbbv\xd3\xbc\xcd\xdb\xbc\x1d\x81\x94\xde\xa9\xd9N\xa4A\x93dQ \xaa\x1f\x02 \x13\xc9\xed\x8a4%>\xd3\x00~\x04Hv\xa3\x97\xdc\xd5\xc8O\x13\x92\xc3P\x0bi\x10\x15^o\x96\xeb#\x9a\x05.\xd2x-/\x94$\xd8\xefB\x08~\xf0\xfc\x8f%i\xb0\xb7\xcdt;H\xce\n\xc3`\xb5\xde\xe7\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00' 
    #print(_8bits, end="\n\n")
    #ss = payloadEncode(_8bits)
    #print(ss, end="\n\n")
    aa = messageEncode(ss)
    print(aa, end="\n\n")
    tt = messageDecode(aa)
    print(tt, end="\n\n")
    #mm = payloadDecode(tt)
    #print(mm.encode("latin1"))