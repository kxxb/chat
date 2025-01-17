from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor


class Client(Protocol):
    ip: str = None
    login: str = None
    factory: 'Chat'

    def __init__(self, factory):
        """
        Инициализация фабрики клиента
        :param factory:
        """
        self.factory = factory

    def connectionMade(self):
        """
        Обработчик подключения нового клиента
        """
        self.ip = self.transport.getHost().host
        self.factory.clients.append(self)

        print(f"Client connected: {self.ip}")
        self.transport.write("Welcome to the chat v0.1\n".encode())

    def dataReceived(self, data: bytes):
        """
        Обработчик нового сообщения от клиента
        :param data:
        """
        message = data.decode().replace('\n', '')

        if self.login is not None:
            server_message = f"{self.login}: {message}"
            self.factory.notify_all_users(server_message)
            self.factory.history.append(server_message)
            print(server_message)
        else:
            if message.startswith("login:"):
                 new_login = message.replace("login:", "")
                 if (self.check_online(new_login) == 'new'):
                     self.login = new_login
                     notification = f"New user connected: {self.login}"
                     self.factory.notify_all_users(notification)
                     print(notification)
                     if len(self.factory.history) > 0:
                         for stored_message in self.factory.history:
                             self.transport.write(f"{stored_message}\n".encode())

                 else:
                     print(f"Error: Losgin {new_login} alredy online")
                     self.transport.write("exit\n".encode())

            else:
                print("Error: Invalid client login")

    def check_online(self, new_login):
        for online_user in self.factory.clients:
            if new_login == online_user.login:
                return 'online'
            else:
                return 'new'

    def connectionLost(self, reason=None):
        """
        Обработчик отключения клиента
        :param reason:
        """
        self.factory.clients.remove(self)
        print(f"Client disconnected: {self.ip}")


class Chat(Factory):
    clients: list
    history: list

    def __init__(self):
        """
        Инициализация сервера
        """
        self.clients = []
        self.history = []
        print("*" * 10, "\nStart server \nCompleted [OK]")

    def startFactory(self):
        """
        Запуск процесса ожидания новых клиентов
        :return:
        """
        print("\n\nStart listening for the clients...")

    def buildProtocol(self, addr):
        """
        Инициализация нового клиента
        :param addr:
        :return:
        """
        return Client(self)

    def notify_all_users(self, data: str):
        """
        Отправка сообщений всем текущим пользователям
        :param data:
        :return:
        """
        for user in self.clients:
            user.transport.write(f"{data}\n".encode())


if __name__ == '__main__':
    reactor.listenTCP(7410, Chat())
    reactor.run()
