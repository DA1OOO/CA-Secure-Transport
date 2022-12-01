# CUHK服务端 9335端口
import socket
from OpenSSL import crypto
from OpenSSL import SSL

CERT_FILE = "cuhk.cer"
KEY_FILE = "cuhk.key"


# 初始化Socket
def initial_socket():
    # 创建套接字
    try:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("=====> Create socket succeeded!")
    except socket.error as err:
        print("=====> Create socket failed!，error details: %s" % (err))
    # 套接字默认端口
    port = 9335
    # 监听本机上80端口的网络请求
    my_socket.bind(('127.0.0.1', port))
    # 切换套接字到监听模式，最多阻塞5笔请求
    my_socket.listen(5)
    print("=====> Socket listening...")
    return my_socket


# 接受客户端连接，并保持监听,同时想起发送reply_msg
def connect_accept(my_socket, tag, reply_msg='===> Thanks for your connect!'.encode()):
    # 与客户端建立连接。
    c, addr = my_socket.accept()
    # 向客户发送回复信息。编码以发送字节类型。
    c.send(reply_msg)
    recv_str = c.recv(1024)
    dec_str = recv_str.decode()
    print("Received msg: %s" % dec_str)
    # 关闭与客户端的连接
    c.close()
    return recv_str


def generate_root_ca():
    print('=====> Start generating root cert.')
    # create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 1024)
    # create a self-signed cert
    cert = crypto.X509()
    cert.get_subject().C = "CN"
    cert.get_subject().ST = "HongKong"
    cert.get_subject().L = "HongKong"
    cert.get_subject().O = "CUHK"
    cert.get_subject().OU = "CUHK-DA1YAYUAN"
    cert.get_subject().CN = "localhost"
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha1')

    # open(join(cert_dir, CERT_FILE), "wt").write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    with open(CERT_FILE, "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

    # open(join(cert_dir, KEY_FILE), "wt").write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
    with open(KEY_FILE, "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
    print("=====> cuhk.cer filepath: /%s " % CERT_FILE)
    print("=====> cuhk.key filepath: /%s " % KEY_FILE)
    return k


def generate_cer(req, issuer_cert, issuer_key, digest="sha256",
                 extensions=None, serial=0):
    cert = crypto.X509()
    cert.set_serial_number(serial)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)
    cert.set_issuer(issuer_cert.get_subject())
    cert.set_subject(req.get_subject())
    cert.set_pubkey(req.get_pubkey())

    if extensions:
        for ext in extensions:
            if callable(ext):
                ext = ext(cert)
            cert.add_extensions([ext])

    cert.sign(issuer_key, digest)

    return cert


def main():
    print('################ Step 0 ################')
    # 初始化socket
    my_socket = initial_socket()
    # 生成根证书
    key_pair = generate_root_ca()
    # 建立连接 保持监听
    tag = 1
    while True:
        byte_msg = connect_accept(my_socket, tag)
        tag += 1
        if tag == 3:
            break
    print('################ Step 2 ################')
    # csr请求反序列化
    csr_request = crypto.load_certificate_request(crypto.FILETYPE_PEM, byte_msg)
    print('=====> CSR Request Get.')
    # 从文件中读取根证书
    with open(CERT_FILE, "r") as f:
        root_cert = crypto.load_certificate(crypto.FILETYPE_PEM, f.read())
    # 从文件中读取私钥
    with open(KEY_FILE, "r") as f:
        root_pri_key = crypto.load_privatekey(crypto.FILETYPE_PEM, f.read())
    # 生成cert2
    csr_request.sign(key_pair, digest='sha256')
    cert2 = generate_cer(csr_request, root_cert, root_pri_key)
    print('=====> Cert 2 generated.')
    byte_cert2 = crypto.dump_certificate(crypto.FILETYPE_PEM, cert2)
    # 将cert2通过socket发送到Student进程
    connect_accept(my_socket, tag, byte_cert2)
    print('=====> Send Cert 2 to student.')


if __name__ == '__main__':
    main()
