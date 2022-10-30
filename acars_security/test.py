from ctypes import *
import multiprocessing
from time import sleep
import Util
dll_test = CDLL("/home/jiaxv/inoproject/Acars_Security/bin/libacarsrec.so")



class RecvEvent(multiprocessing.Process):
    def __init__(self):
        super().__init__()

    def run(self):
        addr = "127.0.0.1:5555"
        ppm = "-8"
        index = "0"
        freq = "131.45"
        v = c_int(1)
        mode= c_int(210)
        ppm_i = (c_ubyte*len(ppm)).from_buffer_copy(bytearray(ppm.encode()))
        Rawaddr = (c_ubyte*len(addr)).from_buffer_copy(bytearray(addr.encode()))
        index_ = (c_ubyte*len(index)).from_buffer_copy(bytearray(index.encode()))
        freq_ = (c_ubyte*len(freq)).from_buffer_copy(bytearray(freq.encode()))
        dll_test.startRecv(v, mode, Rawaddr, ppm_i, index_, freq_)

re = RecvEvent()

def startWorking():
    re.start()


if __name__ == "__main__":
    WorkThread = Util.KThread(target=startWorking)
    WorkThread.start()
    print("!!!!!!!!!")

    sleep(5)
    re.terminate()
    WorkThread.kill()
    
    