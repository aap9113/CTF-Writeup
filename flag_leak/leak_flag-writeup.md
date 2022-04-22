# Flag Leak

##### picoCTF 2022 challenges - [Link to the challenge](https://play.picoctf.org/practice?originalEvent=70&page=4)

> Adwait Pathak | aap9113

<hr>

![challenge](\Artifacts\0-chall.png)

- We get a binary, a source code file and a remote server to connect to.
- We can analyze the binary using ghidra or use the source code.
- We do a checksec on the binary to see the security measures implemented on it.

![checksec](/Artifacts/1-checksec.png)

- There is no canary but the NX bit is enabled.
- The stack is non executable. Hence, we can't input our shellcode and transfer the control of the eip pointer to this code.
- Hence, analyzing the source code.

![code](/Artifacts/1-code.png)

- Trying to understand the source code, we can see that the input variable has size 128.
- We can try a buffer overflow but it won't work because the scanf is implemented where 127 bytes of data will be read.

![bof-try](/Artifacts/2-boftry.png)

- We see that our given input is shortened. Hence, we can't do a bof here.
<br>

- We need to go a few lines above a see the read_flag() function.
- The main function passes control to vuln(), where we go to read_flag().
- read_flag() does not print out the data, but it stores the data in a buffer variable.
- This variable will be present somewhere on the stack.
- Hence, it is not about redirecting the control to that function.
- Also, for the program to work, we need to create an additional file:
    1. *flag.txt*: containing a dummy flag for debugging
<br>

- We see that the printf() is not implemented properly and we can use this to our advantage.
- The compiler does not understand the miss-match in format specifiers and user-data.
> eg: printf('%s', str_input) will print out the string contents from str_input
- But, in our case, when we do only `printf(%s)`, we get program memory as our output.
- The data for the program is stored on a stack and the `printf(format_specifier)` fetches values from the stack in this vulnerability.
> Read about format string vulnerabilities -> Chapter 6: of Computer & Internet Security: *A Hands-on Approach 2e*, by Wenliang Du.


- Hence, we will be using format specifiers to leak output from the program data.
- This is because, the compiler doesn't check if the format specifiers have data in the format string.
- If it sees a format specifier, eg: '%s', it will go the the value above the stack, treat it as an address and print out the data it points to.
- lly, if it sees '%p', it will go the the value above the stack, and print out the address.
- We will use the same approach and enter a bunch of "%p" in the format string as an input to the program.
- This should print out a few address for us.

![format-string-1](/Artifacts/2-formatstring.png)

![format-string-2](/Artifacts/2-formatstring-2.png)

- Now, we don't know which of these addresses point to what data.
- But, most of the addresses are kindof similar and some of them are different.
- Now, as explained earlier, we need the flag string that is stored in some variable which has to be on the stack.
- For this, we have to use the %s specifier which will get the string from the address on the stack.
- Now, we can calculate manually at which point we see a different address and specify that number to the %s.
> eg: `%15$s` will return a string if present at the 15 position above the current location of the stack, else, the program will crash.
- This method will take a lot of trail and error.
- Rather, we can write a script that will test every position for the string value and if not present, returns a segfault.
- This way, we will be able to find the string present at every position above the stack.

![local-code](/Artifacts/3-local-code.png)

- This Python script will run thru a for loop (i) and send data to the binary in the mentioned method `%{i}$s`
- If we get a segfault, we know that there is no string in this position and we move to the next position.
- If there is a string, the position on the stack and the string content will be printed out to us.

![local-flag](/Artifacts/3-local-flag.png)

- We see our debugging flag in the output.
- Hence, we can see that the flag is being stored on the 24th position on the stack above the current position.
- Now, we can directly use %24$s as input for the remote flag or we can run the same program to output more data present on the stack.
- Hence, taking the code remote.

![remote-code](/Artifacts/3-remote-code.png)

- We find the flag using the format string vulnerability
- The server port numbers change because the instance is restarted.

![remote-flag](/Artifacts/remote-flag.png)

- Hence, PWNED!
