import base64

from gmssl.sm4 import CryptSM4, SM4_ENCRYPT, SM4_DECRYPT
from gmssl import sm2, func, sm3

import Crypto
import Util


class Message:
    PREVIEW = 1
    SEND = 2

    def __init__(self, text):
        self.text = text
        self.key = b'1234567890123456'
        self.keys = Crypto.Keys()

    def encrypt(self):
        value = []
        for i in range(len(self.text)):
            value.append(Util.to6Bit(self.text[i]))

        
        crypt = CryptSM4()
        crypt.set_key(self.key, SM4_ENCRYPT)
        return crypt.crypt_ecb(bytes(Util.loadCode(value)))
        #return self.text

    def decrypt(self):
        crypt = CryptSM4()
        crypt.set_key(self.key, SM4_DECRYPT)
        return crypt.crypt_ecb(self.text)

    def sign(self, encrypt_res):
        sm2_crypt = sm2.CryptSM2(public_key=self.keys.getPubKey(), private_key=self.keys.getPriKey())
        sign = sm2_crypt.sign_with_sm3(encrypt_res)
        return Util.hex2byte(sign)

    def verify(self):
        sm2_crypt = sm2.CryptSM2(public_key=self.keys.getPubKey(), private_key=self.keys.getPriKey())
        verify = sm2_crypt.verify_with_sm3(self.sign_res, self.encry_res)
        return verify

    def getEncryptMessage(self, mod):
        encrypt_res = self.encrypt()
        sign_res = self.sign(encrypt_res)

        value = []

        value.append(len(encrypt_res))
        value.append(len(sign_res))

        value.extend(encrypt_res)
        value.extend(sign_res)


        if mod == self.PREVIEW:
            string = Util.deLoadCode(value)
            return string

        elif mod == self.SEND:
            string = Util.deLoadCode(value)
            #return string
            return Util.byteString2Ascii(self.text)


    def getDescryptMessage(self):
        encrypt_res = self.decrypt()
        return Util.deLoadCode(encrypt_res)