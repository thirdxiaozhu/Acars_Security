from ctypes import *
import Process

dll_test = CDLL("/home/jiaxv/CLionProjects/acars_crypt/build/libacarscrypt.so")

MODE_CMU = 210
MODE_DSP = 220
MODE_CA = 230

IV_LEN = 16
KEY_LEN = 16
SIGN_LEN = 72
CA_PRIV_PATH = "/home/jiaxv/inoproject/Acars_Security/users/ca/capri.pem"
CA_PASSWD = "iamca"

class Se(Structure):
    _fields_ = [
                ("file_path", POINTER(c_ubyte)),
                ("pub_path", POINTER(c_ubyte)),
                ("pri_path", POINTER(c_ubyte)),
                ("ca_path", POINTER(c_ubyte)),
                ("ca_passwd", POINTER(c_ubyte)),
                ("passwd", POINTER(c_ubyte)),
                ("country", POINTER(c_ubyte)),
                ("locality", POINTER(c_ubyte)),
                ("province", POINTER(c_ubyte)),
                ("organization", POINTER(c_ubyte)),
                ("org_unit", POINTER(c_ubyte)),
                ("common_name", POINTER(c_ubyte)),
                ("source", POINTER(c_ubyte))]

    def __init__(self):
        self.file_path = cast(create_string_buffer(255), POINTER(c_ubyte))  #需要首先分配内存
        self.pub_path = cast(create_string_buffer(255), POINTER(c_ubyte))  
        self.pri_path = cast(create_string_buffer(255), POINTER(c_ubyte))  
        self.ca_path = cast(create_string_buffer(255), POINTER(c_ubyte))  


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
            self.cipher_len = self.plain_len + 16
            
            self.cast()
            self.plain = (c_ubyte*len(plain_text)).from_buffer_copy(bytearray(plain_text))
            self.cipher = (c_ubyte*self.cipher_len).from_buffer_copy(bytearray([0 for i in range(self.cipher_len)]))
        elif plain_text is None:
            self.cipher_len = len(cipher_text)
            self.plain_len = self.cipher_len -16
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

class Security:
    def getIV():
        iv_buffer = cast(create_string_buffer(IV_LEN), POINTER(c_ubyte))
        dll_test.setIv(iv_buffer)
        iv = string_at(iv_buffer, IV_LEN)
        return iv

    def cert_test(path, paras, entity_num, passwd):
        se = Se()
        if entity_num == MODE_DSP:
            pem_path = "/home/jiaxv/inoproject/Acars_Security/" + path + "dspcert.pem" + "\x00"
            pub_path = "/home/jiaxv/inoproject/Acars_Security/" + path + "dsppub.pem" + "\x00"
            pri_path = "/home/jiaxv/inoproject/Acars_Security/" + path + "dsppri.pem" + "\x00"
        elif entity_num == MODE_CMU:
            pem_path = "/home/jiaxv/inoproject/Acars_Security/" + path + "cmucert.pem" + "\x00"
            pub_path = "/home/jiaxv/inoproject/Acars_Security/" + path + "cmupub.pem" + "\x00"
            pri_path = "/home/jiaxv/inoproject/Acars_Security/" + path + "cmupri.pem" + "\x00"
        elif entity_num == MODE_CA:
            pem_path = "/home/jiaxv/inoproject/Acars_Security/" + path + "cacert.pem" + "\x00"
            pub_path = "/home/jiaxv/inoproject/Acars_Security/" + path + "capub.pem" + "\x00"
            pri_path = "/home/jiaxv/inoproject/Acars_Security/" + path + "capri.pem" + "\x00"
        
        country = paras[0]
        locality = paras[1]
        province = paras[2]
        organization = paras[3]
        org_unit = paras[4]
        common_name = paras[5]
        se.file_path = (c_ubyte*len(pem_path)).from_buffer_copy(bytearray(pem_path.encode()))
        se.pub_path = (c_ubyte*len(pub_path)).from_buffer_copy(bytearray(pub_path.encode()))
        se.pri_path = (c_ubyte*len(pri_path)).from_buffer_copy(bytearray(pri_path.encode()))
        se.ca_path = (c_ubyte*len(CA_PRIV_PATH)).from_buffer_copy(bytearray(CA_PRIV_PATH.encode()))
        se.ca_passwd = (c_ubyte*len(CA_PASSWD)).from_buffer_copy(bytearray(CA_PASSWD.encode()))
        se.passwd = (c_ubyte*len(passwd)).from_buffer_copy(bytearray(passwd.encode()))
        se.country = (c_ubyte*len(country)).from_buffer_copy(bytearray(country.encode()))
        se.locality = (c_ubyte*len(locality)).from_buffer_copy(bytearray(locality.encode()))
        se.province = (c_ubyte*len(province)).from_buffer_copy(bytearray(province.encode()))
        se.organization = (c_ubyte*len(organization)).from_buffer_copy(bytearray(organization.encode()))
        se.org_unit = (c_ubyte*len(org_unit)).from_buffer_copy(bytearray(org_unit.encode()))
        se.common_name = (c_ubyte*len(common_name)).from_buffer_copy(bytearray(common_name.encode()))

        dll_test.test_x509_cert.argtypes = [c_void_p]
        dll_test.test_x509_cert(byref(se))

    def symmetricEncrypt(key, iv, plain_str):
        plain = Process.payloadEncode(plain_str)

        ce = Ce(key, iv, plain, None)

        dll_test.sm4_encrypt_CBC.argtypes = [c_void_p]
        dll_test.sm4_encrypt_CBC(byref(ce))

        cipher = string_at(ce.cipher, ce.cipher_len)
        iv = string_at(ce.iv, IV_LEN)

        cipher_str = cipher.decode("latin1")
        return cipher_str
    
    def symmetricDecrypt(key, iv, cipher_str):
        ce2 = Ce(key, iv, None, cipher_str)
        ce2.iv =(c_ubyte*IV_LEN).from_buffer_copy(bytearray(iv))

        dll_test.sm4_decrypt_CBC.argtypes = [c_void_p]
        dll_test.sm4_decrypt_CBC(byref(ce2))
        plain2 = string_at(ce2.plain_2, ce2.plain_len)

        return Process.payloadDecode(plain2)

    def getSign(path, cipher, key):
        filepath_encoded = path.encode("latin1")
        filepath = (c_char*len(filepath_encoded)).from_buffer_copy(bytearray(filepath_encoded))

        cipher_encoded = cipher.encode("latin1")
        cipher_text = (c_ubyte*len(cipher_encoded)).from_buffer_copy(bytearray(cipher_encoded))
        cipherlen = c_size_t(len(cipher_encoded))

        sign_space = cast(create_string_buffer(SIGN_LEN), POINTER(c_ubyte))  
        signlen = c_size_t(0)

        prikey = (c_char*len(key)).from_buffer_copy(bytearray(key.encode()))
        dll_test.getSign(filepath, sign_space, byref(signlen), cipher_text, cipherlen, prikey)
        
        return string_at(sign_space, signlen.value)

    def verySign(path, cipher, signtext):
        filepath_encoded = path.encode("latin1")
        filepath = (c_char*len(filepath_encoded)).from_buffer_copy(bytearray(filepath_encoded))

        cipher_text = (c_ubyte*len(cipher)).from_buffer_copy(bytearray(cipher))
        cipherlen = c_size_t(len(cipher))

        sign_text = (c_ubyte*len(signtext)).from_buffer_copy(bytearray(signtext))
        signlen = c_size_t(len(signtext))

        ret = dll_test.verifySign(filepath, sign_text, signlen, cipher_text,cipherlen)

        return ret
    
    def getCert(path):
        path = path + "\00"
        file_path = (c_char*len(path)).from_buffer_copy(bytearray(path.encode("latin1")))
        cert_space = cast(create_string_buffer(1024), POINTER(c_ubyte))  
        cert_len = c_size_t(0)
        dll_test.getCertWith64(file_path, cert_space, byref(cert_len))

        return string_at(cert_space, cert_len.value)
    
    def verifyCert(cert):
        capath = "/home/jiaxv/inoproject/Acars_Security/users/ca/cacert.pem" + "\00"
        ca_path_b = (c_char*len(capath)).from_buffer_copy(bytearray(capath.encode("latin1")))
        user_cert = (c_char*len(cert)).from_buffer_copy(bytearray(cert))
        user_len = c_size_t(len(cert))

        return dll_test.verifyCert(ca_path_b, user_cert, user_len)
    
    def encryptSymKey(cert):
        random_key = cast(create_string_buffer(KEY_LEN), POINTER(c_ubyte))  
        user_cert = (c_char*len(cert)).from_buffer_copy(bytearray(cert))
        user_len = c_size_t(len(cert))
        ret = cast(create_string_buffer(1024), POINTER(c_ubyte))
        ret_len = c_size_t(0)

        dll_test.encryptRandomSymKey(random_key, user_cert, user_len, ret, byref(ret_len))

        return (string_at(random_key, KEY_LEN), string_at(ret, ret_len.value))
    
    def decryptSymKey(cipher):
        pripath = "/home/jiaxv/inoproject/Acars_Security/users/dsp/dsppri.pem" + "\00"
        pri_path_b = (c_char*len(pripath)).from_buffer_copy(bytearray(pripath.encode("latin1")))
        cipher_in = (c_char*len(cipher)).from_buffer_copy(bytearray(cipher))
        cipher_len = c_size_t(len(cipher))
        plain_out = cast(create_string_buffer(KEY_LEN), POINTER(c_ubyte))
        plain_len = c_size_t(0)

        is_success = dll_test.decryptRandomSymKey(pri_path_b, cipher_in, cipher_len, plain_out, byref(plain_len))

        if is_success == 0:
            return string_at(plain_out, plain_len.value)
        else:
            return None