import deflate
import Crypto_Util as Crypto
a = Crypto.Security.getCert("/home/jiaxv/inoproject/Acars_Security/users/ca/cacert.pem")
print(a)
level = 12  # The default; may be 1-12 for libdeflate.
compressed = deflate.gzip_compress(a, level)
original = deflate.gzip_decompress(compressed)

print(len(compressed), len(a))

