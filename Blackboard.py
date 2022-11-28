# Blackboard服务端 端口3141
import socket
import random
import base64
from OpenSSL import crypto
from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

CERT_FILE = 'cuhk.cer'


def initial_socket():
    print("-------- Socket Initial -----------")
    # 创建套接字
    try:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Create socket succeeded!")
    except socket.error as err:
        print("Create socket failed!，error details: %s" % (err))
    # 套接字默认端口
    port = 3141
    # 监听本机上80端口的网络请求
    my_socket.bind(('127.0.0.1', port))
    # 切换套接字到监听模式，最多阻塞5笔请求
    my_socket.listen(5)
    print("Socket listening...")
    return my_socket


# 接受客户端连接，并保持监听
def connect_accept(my_socket, tag, reply_msg='===> Thanks for your connect!'.encode()):
    # 与客户端建立连接。
    c, addr = my_socket.accept()

    print('----------', 'No.', tag, 'Connect Success!', '---------')
    print('addr:', addr)
    tag += 1
    # 向客户发送回复信息。编码以发送字节类型。
    c.send(reply_msg)
    recv_str = c.recv(1024)
    dec_str = recv_str.decode()
    print("Received msg: %s" % dec_str)
    # 关闭与客户端的连接
    c.close()
    print("---------Connect close------------")
    return recv_str


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
    # 初始化socket
    my_socket = initial_socket()
    # 建立连接 保持监听
    tag = 1
    while True:
        byte_msg = connect_accept(my_socket, tag)
        tag += 1
        if tag == 2:
            break
    msg = byte_msg.decode()
    # 拆分request信息 获取sid和证书部分
    split_msg = msg.split('|')
    sid = split_msg[0]
    cert2 = crypto.load_certificate(crypto.FILETYPE_PEM, split_msg[1])
    # 对证书校验
    with open(CERT_FILE, "r") as f:
        # 读取CUHK根证书
        root_cert = crypto.load_certificate(crypto.FILETYPE_PEM, f.read())
    x509_store = crypto.X509Store()
    x509_store.add_cert(root_cert)
    x509_store_context = crypto.X509StoreContext(x509_store, cert2)
    if x509_store_context.verify_certificate() is None:
        print("===> Cert Check success！")
    else:
        print('===> Cert Check failed')
        return
    # 生成16位Session key, 开始准备会话
    session_key = ''.join(random.sample(
        ['z', 'y', 'x', 'w', 'v', 'u', 't', 's', 'r', 'q', 'p', 'o', 'n', 'm', 'l', 'k', 'j', 'i', 'h', 'g', 'f', 'e',
         'd', 'c', 'b', 'a', '!', '@', '#', '$', '%', '^', '&', '*'], 16))
    # 从证书中取出公钥
    pub_key = crypto.dump_publickey(crypto.FILETYPE_PEM, cert2.get_pubkey())
    # 将session key加密
    encrypt_session_key = rsa_encryption(session_key, pub_key)

    # 发送加密后的session key到Student进程
    my_socket_1 = initial_socket()
    # 接受客户端链接，并发送加密后的session key给客户端
    connect_accept(my_socket_1, 0, bytes(encrypt_session_key.encode()))


if __name__ == '__main__':
    main()
