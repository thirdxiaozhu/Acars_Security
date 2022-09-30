import deflate
level = 6  # The default; may be 1-12 for libdeflate.
compressed = deflate.gzip_compress(b"hello world!" * 10, level)
print(compressed)
original = deflate.gzip_decompress(compressed)