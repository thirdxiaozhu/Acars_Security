from ctypes import *

class Ce(Structure):
    _fields_ = [("source_len", c_int),
                ("source", POINTER(c_ubyte))]

    def __init__(self):
        self.complex_i8 = cast(create_string_buffer(50), POINTER(c_ubyte))  #需要首先分配内存

class Se(Structure):
    _fields_ = [
                ("file_path", POINTER(c_ubyte)),
                ("country", POINTER(c_ubyte)),
                ("locality", POINTER(c_ubyte)),
                ("province", POINTER(c_ubyte)),
                ("organization", POINTER(c_ubyte)),
                ("org_unit", POINTER(c_ubyte)),
                ("common_name", POINTER(c_ubyte)),
                ("source", POINTER(c_ubyte))]

    def __init__(self):
        self.file_path = cast(create_string_buffer(50), POINTER(c_ubyte))  #需要首先分配内存

source = "HelloWorld"
dll_test = CDLL("/home/jiaxv/CLionProjects/acars_crypt/build/libacarscrypt.so")
#ce = Ce()
#ce.source_len = len(source)
#ce.source = (c_ubyte*len(source)).from_buffer_copy(bytearray(source.encode()))
#
#dll_test.sm4_encrypt_CBC.argtypes = [c_void_p]
#dll_test.sm4_encrypt_CBC(byref(ce))

se = Se()
file_path = "/home/jiaxv/CLionProjects/acars_crypt/build/test1.pem"
country = "CN"
locality = "DongLi"
province = "TianJin"
organization = "CAUC"
org_unit = "AnQuan"
common_name = "CA"
se.file_path = (c_ubyte*len(file_path)).from_buffer_copy(bytearray(file_path.encode()))
se.country = (c_ubyte*len(country)).from_buffer_copy(bytearray(country.encode()))
se.locality = (c_ubyte*len(locality)).from_buffer_copy(bytearray(locality.encode()))
se.province = (c_ubyte*len(province)).from_buffer_copy(bytearray(province.encode()))
se.organization = (c_ubyte*len(organization)).from_buffer_copy(bytearray(organization.encode()))
se.org_unit = (c_ubyte*len(org_unit)).from_buffer_copy(bytearray(org_unit.encode()))
se.common_name = (c_ubyte*len(common_name)).from_buffer_copy(bytearray(common_name.encode()))

dll_test.test_x509_cert.argtypes = [c_void_p]
dll_test.test_x509_cert(byref(se))


import base64


# base64解码
def base64_decode(base64_data):
    temp = base64.b64decode(base64_data).hex()
    return temp


data = "MIGTAgEAMBMGByqGSM49AgEGCCqBHM9VAYItBHkwdwIBAQQgnjU54bw2PSSh4ZtMgRzt0sdvty2V7+HwLRhwhkCkaDugCgYIKoEcz1UBgi2hRANCAASShZ1nhJS+xjW3Y+bUPF8BJcCSl4pgWArqAXqN7roFbfeq+deCQXOPkrVXXDL4Gsy2MXf/khlSRY4/oxYRtymp"
tem = base64_decode(data)
print(tem)