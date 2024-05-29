import socket
import threading
from db_helper import *
HOST = '0.0.0.0'  # 监听所有可用的接口
PORT = 8080  # 端口号import socket
BUFF_SIZE = 4096
SEP = '_@#sE!p_'

def server_run():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    print(f"等待客户端连接在 {HOST}:{PORT}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"客户端 {client_address} 已连接")
        task = threading.Thread(target=TCP_task, args=(client_socket,), name='tcp_task')
        task.start()

def send_response(client_socket):
    status_code = "200 OK"
    content_type = "text/html"
    content = "<html><body><p>hello world<p></body></html>"
    content_lenth=len(content)
    response = f"HTTP/1.1 {status_code}\r\nContent-Type: {content_type}\r\nContent-Length: {content_lenth}\r\n\r\n{content}"
    client_socket.send(response.encode('utf-8'))

def TCP_task(client_socket : socket.socket) -> None:

    isOK=False
    data_list, list_index = None, 0
    hello=True

    while True:
        try:
            # 接收客户端发送的数据
            data = client_socket.recv(BUFF_SIZE)
            data = data.decode('utf-8')
            print('receive >>>', data)

            # 发送一个简单的HTTP响应，表示OK
            # 不发的话会返回一个localhost didn’t send any data. ERR_EMPTY_RESPONSE
            # send_response(client_socket)

            if isOK==False:
                db_name, db_password, query = data.split(SEP)
                db_name += '.db'
                connection = connect_database(db_name, db_password)
                if connection==None:
                    client_socket.send('deny'.encode('utf-8'))
                    print('拒绝访问...')
                    raise Exception('数据库未打开, 可能密码错误...')
                else:
                    isOK=True
                    # 若是下载请求 先提前下载好数据便于后面传送数据
                    if query == 'download':
                        data_list, list_index = getAllMemo(connection), 0
                    client_socket.send('ok'.encode('utf-8'))


            else:
                if query == 'upload':
                    # 存入一条数据
                    success_message=InsertOneMemo(connection, data)
                    if success_message==True:
                        client_socket.send('ok'.encode('utf-8'))
                    else:
                        client_socket.send('failed'.encode('utf-8'))

                elif query == 'download':
                    # 通过next请求信号来不断传送数据
                    if data == 'next':
                        if list_index < len(data_list):
                            item = data_list[list_index]
                            # item[0]为主键id值 不用管
                            info = item[1] + SEP + item[2] + SEP + item[3]
                            print('get>>>>>'+info)
                            client_socket.send(info.encode('utf-8'))
                            list_index += 1
                        else:
                            print('download already succeed')
                            client_socket.send('finished'.encode('utf-8'))
                            client_socket.close()
                    else:
                        client_socket.send('deny'.encode('utf-8'))
                        client_socket.close()

            print('|-- done.')
        except Exception as e:
            print(f'{type(e)} {str(e)}\n')
            print('可能客户端链接断开...')
            client_socket.close()
            break



if __name__ == '__main__':
    server_run()