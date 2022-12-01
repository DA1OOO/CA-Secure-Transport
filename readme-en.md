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
### Step 0
1. After `CUHK.py` and `Blackboard.py` are started, these two processes keep listening on ports `9335` and `3141` respectively.
2. At the same time, `CUHK.py` will generate key pairs and root certificates, store the root certificate and key in the local `cuhk.cer` and `cuhk.key` locations respectively.
### Step 1
1. Running `Student.py`, then enter **10** **digital** number as student ID.
2. Then, it will generate a **key pair**, and use it to generate a **CSR request**.
3. Serialize the CSR request and send it to `CUHK.py` ( port: 9335 )
### Step 2
1. `CUHK.py` get **CSR request** from `Student.py`.
2. Sign CSR request and generate **cert 2**.
3. Send back **cert 2** to `Student.py` by socket.


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