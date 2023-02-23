import Crypto_Util

#cert = b'0\x82\x01\xcf0\x82\x01r\xa0\x03\x02\x01\x02\x02\x14\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x000\x0c\x06\x08*\x81\x1c\xcfU\x01\x83u\x05\x000e1\x0b0\t\x06\x03U\x04\x06\x13\x02CN1\x0f0\r\x06\x03U\x04\x07\x13\x06DongLi1\x100\x0e\x06\x03U\x04\x08\x13\x07TianJin1\r0\x0b\x06\x03U\x04\n\x13\x04CAUC1\x0f0\r\x06\x03U\x04\x0b\x13\x06AnQuan1\x130\x11\x06\x03U\x04\x03\x13\nDspDefault0\x1e\x17\r230216213059Z\x17\r240216133059Z0e1\x0b0\t\x06\x03U\x04\x06\x13\x02CN1\x0f0\r\x06\x03U\x04\x07\x13\x06DongLi1\x100\x0e\x06\x03U\x04\x08\x13\x07TianJin1\r0\x0b\x06\x03U\x04\n\x13\x04CAUC1\x0f0\r\x06\x03U\x04\x0b\x13\x06AnQuan1\x130\x11\x06\x03U\x04\x03\x13\nDspDefault0Y0\x13\x06\x07*\x86H\xce=\x02\x01\x06\x08*\x81\x1c\xcfU\x01\x82-\x03B\x00\x04\xbaT2x\x0bC\xf3&\xb7[U7\x03\xd2H\t\x0fDBE\xf2\x0f\xb8\xe2\xa6\xae\x0c\x1a\xd6t\xdfg\xee\xbc^;\xc3\xa7_H\xb5\xfe\xad(\xb1R\x07\xba\xceD<\xd5OP\xd3\xf8\xde\x9cT\xae[\xcf\xa7\x0e0\x0c\x06\x08*\x81\x1c\xcfU\x01\x83u\x05\x00\x03I\x000F\x02!\x00\xb5\xc8`\xb1x\x1c\x9b\xaaA }B\xa6\xd1\x81\xc83aq\xb0\xb9\xc4s\x0b6W\xf5\xc2\x88\x02\x91\xea\x02!\x00\xfd\xa0\x1b\xc3.~\x1f\xdc\xaf\xf9W\xa8\x07@\x94UucH\xbdG\xfdA\x13\xb4\x0f\x997\xdc\x89x\xd3'

cert = Crypto_Util.Security.getCert("/home/jiaxv/inoproject/Acars_Security/users/dsp/dspcert.pem")
Crypto_Util.Security.verifyCert(cert)
ret = Crypto_Util.Security.encryptSynKey(cert)
print(ret)

ret = Crypto_Util.Security.decryptSynKey(ret)
print(ret)