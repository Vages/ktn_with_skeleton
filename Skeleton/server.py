'''
KTN-project 2013 / 2014
Very simple server implementation that should serve as a basis
for implementing the chat server
'''
import SocketServer
from threading import Thread

'''
The RequestHandler class for our server.

It is instantiated once per connection to the server, and must
override the handle() method to implement communication to the
client.
'''


class ClientHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        # Get a reference to the socket object
        self.connection = self.request
        # Get the remote ip adress of the socket
        self.ip = self.client_address[0]
        # Get the remote port number of the socket
        self.port = self.client_address[1]
        print 'Client connected @' + self.ip + ':' + str(self.port)
        self.server.addClient(self)
        while True:
            data = self.connection.recv(4096).strip()
            if data:
                print data
                # Return the string in uppercase
                self.connection.sendall(data)
            else:
                print 'Client disconnected!'
                break

'''
This will make all Request handlers being called in its own thread.
Very important, otherwise only one client will be served at a time
'''

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):

    def createClientList(self):
        self.connectedClients = []

    def addClient(self, clientHandler):
        self.connectedClients.append(clientHandler)

    def removeClient(self, clientHandler):
        self.connectedClients.remove(clientHandler)

if __name__ == "__main__":
    HOST = 'localhost'
    PORT = 24602


    # Create the server, binding to localhost on port 9999
    server = ThreadedTCPServer((HOST, PORT), ClientHandler)
    server.createClientList()

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
