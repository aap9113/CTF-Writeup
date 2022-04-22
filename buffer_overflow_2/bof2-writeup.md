# Buffer Overflow 2

##### picoCTF 2022 challenges - [Link to the challenge](https://play.picoctf.org/practice?originalEvent=70&page=4)

> Adwait Pathak | aap9113

<hr>

![challenge-info](/Artifacts/0-chall.png)

- We get a binary, a source file and a server to connect to.
- We analyze the binary in Ghidra to see the flow of the program and the functions that will help us in exploitation.
    - Or we can directly view the source code file.
- First, lets check the details of the binary.

![checksec](/Artifacts/2-checksec.png)

- It is a 32-bit binary and hence, we will be using 4 byte increments in our attempt to pwn the binary.
- It also doesnt have a canary but the stack is non executable.
    - Hence, we can't input our shellcode and transfer the control of the eip pointer to this code.
- But, we see we have a win() function that we will try to transfer the control to.

![code](/Artifacts/1-code.png)

- We see that the main function asks for a string and passes the control to function vuln().
- vuln() has a gets() function which we have studied to be vulnerable to buffer overflow.
- It accepts user-sized input and tries to fit it in the buffer variable.
- We know the buffer size is 100, so we try to overflow the program with an input of 150 to check if we get a segfault.


![segfault](/Artifacts/3-segfault.png)

- We get a segmentation fault because of the buffer overflow overwriting important values.
- We can check this in gdb.

![segfault-gdb](/Artifacts/3-segfault-gdb.png)

- We can see that the eip (instruction pointer) has been overwritten and program crashes.
- Hence, we can control the flow of the program using our input string.
- But, we need to find the offset where the `(input + previous frame pointer) = offset` + return address is placed.
- We can do that by creating a unique *pattern* which is a feature of `gdb-peda`
- We can give this pattern as the input and then input the $eip value after the program stops to the same pattern module to get the offset.

![input-pattern](/Artifacts/4-pattern-1.png)

![find-offset](/Artifacts/4-pattern-offset.png)

- We see that the offset is 112. Hence, the value in `input_string[112:116]` will have the return address that we need to control.
- We want to direct the control to the win() function, hence, we will find the address of this function and then pack this into a 32bit address using pwntools and then input this to the binary.

![info-registers](/Artifacts/4-info-functions.png)

- We write a simple python script using pwntools (thanks to the offsec course)
- We pack the win() address as specified and append it to the offset.
- We send this payload to the binary as user input and print the response.

![local-code-1](/Artifacts/4-pwnscript1.png)

![](/Artifacts/4-pwn-local-1.png)

- The output says that there is no flag in the local version.
- Hence, without seeing the win() function, I tried this on the remote site thinking that it will have a flag.txt and give us the flag contents.
- We do this by making changes to the code, uncommenting the remote part.

![remote-1](/Artifacts/4-remote-pwn-1.png)

- But, we did not get the flag. This means there is more to the win() function than just redirecting control.
- Checking the win() function, we can see that there is comparison of the parameter values.

![win-code](/Artifacts/4-win-code.png)

- We need to match these values in order to print the flag.
- Hence, continuing locally, I made 2 more files.
    1. flag.txt: containing a dummy flag for debugging
    2. badfile: to give input during gdb -> `gdb-peda$ r < badfile`

![badfile-flag](/Artifacts/5-badfile1.png)

![disas-win](/Artifacts/5-a_disas_win.png)

- We disassemble the win() function to take a deeper look.
- We set a breakpoint before the comparison takes place to check the values that are being held in these parameters.

![find-values-ebp](/Artifacts/5-acomparison.png)

- we manually examine the hexadecimal value present in the register compared with 0xcafef00d
- we also examine the string it represents and we can see that these values are not something that are a part of our previous input string.
- Hence, in order to control these values, I can think of extending the user input and check if these registers are being affected.
- I added a few 'B's at the end of our input string. (add 'B'*20)

![adding-bs](/Artifacts/5-bs-add.png)

- We echo this string to the badfile and then input it to gdb while running with our breakpoint set

![b-gdb](/Artifacts/5-b-gdb.png)

- Now, when we examine the string present at the comparison parameter, we see that it is replaced with Bs.
- Hence, the arguements can be controlled with the user input.
- We see 'B' 16 times and we had added 20 Bs which means that the first 4 are not being considered. Hence the offset is 4.
- But we need to confirm this. We can do this similarly using pattern in `gdb-peda$ pattern create 20`
- We append this pattern to our previous input: `'A'*112 + return_add + pattern_string` and echo it to the badfile.

![gdb-get-offset](/Artifacts/5-echo-pattern.png)

- Now, running the program with the breakpoint.

![gdb-get-offset](/Artifacts/5-gdb-pattern.png)

- We see our pattern string and we can find the offset of our unqiue string at `$ebp+0x8 to be 4`. lly, at `$ebp+0xc is 8`.
- Hence, our input string should be of the form:
` 'A'*112 + win_address + 'A'*4 + 0xcafef00d + 0xf00df00d`
- This way, when the eip is turned to win(), during comparison of `$ebp+8` and `$ebp+12`, the correct values will be seen respectively.

<br>

- Now, taking all this to our python code, we will try to get the flag on the local binary first.
- The new code will look like the following:

![local-code-final](/Artifacts/6-local-final.png)

- Here we keep any 4 characters after the ret_add as they don't matter
- The packing of integers is important for the computer to read these bytes of data properly
> eg: p32(0xdeadbeef) >> b'\xef\xbe\xad\xde'
- Running this script, we get our debugger flag properly.

![local-flag](/Artifacts/6-local-flag.png)

- Now, we can take this to the remote server.

![remote-code](/Artifacts/6-remote-code.png)

![remote-flag](/Artifacts/6-remote-flag.png)

- Hence, PWNED.