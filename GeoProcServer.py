"""
Сервер Обработки Геолокации
"""

import socket
import time
import hashlib
from datetime import datetime
from threading import Thread, Timer


class GeoProcServer:
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.SERVER_ADDRESS = (socket.gethostbyname(socket.gethostname()), 48888)
        self.limit = 1
        self.clients = 0
        self.clients_arr = []

    def start_server(self):
        """Запуск сервера"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.SERVER_ADDRESS)
        self.socket.listen(5)
        listen_for_connections = Thread(target=self.client_listener, daemon=True)
        listen_for_connections.start()
        listen_for_connections.join()

    def client_listener(self):
        """Запуск отдельного потока для прослушки подключения клиентов"""
        while True:
            try:
                conn, adr = self.socket.accept()
                if self.clients < self.limit:
                    self.clients_arr.append(conn)
                    print("Новый клиент подключен " + str(conn))
                    Thread(target=self.client_thread, args=(conn,)).start()
                    self.clients += 1
                else:
                    print("Превышен лимит пользователей")
                    conn.close()
            except OSError:
                pass

    def client_thread(self, conn):
        """
        Поток клиента
        Если получен правильный токен, не закрывает соединение
        Получает IMEI и координаты от клиента
        """

        def no_data():
            """Если нет данных, закрыть поток"""
            try:
                print(incoming_token)
                Thread(target=self.temp, args=(conn,)).start()
                if incoming_token != verification_token:
                    self.closed_connect(conn)
            except NameError:
                self.closed_connect(conn)

        verification_token = self.generate_time_token()
        Timer(2.0, no_data).start()
        try:
            in_data = conn.recv(1024)
            incoming_token = format(in_data.decode('utf8'))
            if incoming_token == verification_token:
                while True:
                    try:
                        data = conn.recv(1024)
                        msg = format(data.decode('utf8'))
                        print(msg)
                        # TODO тут обработка координат, imei и времени
                        if msg == "":
                            self.closed_connect(conn)
                            break
                    except ConnectionError:
                        self.closed_connect(conn)
                        break
            else:
                self.closed_connect(conn)
        except ConnectionAbortedError:
            self.closed_connect(conn)

    def temp(self, conn):
        print("send 1")
        self.send_msg(conn, "one")
        time.sleep(2)
        print("send 2")
        self.send_msg(conn, "two")

    def send_msg(self, conn, msg):
        """Отправка сообщения клиенту"""
        try:
            conn.send(bytes(str(msg), 'utf8'))
        except ConnectionError:
            self.closed_connect(conn)

    def closed_connect(self, conn):
        """Закрытие связи с клиентом"""
        i = 0
        while i < len(self.clients_arr):
            if self.clients_arr[i] == conn:
                print("Клиент отключен " + str(conn))
                conn.close()
                del self.clients_arr[i]
            i += 1
        self.clients -= 1

    def generate_time_token(self):
        date = datetime.today().strftime('%Y--%m%d')
        s = date + "$KonVi%"
        hashed = hashlib.md5()
        hashed.update(s.encode('utf-8'))
        return hashed.hexdigest()


if __name__ == '__main__':
    GeoProcServer().start_server()
    # GeoProcServer().generate_time_token()
