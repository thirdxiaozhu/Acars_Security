import OpenSSL
from dateutil import parser


cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, open("users/dsp/dspcert.pem").read())
certIssue = cert.get_issuer()
 
print ("证书版本:            ",cert.get_version() + 1)
 
print ("证书序列号:          ",hex(cert.get_serial_number()))
 
print ("证书中使用的签名算法: ",cert.get_signature_algorithm().decode("UTF-8"))
 
print ("颁发者:              ",certIssue.commonName)
 
datetime_struct = parser.parse(cert.get_notBefore().decode("UTF-8"))
 
print ("有效期从:             ",datetime_struct.strftime('%Y-%m-%d %H:%M:%S'))
 
datetime_struct = parser.parse(cert.get_notAfter().decode("UTF-8"))
 
print ("到:                   ",datetime_struct.strftime('%Y-%m-%d %H:%M:%S'))
 
print ("证书是否已经过期:      ",cert.has_expired())
 
print("公钥长度" ,cert.get_pubkey().bits())
 
print("公钥:\n" ,OpenSSL.crypto.dump_publickey(OpenSSL.crypto.FILETYPE_PEM, cert.get_pubkey()).decode("utf-8"))
 
print("主体信息:")
 
print("CN : 通用名称  OU : 机构单元名称")
print("O  : 机构名    L  : 地理位置")
print("S  : 州/省名   C  : 国名")
 
for item in certIssue.get_components():
    print(item[0].decode("utf-8"), "  ——  ",item[1].decode("utf-8"))
    print(item)
 
print(cert.get_extension_count())
 