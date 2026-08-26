import struct

for a in [1410, 1064, 2]:
    print(a, "=", struct.pack(">H", a).hex())
