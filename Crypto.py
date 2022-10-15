from ctypes import *
import test
import base64

dll_test = CDLL("/home/jiaxv/CLionProjects/acars_crypt/build/libacarscrypt.so")

MODE_CMU = 210
MODE_DSP = 220

IV_LEN = 16

class Se(Structure):
    _fields_ = [
                ("file_path", POINTER(c_ubyte)),
                ("pub_path", POINTER(c_ubyte)),
                ("pri_path", POINTER(c_ubyte)),
                ("country", POINTER(c_ubyte)),
                ("locality", POINTER(c_ubyte)),
                ("province", POINTER(c_ubyte)),
                ("organization", POINTER(c_ubyte)),
                ("org_unit", POINTER(c_ubyte)),
                ("common_name", POINTER(c_ubyte)),
                ("source", POINTER(c_ubyte))]

    def __init__(self):
        self.file_path = cast(create_string_buffer(100), POINTER(c_ubyte))  #需要首先分配内存
        self.pub_path = cast(create_string_buffer(100), POINTER(c_ubyte))  
        self.pri_path = cast(create_string_buffer(100), POINTER(c_ubyte))  


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
            self.cipher = (c_ubyte*self.cipher_len).from_buffer_copy(bytearray([0 for i in range(self.cipher_len)]))
        elif plain_text is None:
            self.cipher_len = len(cipher_text)
            self.plain_len = self.cipher_len 
            self.cast()
            self.cipher = (c_ubyte*len(cipher_text)).from_buffer_copy(bytearray(cipher_text))
            self.plain = (c_ubyte*self.plain_len).from_buffer_copy(bytearray([0 for i in range(self.plain_len)]))
        self.key = (c_ubyte*len(key)).from_buffer_copy(bytearray(key.encode()))
        self.iv = (c_ubyte*IV_LEN).from_buffer_copy(bytearray(iv))

    def cast(self):
        self.key = cast(create_string_buffer(self.key_len), POINTER(c_ubyte)) 
        self.iv = cast(create_string_buffer(IV_LEN), POINTER(c_ubyte))  
        self.plain = cast(create_string_buffer(self.plain_len), POINTER(c_ubyte))  
        self.plain_2 = cast(create_string_buffer(self.plain_len), POINTER(c_ubyte))  
        self.cipher = cast(create_string_buffer(self.cipher_len), POINTER(c_ubyte))  

    def calloc(self, component, length):
        calloc_0 = bytearray([0 for i in range(length)])
        component = (c_ubyte*length).from_buffer_copy(bytearray([0 for i in range(length)]))

class Security:
    def getIV():
        iv_buffer = cast(create_string_buffer(IV_LEN), POINTER(c_ubyte))
        dll_test.setIv(iv_buffer)
        iv = string_at(iv_buffer, IV_LEN)
        return iv

    def cert_test(path, paras, entity_num):
        se = Se()
        if entity_num == MODE_DSP:
            pem_path = "/home/jiaxv/inoproject/Acars_Security/" + path + "dspcert.pem"
            pub_path = "/home/jiaxv/inoproject/Acars_Security/" + path + "dsppub.pem"
            pri_path = "/home/jiaxv/inoproject/Acars_Security/" + path + "dsppri.pem"
        elif entity_num == MODE_CMU:
            pem_path = "/home/jiaxv/inoproject/Acars_Security/" + path + "cmucert.pem"
            pub_path = "/home/jiaxv/inoproject/Acars_Security/" + path + "cmupub.pem"
            pri_path = "/home/jiaxv/inoproject/Acars_Security/" + path + "cmupri.pem"
        country = paras[0]
        locality = paras[1]
        province = paras[2]
        organization = paras[3]
        org_unit = paras[4]
        common_name = paras[5]
        se.file_path = (c_ubyte*len(pem_path)).from_buffer_copy(bytearray(pem_path.encode()))
        se.pub_path = (c_ubyte*len(pub_path)).from_buffer_copy(bytearray(pub_path.encode()))
        se.pri_path = (c_ubyte*len(pri_path)).from_buffer_copy(bytearray(pri_path.encode()))
        se.country = (c_ubyte*len(country)).from_buffer_copy(bytearray(country.encode()))
        se.locality = (c_ubyte*len(locality)).from_buffer_copy(bytearray(locality.encode()))
        se.province = (c_ubyte*len(province)).from_buffer_copy(bytearray(province.encode()))
        se.organization = (c_ubyte*len(organization)).from_buffer_copy(bytearray(organization.encode()))
        se.org_unit = (c_ubyte*len(org_unit)).from_buffer_copy(bytearray(org_unit.encode()))
        se.common_name = (c_ubyte*len(common_name)).from_buffer_copy(bytearray(common_name.encode()))

        dll_test.test_x509_cert.argtypes = [c_void_p]
        dll_test.test_x509_cert(byref(se))

    def symmetricEncrypt(key, iv, plain_str):

        plain = test.payloadEncode(plain_str)
        ce = Ce(key, iv, plain, None)

        dll_test.sm4_encrypt_CBC.argtypes = [c_void_p]
        dll_test.sm4_encrypt_CBC(byref(ce))

        cipher = string_at(ce.cipher, ce.cipher_len)
        iv = string_at(ce.iv, IV_LEN)

        cipher_str = cipher.decode("latin1")


        return test.messageEncode(cipher_str.encode("latin1"))
    
    def symmetricDecrypt(key, iv, cipher_str):
        ce2 = Ce(key, iv, None, test.messageDecode(cipher_str))
        ce2.iv =(c_ubyte*IV_LEN).from_buffer_copy(bytearray(iv))

        dll_test.sm4_decrypt_CBC.argtypes = [c_void_p]
        dll_test.sm4_decrypt_CBC(byref(ce2))
        plain2 = string_at(ce2.plain_2, ce2.plain_len)

        #print("!!!!!" , test.payloadDecode(plain2))
        
        return test.payloadDecode(plain2)
