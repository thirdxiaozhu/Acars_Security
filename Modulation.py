from ctypes import util
from scipy import signal
import numpy as np
import Util

f_s = 20
class Modulation:
    def __init__(self) -> None:
        pass

    @staticmethod
    def MSK(diff):
        diff = np.asarray(diff)
        length = len(diff)

        ip = 2*diff-2
        fm = ip/4
        fmR = np.repeat(fm, f_s)

        ts = np.arange(0,1,1/f_s)
        tsR = np.tile(ts,length)

        filter = Util.filter([0,1],[1,-1],ip)
        filter = np.array(filter, dtype=float)
        theta = np.pi/2.0*filter
        thetaR = np.repeat(theta, f_s)

        cpfsk =np.cos(2*np.pi*(1+fmR)*tsR + thetaR)


        return cpfsk


    @staticmethod
    def AM(cpfsk):
        Ac = 64
        f_s2 = 2

        cpfskR = np.repeat(cpfsk, f_s2)
        print(len(cpfskR))
        t = np.arange(0, ((len(cpfskR)-1)/f_s2) + 1/f_s2, 1/f_s2)
        print(len(t))
        ct = Ac * np.cos(2.0*np.pi*t)
        AM = ct*(1+cpfskR)

        cf_AM = Ac * AM - Ac
        zeros = np.zeros((f_s * f_s2 * 2400)-len(cf_AM))
        cf_AM = np.append(cf_AM, zeros)
        b, a = signal.butter(2, 0.0075)

        cf_AM = np.array(Util.filter(b,a,cf_AM), dtype=complex)
        cf_AM = signal.resample_poly(cf_AM, 12 , 1)

        I = cf_AM.real.astype('int8')
        Q = cf_AM.imag.astype('int8')

        return [I,Q]