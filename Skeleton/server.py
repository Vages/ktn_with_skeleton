'''
KTN-project 2013 / 2014
Very simple server implementation that should serve as a basis
for implementing the chat server
'''
import SocketServer
import json
from threading import Thread


HOST = 'localhost'
PORT = 24601

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
        self.loggedIn = False
        while True:
            data = self.connection.recv(4096).strip()
            if data:
                decodedData = json.loads(data) # decodes the data to Json. Here comes the fun.
                request = decodedData["request"]
                if self.loggedIn:
                    if request == "login":
                        errorMessage = {'response':'login', 'error':'Already logged in'}
                        self.sendMessage(json.dumps(errorMessage))
                    elif request == "logout":
                        pass
                    elif request == "message":
                        self.server.broadcastMessage(decodedData, self)
                else:
                    if request == "login":
                        self.username = decodedData["username"]
                        self.loggedIn = True
                        self.server.addLoggedInClient(self)
                        loginMessage = {"response":"login", "username":self.username}
                        self.sendMessage(json.dumps(loginMessage))
                    elif request == "logout":
                        errorMessage = {"response":"logout", "error":"Not logged in!"}
                        self.sendMessage(json.dumps(errorMessage))
                    elif request == "message":
                        errorMessage = {"response":"message", "error":"You have to log in before sending a message."}
                        self.sendMessage(json.dumps(errorMessage))
            else:
                print 'Client disconnected!'
                break

    def sendMessage(self, message):
        self.connection.sendall(message)

'''
This will make all Request handlers being called in its own thread.
Very important, otherwise only one client will be served at a time
'''

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):

    def createClientListAndLog(self):
        self.connectedClients = []
        self.log = []

    def broadcastMessage(self, message, clientHandler):
        message.pop("request", None)
        message["response"] = "message"
        message["username"] = clientHandler.username
        self.log.append(message)
        jsonDump = json.dumps(message)
        for client in self.connectedClients:
            client.sendMessage(jsonDump)

    def addLoggedInClient(self, clientHandler):
        self.connectedClients.append(clientHandler)
        notification = clientHandler.username + " has logged in"


    def removeLoggedInClient(self, clientHandler):
        self.connectedClients.remove(clientHandler)

if __name__ == "__main__":


    # Create the server, binding to localhost on port 9999
    server = ThreadedTCPServer((HOST, PORT), ClientHandler)
    server.createClientListAndLog()

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print