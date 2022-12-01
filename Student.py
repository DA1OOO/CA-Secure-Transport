## Student客户端
import socket
import base64
import hmac
from Crypto import Random
from OpenSSL import crypto
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

TYPE_RSA = crypto.TYPE_RSA


# 连接到目标端口
def connect_port(port):
    # 创建socket 对象
    my_socket = socket.socket()
    # 连接到本地计算机上的服务器上的port端口
    my_socket.connect(('127.0.0.1', port))
    return my_socket


# 用户输入
def input_info():
    sid = input("=====> Enter student ID (10 digit number): ")
    # 数据校验
    while len(sid) != 10 or (sid.isdecimal() is not True):
        sid = input("=====> Error input! Please input again: ")
    return sid


def generate_key_pair(cert_type, bits):
    pkey = crypto.PKey()
    pkey.generate_key(cert_type, bits)
    return pkey


def generate_crs_request(pkey, digest="sha256", **name):
    req = crypto.X509Req()
    subj = req.get_subject()

    if name is not None:
        for key, value in name.items():
            setattr(subj, key, value)

    req.set_pubkey(pkey)
    req.sign(pkey, digest)
    return req


# RSA加密
def rsa_encryption(text: str, public_key: bytes):
    # 字符串指定编码（转为bytes）
    text = text.encode('utf-8')
    # 构建公钥对象
    cipher_public = PKCS1_v1_5.new(RSA.importKey(public_key))
    # 加密（bytes）
    text_encrypted = cipher_public.encrypt(text)
    # base64编码，并转为字符串
    text_encrypted_base64 = base64.b64encode(text_encrypted).decode()
    return text_encrypted_base64


# RSA解密
def rsa_decryption(text_encrypted_base64: str, private_key: bytes):
    # 字符串指定编码（转为bytes）
    text_encrypted_base64 = text_encrypted_base64.encode('utf-8')
    # base64解码
    text_encrypted = base64.b64decode(text_encrypted_base64)
    # 构建私钥对象
    cipher_private = PKCS1_v1_5.new(RSA.importKey(private_key))
    # 解密（bytes）
    text_decrypted = cipher_private.decrypt(text_encrypted, Random.new().read)
    # 解码为字符串
    text_decrypted = text_decrypted.decode()
    return text_decrypted


def main():
    print('################ Step 1 ################')
    # 发送SID到CUHK
    sid = input_info()
    my_socket = connect_port(9335)
    my_socket.send(sid.encode())
    print(my_socket.recv(1024).decode())
    my_socket.close()

    key_pair = generate_key_pair(TYPE_RSA, 1024)
    pri_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, key_pair)
    csr_request = generate_crs_request(pkey=key_pair)
    print('=====> CSR Request Generated.')
    # 序列化x509req 并发送到CUHK
    byte_csr_request = crypto.dump_certificate_request(crypto.FILETYPE_PEM, csr_request)
    my_socket_1 = connect_port(9335)
    my_socket_1.send(byte_csr_request)
    print(my_socket_1.recv(1024).decode())
    my_socket_1.close()

    # 通过socket从CUHK获取cert2
    my_socket_2 = connect_port(9335)
    byte_cert2 = my_socket_2.recv(4096)
    my_socket_2.close()
    print('===> Get Cert2!')
    print('===> SID:', sid, 'sign finished!')

    # 初始化request 并发送到Blackboard [SID, cert2]
    my_socket_3 = connect_port(3141)
    temp_request = '===> Student: (' + sid + ') requests to upload report !' + '|' + str(byte_cert2.decode())
    my_socket_3.send(temp_request.encode())

    # 通过socket从Blackboard处获取session key
    my_socket_4 = connect_port(3141)
    encrypted_session_key = my_socket_4.recv(4096)
    my_socket_4.send('get session key!'.encode())

    # 解密session key
    print('===> encrypted_session_key:', encrypted_session_key.decode())
    decrypt_session_key = rsa_decryption(encrypted_session_key.decode(), pri_key)
    print('===> decrypt_session_key:', decrypt_session_key)
    # 将解密后的session key发送到blackboard端校验
    my_socket_5 = connect_port(3141)
    my_socket_5.send(bytes(decrypt_session_key.encode()))

    # 等待blackboard校验session是否安全
    my_socket_6 = connect_port(3141)
    re_msg = my_socket_6.recv(4096).decode()
    my_socket_6.send(bytes("TRUE".encode()))
    if re_msg == "Session secure!":
        print(re_msg)
    else:
        print(re_msg)
        return

    # Step 6 开始发送msg + mac
    for i in range(1, 11):
        msg = ('This is No.' + str(i) + ' Message.|').encode()

        mac = hmac.new(bytes(decrypt_session_key.encode()), msg, digestmod='sha256').digest()
        base64_mac = base64.b64encode(mac)
        my_socket_7 = connect_port(3141)
        my_socket_7.send(msg + base64_mac)


if __name__ == '__main__':
    main()
