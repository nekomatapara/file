#server

import socket
import random
import time

SERVER_IP = '0.0.0.0'
SERVER_PORT = int(input('输入服务器端口号: '))
LOSS_RATE = 0.3


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        server_socket.bind((SERVER_IP, SERVER_PORT))
    except OSError as e:
        print(f"Error binding socket: {e}")
        return
    print("Server完成初始化,IP为：",SERVER_IP,",端口为",SERVER_PORT,",等待客户端连接")

    while True:
        data, client_addr = server_socket.recvfrom(1024)
        print("获得连接请求")
        #二次握手
        if "CONNECT" in data.decode():
            print("已成功收到", client_addr, "的消息")
            content = "000SUCCESS".encode()
            server_socket.sendto(content, client_addr)
            data, client_addr = server_socket.recvfrom(1024)
            if "CONNECT_SUCCESS" in data.decode():
                print("已建立与", client_addr, "的连接")
                break
        else:
            print("未成功建立连接")

    while True:
        data, client_addr = server_socket.recvfrom(1024)
        if random.random() > LOSS_RATE:
            seq = int.from_bytes(data[:2], byteorder='big')
            ver = int.from_bytes(data[2:3], byteorder='big')
            len = int.from_bytes(data[3:5], byteorder='big')
            con = data[5:5 + len].decode('utf-8')
            server_time = time.strftime("%H-%M-%S", time.localtime())

            #二次挥手
            if "CLOSE" in data.decode():
                print("收到断开请求")
                print("发送断开请求")
                content = "000OKCLOSE".encode()
                server_socket.sendto(content, client_addr)
                # 三次挥手
                print("再次发送断开请求")
                content = "000REALLYOKCLOSE".encode()
                server_socket.sendto(content, client_addr)
                data, client_addr = server_socket.recvfrom(1024)
                if "FINILLYCLOSE" in data.decode():
                    server_socket.close()
                    print("收到确认断开确定，结束程序，关闭服务器")
                    break
            else:
                print(f"收到包, 时间: {server_time}, IP：{client_addr[0]}, 序号: {seq}, 版本：{ver}, 内容：{con}")
                response = str(seq)+str(ver)+"3"+"Get"
                server_socket.sendto(response.encode(), client_addr)
                #print(response)


if __name__ == "__main__":
    main()