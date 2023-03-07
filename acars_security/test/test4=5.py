import deflate

Crypto.Security.getCert("/home/jiaxv/inoproject/Acars_Security/users/dsp/dspcert.pem")
level = 12  # The default; may be 1-12 for libdeflate.
compressed = deflate.gzip_compress(b"hello world!" * 1000, level)
original = deflate.gzip_decompress(compressed)

print(compressed)