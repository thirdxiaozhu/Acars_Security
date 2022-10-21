from ctypes import *
#import base64
import deflate
from Crypto import Security

import Process

dll_test = CDLL("/home/jiaxv/CLionProjects/acars_crypt/build/libacarscrypt.so")

DEFAULT_LENGTH = 512
KEY_LEN = 16
IV_LEN = 16

class Ce(Structure):
    _fields_ = [
                ("key_len", c_int),
                ("plain_len", c_int),
                ("cipher_len", c_int),
                ("key", POINTER(c_ubyte)),
                ("iv", POINTER(c_ubyte)),
                ("plain", POINTER(c_ubyte)),
                ("plain_2", POINTER(c_ubyte)),
                ("cipher", POINTER(c_ubyte))
                ]

    def __init__(self, key, iv, plain_text, cipher_text):
        self.key_len = len(key)
        if cipher_text is None:
            self.plain_len = len(plain_text)
            self.cipher_len = self.plain_len + 15
            self.cast()
            self.plain = (c_ubyte*len(plain_text)).from_buffer_copy(bytearray(plain_text))
        elif plain_text is None:
            self.cipher_len = len(cipher_text)
            self.plain_len = self.cipher_len - 15
            self.cast()
            self.cipher = (c_ubyte*len(cipher_text)).from_buffer_copy(bytearray(cipher_text))
        self.key = (c_ubyte*len(key)).from_buffer_copy(bytearray(key.encode()))
        self.iv = (c_ubyte*IV_LEN).from_buffer_copy(bytearray(iv))

    def cast(self):
        self.key = cast(create_string_buffer(self.key_len), POINTER(c_ubyte))  #需要首先分配内存
        self.iv = cast(create_string_buffer(IV_LEN), POINTER(c_ubyte))  #需要首先分配内存
        self.plain = cast(create_string_buffer(self.plain_len), POINTER(c_ubyte))  #需要首先分配内存
        self.plain_2 = cast(create_string_buffer(self.plain_len), POINTER(c_ubyte))  #需要首先分配内存
        self.cipher = cast(create_string_buffer(self.cipher_len), POINTER(c_ubyte))  #需要首先分配内存

def aaa():
        
    key = "03"
    plain = "O8PIQA36P829P2VXPCVED8PUOPLY7MI32KVNPJ9CF792QWER8AAA381Z5Y68XFD3"
    print(len(plain))
    plain = Process.encodeMsg(plain)
    print(len(plain))

    iv_buffer = cast(create_string_buffer(IV_LEN), POINTER(c_ubyte))
    dll_test.setIv(iv_buffer)
    iv = string_at(iv_buffer, IV_LEN)

    ce = Ce(key, iv, plain , None)

    dll_test.sm4_encrypt_CBC.argtypes = [c_void_p]
    dll_test.sm4_encrypt_CBC(byref(ce))

    cipher = string_at(ce.cipher, ce.cipher_len)
    iv = string_at(ce.iv, IV_LEN)

    string = cipher.decode("latin1")

    ce2 = Ce(key, iv, None, string.encode("latin1"))
    ce2.iv =(c_ubyte*IV_LEN).from_buffer_copy(bytearray(iv))

    #print(string_at(ce2.cipher, ce2.cipher_len), ce2.cipher_len)
    dll_test.sm4_decrypt_CBC.argtypes = [c_void_p]
    dll_test.sm4_decrypt_CBC(byref(ce2))
    #print(string_at(ce.plain, ce.plain_len))
    plain2 = string_at(ce2.plain_2, ce2.plain_len)

    print(Process.decodeMsg(plain2))

def bbb():
    key = "03"
    plain = "ONN01LO02DM243#@%#@^$%@#^@$$#^$^qdfqr43234t!!@#!RD!@\(*&!(*$^!(#*@$^(*^!#(*^($%"
    iv = Security.getIV()

    tt = Security.symmetricEncrypt(key, iv, plain)
    ss = Security.symmetricDecrypt(key, iv,  tt)

#aaa()
bbb()





#class Se(Structure):
#    _fields_ = [
#                ("file_path", POINTER(c_ubyte)),
#                ("country", POINTER(c_ubyte)),
#                ("locality", POINTER(c_ubyte)),
#                ("province", POINTER(c_ubyte)),
#                ("organization", POINTER(c_ubyte)),
#                ("org_unit", POINTER(c_ubyte)),
#                ("common_name", POINTER(c_ubyte)),
#                ("source", POINTER(c_ubyte))]
#
#    def __init__(self):
#        self.file_path = cast(create_string_buffer(50), POINTER(c_ubyte))  #需要首先分配内存
#
#source = "HelloWorld"
##ce = Ce()
##ce.source_len = len(source)
##ce.source = (c_ubyte*len(source)).from_buffer_copy(bytearray(source.encode()))
##
##dll_test.sm4_encrypt_CBC.argtypes = [c_void_p]
##dll_test.sm4_encrypt_CBC(byref(ce))
#
#se = Se()
#file_path = "/home/jiaxv/CLionProjects/acars_crypt/build/test1.pem"
#country = "CN"
#locality = "DongLi"
#province = "TianJin"
#organization = "CAUC"
#org_unit = "AnQuan"
#common_name = "CA"
#se.file_path = (c_ubyte*len(file_path)).from_buffer_copy(bytearray(file_path.encode()))
#se.country = (c_ubyte*len(country)).from_buffer_copy(bytearray(country.encode()))
#se.locality = (c_ubyte*len(locality)).from_buffer_copy(bytearray(locality.encode()))
#se.province = (c_ubyte*len(province)).from_buffer_copy(bytearray(province.encode()))
#se.organization = (c_ubyte*len(organization)).from_buffer_copy(bytearray(organization.encode()))
#se.org_unit = (c_ubyte*len(org_unit)).from_buffer_copy(bytearray(org_unit.encode()))
#se.common_name = (c_ubyte*len(common_name)).from_buffer_copy(bytearray(common_name.encode()))
#
#dll_test.test_x509_cert.argtypes = [c_void_p]
#dll_test.test_x509_cert(byref(se))
