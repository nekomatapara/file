#Client

import socket
import time
import statistics
import struct

SERVER_IP = str(input('输入服务器端IP: '))
SERVER_PORT = int(input('输入服务器端口号: '))
TIMEOUT = 0.1
NUM_REQUESTS = 12
startime = time.time()

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    client_socket.settimeout(0.1)

    seq_num = 1
    sent_packets = 0
    received_packets = 0

    rtt_times = []

    #一次握手
    print("正在建立连接")
    content = "000CONNECT".encode()
    client_socket.sendto(content, (SERVER_IP, SERVER_PORT))

    try:
        data, addr = client_socket.recvfrom(2048)
        #三次握手
        if "SUCCESS" in data.decode():
            print("服务器响应")
            content = "000CONNECT_SUCCESS".encode()
            client_socket.sendto(content, (SERVER_IP, SERVER_PORT))
            print("连接已建立。")
    except socket.timeout:
        print("连接超时。")
        exit()


    PACKET = f"!{2}s{1}s{2}s{200}s"

    while seq_num <= NUM_REQUESTS:
        Seq_num = struct.pack("!H", seq_num)
        Ver = b"\x02"
        content = "it is a message"
        Content = content.encode('utf-8')
        length = len(content)
        Length = struct.pack("!H", length)
        message = struct.pack(PACKET, Seq_num, Ver, Length, Content)



        for i in range(3):
            send_time = time.time()
            client_socket.sendto(message, (SERVER_IP, SERVER_PORT))
            sent_packets += 1
            try:
                data, client_address= client_socket.recvfrom(1024)
                response_time = time.time()
                Response_time = time.strftime("%H-%M-%S", time.localtime())
                if "Get" in data.decode():
                    #print(data.decode())
                    print(f"接收包, 时间: {Response_time}, 序号: {seq_num}")
                    received_packets += 1
                    rtt = (response_time - send_time) * 1000
                    rtt_times.append(rtt)
                    break
            except TimeoutError as e:
                print(f" Sequence {seq_num}, request timeout")
        time.sleep(0.5)
        seq_num += 1
    client_socket.settimeout(1)
    #一次挥手
    content = "000CLOSE".encode()
    client_socket.sendto(content, (SERVER_IP, SERVER_PORT))
    print("申请断开连接")
    data, client_address = client_socket.recvfrom(1024)
    if "OKCLOSE" in data.decode():
        print("收到断开确定")
        data, client_address = client_socket.recvfrom(1024)
        if "REALLYOKCLOSE" in data.decode():
            print("再次收到断开确定")
            #四次挥手
            content = "000FINILLYCLOSE".encode()
            client_socket.sendto(content, (SERVER_IP, SERVER_PORT))
            #结束
            finishtime = time.time()
            print("结束程序，关闭客户端")
            client_socket.close()





    loss_rate = (sent_packets - received_packets) / sent_packets * 100
    max_rtt = max(rtt_times)
    min_rtt = min(rtt_times)
    avg_rtt = statistics.mean(rtt_times)
    std_dev_rtt = statistics.stdev(rtt_times)
    retransmissions = finishtime - startime

    print("\n-------- Summary --------")
    print(f"Received UDP packets: {received_packets}")
    print(f"Packet loss rate: {loss_rate:.2f}%")
    print(f"Max RTT: {max_rtt:.2f}ms")
    print(f"Min RTT: {min_rtt:.2f}ms")
    print(f"Average RTT: {avg_rtt:.2f}ms")
    print(f"RTT Standard Deviation: {std_dev_rtt:.2f}ms")
    print(f"Number of retransmissions: {retransmissions}")


if __name__ == "__main__":
    main()