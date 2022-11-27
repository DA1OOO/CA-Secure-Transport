# Blackboard服务端 端口3141
import socket

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
    str = c.recv(1024)
    dec_str = str.decode()
    print("Received msg: %s" % dec_str)
    # 关闭与客户端的连接
    c.close()
    print("---------Connect close------------")
    return str

if __name__ == '__main__':
    # 初始化socket
    my_socket = initial_socket()
    # 建立连接 保持监听
    tag = 1
    byte_msg = 0
    while True:
        byte_msg = connect_accept(my_socket, tag)
        tag += 1
        if tag == 2:
            break
