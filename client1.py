import socket
import threading
import time
import sys


class ClientData:
    def __init__(self):
        self.serverSocket = None
        self.connectedToServer = False
        self.running = True
        self.incomingMessage = ""
        self.currentBackgroundThread = None
        self.currentReceiveThread = None
        self.currentSendThread = None

        self.host = ''
        self.port = 0


clientData = ClientData()
clientDataLock = threading.Lock()


# so using the same style from second year - initial 2 bytes of a message tell how many bytes the rest of the data is

def receiveThread(clientData):
    print("receiveThread running")

    while clientData.connectedToServer is True:
        try:
            data = clientData.serverSocket.recv(2)

            if len(data) == 0:
                # on OSX, 'closed' sockets send 0 bytes, so trap this
                raise socket.error

            size = int.from_bytes(data, byteorder='big')

            data = clientData.serverSocket.recv(size)

            if len(data) > 0:
                text = ""
                text += data.decode("utf-8")
                clientDataLock.acquire()
                clientData.incomingMessage += text
                clientDataLock.release()
                print(text)
            else:
                raise socket.error

        except socket.error:
            print("Server lost")
            clientData.connectedToServer = False
            clientData.serverSocket = None


def sendThread(clientData):
    print("send thread running")

    while clientData.connectedToServer is True:
        try:
            toSend = "wagwan my G this is a test" + str(time.time())
            data = bytes(toSend, 'utf-8')
            clientData.serverSocket.send(len(data).to_bytes(2, byteorder='big'))
            clientData.serverSocket.send(data)
            time.sleep(2000)

        except socket.error:
            print("Server lost")
            clientData.connectedToServer = False
            clientData.serverSocket = None


def backgroundThread(clientData):
    print("backgroundThread running")
    clientData.connectedToServer = False
    while (clientData.connectedToServer is False) and (clientData.running is True):
        try:
            if clientData.serverSocket is None:
                clientData.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                clientData.serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            if clientData.serverSocket is not None:
                clientData.serverSocket.connect((clientData.host, clientData.port))

            clientData.connectedToServer = True

            clientData.currentReceiveThread = threading.Thread(target=receiveThread, args=(clientData,))
            clientData.currentReceivethread.start()

            clientData.currentSendThread = threading.Thread(target=sendThread, args=(clientData,))
            clientData.currentSendthread.start()

        except socket.error:
            print("error")
            clientData.serverSocket = None
            clientDataLock.acquire()
            clientData.incomingMessage = "\nServer Lost/Unavailable"
            clientDataLock.release()


if __name__ == '__main__':
    clientData.host = 'localhost'
    clientData.port = 9000

    if len(sys.argv) > 1:
        clientData.host = sys.argv[1]

        if len(sys.argv) > 2:
            clientData.port = int(sys.argv[2])

    clientData.currentBackgroundThread = threading.Thread(target=backgroundThread, args=(clientData,))
    clientData.currentBackgroundThread.start()


# so order of business for clients right.
# first gotta connect to the server with sockets (bc that's all I know how to use rn)
# then gotta start sending player-simulated data such as location/direction/movement/shooting
# use time to track time message sent and time message received back
