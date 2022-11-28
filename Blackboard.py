# Blackboard服务端 端口3141
import socket
import random
from OpenSSL import SSL
from OpenSSL import crypto
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

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
    # 生成rsa密钥
    pri_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    # 从密钥中提取公钥
    pub_key = pri_key.public_key()
    # 用公钥加密
    encrypted_session = pub_key.encrypt(
        session_key.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    # 用私钥解密
    decrypted_session = pri_key.decrypt(
        encrypted_session,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    # 发送加密后的数据到Student进程
    my_socket_1 = initial_socket()
    connect_accept(my_socket)
    # my_socket_1.send(encrypted_session.decode())


if __name__ == '__main__':
    main()
