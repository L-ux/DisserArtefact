import socket
import threading
import time
import sys

host = ''
port = 0

clientIndex = 0
currentClients = {}
currentClientsLock = threading.Lock()


class Player:
    def __init__(self, ID):
        self.ID = ID


def sendString(socket, message):
    data = bytes(message, 'utf-8')
    try:
        if socket.send(len(data).to_bytes(2, byteorder='big')) == 0:
            raise socket.error

        if socket.send(data) == 0:
            raise socket.error

    except socket.error:
        return False

    return True


def handleNewClient(client_socket):
    global clientIndex

    clientID = str(clientIndex)
    clientIndex += 1

    currentClientsLock.acquire()
    currentClients[client_socket] = Player(clientID)
    currentClientsLock.release()

    print('Player ' + clientID + ' has joined')

    sendString(client_socket, 'connected with ID: ' + clientID)

    thread = threading.Thread(target=clientRecieve, args=(client_socket,))
    thread.start()


def acceptClientsThread(server_socket):
    print('acceptThread running')
    while True:
        (clientSocket, address) = server_socket.accept()


def main():
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    global host, port

    host = 'localhost'
    port = 9000

    if len(sys.argv) > 1:
        host = sys.argv[1]

        if len(sys.argv) > 2:
            port = int(sys.argv[2])

    try:
        serverSocket.bind((host, port))
    except socket.error as err:
        print('Can\'t start server, is another instance running?')
        print(format(err))
        exit()

    print(host + ':' + str(port))

    serverSocket.listen(4)

    thread = threading.Thread(target=acceptClientsThread, args=(serverSocket,))
    thread.start()


if __name__ == '__main__':
    main()
