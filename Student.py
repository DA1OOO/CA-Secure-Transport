## Student客户端
import socket
import pickle
from OpenSSL import crypto
from OpenSSL import SSL

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
    sid = input("===> Enter your student ID: ")
    # 数据校验
    while len(sid) != 10 or (sid.isdecimal() is not True):
        sid = input("===> Error input! Please input again: ")
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


if __name__ == '__main__':
    # 发送SID到CUHK
    sid = '1234567890'
    my_sokect = connect_port(9335)
    my_sokect.send(sid.encode())
    print(my_sokect.recv(1024).decode())
    my_sokect.close()

    key_pair = generate_key_pair(TYPE_RSA, 1024)
    csr_request = generate_crs_request(pkey=key_pair)

    # 序列化x509req 并发送到CUHK
    byte_csr_request = crypto.dump_certificate_request(crypto.FILETYPE_PEM, csr_request)
    my_sokect_1 = connect_port(9335)
    my_sokect_1.send(byte_csr_request)
    print(my_sokect_1.recv(1024).decode())
    my_sokect_1.close()

    # 通过socket从CUHK获取cert2
    my_sokect_2 = connect_port(9335)
    byte_cert2 = my_sokect_2.recv(4096)
    cert2 = crypto.load_certificate(crypto.FILETYPE_PEM, byte_cert2)
    print('===> Get Cert2!')
    print('===> SID:', sid, 'sign finished!')

    # 初始化request 并发送到Blackboard [SID, cert2]
    my_sokect_3 = connect_port(3141)
    my_sokect_3.send('e'.encode())
