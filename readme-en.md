# Claim

## Process of starting program
1. Install `Openssl` and `Pycrypto` libraries
```shell
pip3 install pyopenssl
pip3 install pycryptodome
```
2. Run `CUHK.py` and `Blackboard.py`
3. Run `Student.py`, enter student ID
4. Wait for the program to finish running

## Server and Client
- **CUHK** (Port: 9335)
- **Blackboard** (Port: 3141)
- **Student**

## Program running process

![img_2.png](source/img_2.png)
### Step 0
1. After `CUHK.py` and `Blackboard.py` are started, these two processes keep listening on ports `9335` and `3141` respectively.
2. At the same time, `CUHK.py` will generate key pairs and root certificates, store the root certificate and key in the local `cuhk.cer` and `cuhk.key` locations respectively.
### Step 1
1. Running `Student.py`, then enter **10 digits** as student ID.
2. Then, it will generate a **key pair**, and use it to generate a **CSR request**.
3. Serialize the **CSR request** and send it to `CUHK.py` ( port: 9335 )
### Step 2
1. `CUHK.py` get **CSR request** from `Student.py`.
2. Sign CSR request and use `CSR Request`,`cuhk.cer` and `cuhk.key` to generate **cert 2**.
3. Send back **cert 2** to `Student.py` by socket.
4. `Student.py` get **cert 2** from `CUHK.py` ( port: 9335 ), then dispaly `"SID: ********** sign finished."` in terminal.
### Step 3
1. `Student.py` initiate a request by concatenating, Request: `"SID:********** requests to upload report !"` | `Cert 2`
2. `Blackboard.py` get the request, and then take out `Cert 2` from it.
3. `Blackboard.py` read root certificate from local file`cuhk.cer`.
4. `Blackboard.py` verify the validity of the `Cert 2`, if the verification is passed, go to the next step, or the program will terminate.
### Step 4 
1. `Blackboard.py` generate a `session key`.
2. `Blackboard.py` get the **public key** from `Cert 2`.
3. Use **public key** to encrypt `session key`, and then send it to `Student.py`.
### Step 5
1. `Student.py` get encrypted `session key`, then use its private key that are used to generate the CSR request to decrypt the `session key`.
2. Then, `Student.py` send the decrypted `session key` to `Blackboard.py`.
3. `Blackboard.py` verify the decrypted `session key`.
4. If check pass, `Student.py` and `Blackboard.py` start to communicate.
### Step 6
1. `Student.py` use `session key` and message content to generate **HMAC**, then concatenate message and HMAC: `Message Content` | `HMAC`, send it to `Blackboard.py`.
2. `Blackboard.py` get concatenated message and **HMAC**, then take message out, recalculate HMAC using `session key`.
3. Compare the **HMAC** from `Student.py` with the recalculated **HMAC**, if they are the same, the message is valid, output message in terminal.

## Reference
- [1]  **Socket Programming 1:** https://blog.csdn.net/a883774913/article/details/125395179
- [2]  **Socket Programming 2:** https://blog.csdn.net/Dontla/article/details/103679153
- [3]  **OpenSSL Document:** https://www.pyopenssl.org/en/latest/
- [4]  **Generate Self-Sign Certificate:** https://blog.csdn.net/TheGreenSummer/article/details/110285923
- [5]  **SSL/TLS:** https://blog.csdn.net/wuliganggang/article/details/78428866
- [6]  **SSL/TLS:** https://blog.csdn.net/vip97yigang/article/details/84721027
- [7]  **Wraps pyOpenSSL for quick and easy PKI:** https://github.com/LLNL/certipy
- [8]  **OpenSsl.crypto Usage:** https://vimsky.com/zh-tw/examples/detail/python-method-OpenSSL.crypto.html
- [9]  **Definition Explain:** https://blog.csdn.net/keke_Xin/article/details/84817391
- [10] **CA, Crypto Process:** https://blog.csdn.net/gaoshan12345678910/article/details/114737953
- [11] **RSA Encryption and Decryption:** https://www.jb51.net/article/244576.htm
- [12] **HMAC:** https://star-302.blog.csdn.net/article/details/126887090