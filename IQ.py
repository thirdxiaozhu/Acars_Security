from cmath import pi
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import ctypes

class IQ():

    def __init__(self, sample_rate, baud) -> None:
        self.sample_rate = sample_rate
        self.baud = baud
        self.repeat = int(sample_rate/baud)
        self.freq = baud/4
        self.count = int(sample_rate/baud)
        self.Tb = self.count/sample_rate
        self.fc = 3/(4 * self.Tb)
        self.pi = 3.1416

    def float2hex(self, s):
        fp = ctypes.pointer(ctypes.c_float(s))
        cp = ctypes.cast(fp,ctypes.POINTER(ctypes.c_long))
        return cp.contents.value

    def hex2float(self, h):
        i = int(h,16)
        cp = ctypes.pointer(ctypes.c_int(i))
        fp = ctypes.cast(cp,ctypes.POINTER(ctypes.c_float))
        return fp.contents.value

    def readFile(self, path, pattern):
        bins = []
        binFile = open(path, pattern)

        lines = binFile.readlines()
        for line in lines:
            bins.extend(line)

        binFile.close()
        return bins

    def generateIQ(self, path):
        array = np.array(self.readFile(path, "rb"), dtype=np.int8)
        #array = np.array([1,1,0,1,0,0,0,1,0,1,0,0,0,1,0,0,0,1,0,0,1,0,1,1,1,0,1,0,1], dtype=np.int8)
        #array = np.array([1,1,1,0,1,0,0,0], dtype=np.int8)
        N = len(array)
        n = N * self.count

        t = np.arange(0, (n)/self.sample_rate, 1/self.sample_rate, dtype=np.float32)
        accuracy = len(t) % self.repeat
        if accuracy != 0:
            t = t[0:0-accuracy]

        if N & (N-1) == 0:
            t = t[:-1]

        for i in range(len(array)):
            temp = array[i]
            array[i] = temp if temp == 1 else -1

        finek = []
        finek.append(0)

        for p in range(1,N):
            temp = finek[p-1]+(p)*pi/2*(array[p-1]-array[p])
            temp = temp % (2*pi)
            finek.append(temp)

        finek = np.around(finek, 4)

        pk = np.cos(finek)
        qk = array * pk


        pk = np.round(pk).astype(int)
        qk = np.round(qk).astype(int)


        PK = []
        QK = []
        for p in pk:
            for i in range(self.count):
                PK.append(p)

        for q in qk:
            for i in range(self.count):
                QK.append(q)


        MSK_P = (np.float32)(PK*np.cos(np.dot(pi*self.baud/2,t))*np.sin(np.dot(2*pi*self.fc, t)))
        MSK_Q = (np.float32)(QK*np.sin(np.dot(pi*self.baud/2,t))*np.cos(np.dot(2*pi*self.fc, t)))
        MSK = MSK_P + MSK_Q
        return signal.hilbert(MSK)


    def write_gnuradio_IQ_file(self, sourcePath, targetPath, mode):
        MSK_C_H = self.generateIQ(sourcePath) 
        MSK_C_H_i = MSK_C_H.real
        MSK_C_H_q = MSK_C_H.imag

        iqFile = open(targetPath,"wb")

        temp = []
        for i in range(len(MSK_C_H)):
            float_hex_i = self.float2hex(MSK_C_H_i[i] * 0.8)
            float_hex_q = self.float2hex(MSK_C_H_q[i] * 0.8)
            ind = 0
            while ind < 32:
                iqFile.write(chr(int((float_hex_i >> ind) & 0xff)).encode('latin1'))
                temp.append(int((float_hex_i >> ind) & 0xff))
                ind += 8

            if mode != "float":
                ind = 0
                while ind < 32:
                    iqFile.write(chr(int((float_hex_q >> ind) & 0xff)).encode('latin1'))
                    temp.append(int((float_hex_q >> ind) & 0xff))
                    ind += 8

        iqFile.close()


        #plt.figure(2)
        #plt.subplot(211)
        #plt.plot(MSK_C_H_i, label=u"Carrier")
        #plt.plot(MSK_C_H_q, label=u"aCarrier")

        #plt.subplot(212)
        #plt.plot(MSK_C_H, label=u"cCarrier")
        #plt.show()

        real_list = []
        imag_list = []
        print(len(temp))
        for i in range(0, len(temp), 4):
            subList = temp[i:i+4]
            for j in range(len(subList)):
                subList[j] = str('%#x' % subList[j])[2:]

            subList = subList[::-1]

            if mode != "float":
                if (i/4) % 2 == 0:
                    real_list.append(self.hex2float("".join(subList)))
                else:
                    imag_list.append(self.hex2float("".join(subList)))
            else:
                real_list.append(self.hex2float("".join(subList)))


        real_list = np.array(real_list, dtype=np.float32)
        imag_list = np.array(imag_list, dtype=np.float32)

        combined_fft = np.empty(len(real_list), dtype=np.complex64)
        combined_fft.real = real_list
        combined_fft.imag = imag_list



        plt.figure(2)
        plt.plot(real_list, label=u"Carrier")
        plt.plot(imag_list, label=u"Carrier")
        plt.plot(combined_fft, label=u"aCarrier")
        plt.show()


    def read_gnuradio_IQ_file(self, path, mode):

        float_bytes = self.readFile(path,"rb")


        real_list = []
        imag_list = []
        for i in range(0, len(float_bytes), 4):
            subList = float_bytes[i:i+4]
            for j in range(len(subList)):
                subList[j] = str('%#x' % subList[j])[2:]

            subList = subList[::-1]
            if (i/4) % 2 == 0:
                real_list.append(self.hex2float("".join(subList)))
            else:
                imag_list.append(self.hex2float("".join(subList)))

        real_list = np.array(real_list, dtype=np.float32)
        imag_list = np.array(imag_list, dtype=np.float32)

        combined_fft = np.empty(len(real_list), dtype=np.complex64)
        combined_fft.real = real_list
        combined_fft.imag = imag_list



        plt.figure(2)
        plt.plot(real_list, label=u"Carrier")
        plt.plot(imag_list, label=u"Carrier")
        #plt.plot(combined_fft, label=u"aCarrier")
        plt.show()

    def write_hackrf_IQ_file(self, sourcePath, targetPath):
        MSK_C_H = self.generateIQ(sourcePath) 
        MSK_C_H_i = MSK_C_H.real
        MSK_C_H_q = MSK_C_H.imag

        
        iqFile = open(targetPath,"wb")

        for i in range(len(MSK_C_H)):
            ####   补码  ###
            #i_complement = self.intToBin(int(MSK_C_H_i[i] * 0.8 * 127))
            #q_complement = self.intToBin(int(MSK_C_H_q[i] * 0.8 * 127))
            #iqFile.write(self.int8_to_unsigned_hex(int(i_complement, 2)))
            #iqFile.write(self.int8_to_unsigned_hex(int(q_complement, 2)))

            ####   首bit为符号  ###
            i = int(MSK_C_H_i[i] * 0.8 * 127)
            q = int(MSK_C_H_q[i] * 0.8 * 127)
            iqFile.write(self.int8_to_unsigned_hex(i))
            iqFile.write(self.int8_to_unsigned_hex(q))

        iqFile.close()

    def read_hackrf_IQ_file(self, path):
        int_bytes = self.readFile(path,"rb")

        real_list = []
        imag_list = []
        for i in range(len(int_bytes)):
            temp = "{:08b}".format(int_bytes[i]).replace("0b", "")

            ####  补码  ###
            integer = self.binToInt(temp)

            #### 首bit符号位 ###
            #integer = int(temp, 2)
            #if integer > 127:
            #    integer = 128 - integer

            if i % 2 == 0:
                real_list.append(integer)
            else:
                imag_list.append(integer)


        real_list = np.array(real_list, dtype=np.float32)
        imag_list = np.array(imag_list, dtype=np.float32)

        combined_fft = np.empty(len(real_list), dtype=np.complex64)
        combined_fft.real = real_list
        combined_fft.imag = imag_list



        plt.figure(2)
        plt.plot(real_list, label=u"Carrier")
        plt.plot(imag_list, label=u"Carrier")
        #plt.plot(combined_fft, label=u"aCarrier")
        plt.show()

    def int8_to_unsigned_hex(self, integer):
        #if integer < 0:
        #    integer = 128-integer
        return chr(integer).encode('latin1')

    #十进制转换为二进制
    def intToBin(self, number):
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

    #二进制转换为十进制
    def binToInt(self, number):
        i=int(str(number),2)
        if(i>=2**(8-1)):#如果是负数
            i=-(2**8-i)
            return i
        else:
            return i


if __name__ == "__main__":
    iq = IQ(2400000, 2400)
    #iq.write_gnuradio_IQ_file("/home/jiaxv/inoproject/msk/10001000.txt", "fffff.iq", mode="complex")
    #iq.read_gnuradio_IQ_file("../complex.bin", mode="complex")
    #iq.write_hackrf_IQ_file("/home/jiaxv/inoproject/msk/11111111.txt", "int8.iq")
    iq.read_hackrf_IQ_file("/home/jiaxv/inoproject/msk/acarsgen/poa_1M152.cs8")
    iq.read_hackrf_IQ_file("/home/jiaxv/inoproject/msk/acarsgen/int8.cs8")
    #print(iq.int8_to_unsigned_hex(255))


