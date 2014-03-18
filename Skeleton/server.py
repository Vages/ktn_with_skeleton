'''
KTN-project 2013 / 2014
Very simple server implementation that should serve as a basis
for implementing the chat server
'''
import SocketServer
import json
from threading import Thread
import re

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
        
        # New client set to not logged in
        self.loggedIn = False 
        while True:
            data = self.connection.recv(4096).strip()
            if data:
                decodedData = json.loads(data) # Decode data from JSON
                request = decodedData["request"] # Check user action
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
                        attemptedUsername = decodedData["username"]
                        if attemptedUsername in server.connectedClients: # Check if username already taken
                            errorMessage = {"response":"login", 'error':'Name already taken.', 'username':attemptedUsername}
                            self.sendMessage(json.dumps(errorMessage))
                        else:
                            if re.match("^[0-9A-Za-z_\-]{3,10}$", attemptedUsername):
                                # Username must be 3-10 chars long and consist of only alphanumeric characters
                                self.username = decodedData["username"]
                                self.loggedIn = True
                                self.server.addLoggedInClient(self) # Add client to server list of logged in clients
                                previousMessages = self.server.getMessageBackLog() # Get backlog
                                loginMessage = {"response":"login", "username":self.username, "messages":previousMessages}
                                self.sendMessage(json.dumps(loginMessage))
                            else:
                                errorMessage = {'response':'login', 'error':'Invalid username.\nMust be 3-10 characters long, alphanumeric with "_" or "-".', 'username':attemptedUsername}
                                self.sendmessage(json.dumps(errorMessage))
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
        # Sends a string to the connected client
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
        # Pushes a message to the log and sends it to all logged in cliens
        message.pop("request", None)
        message["response"] = "message" # Adds a server response header
        message["username"] = clientHandler.username # Stamps it with the current username
        self.log.append(message)
        jsonDump = json.dumps(message) # Generates a json dump to send to all logged in clients
        for client in self.connectedClients:
            client.sendMessage(jsonDump)

    def addLoggedInClient(self, clientHandler):
        # Adds a ClientHandler to the current list of logged in clients
        self.connectedClients.append(clientHandler)
        # TODO: Send a notification to all logged in clients
        notification = clientHandler.username + " has logged in"
        messageDict = {"response":"notification", "message":notification}
        for client in self.connectedClients:
            client.sendMessage(json.dumps(messageDict))


    def removeLoggedInClient(self, clientHandler):
        # Removes the current client handler from the list of logged in clients.
        # Used to clean up after logout
        self.connectedClients.remove(clientHandler)

    def getMessageBackLog(self):
        # Returns the last messages; max 20
        return self.log[-20:]

if __name__ == "__main__":
    # Create the server, binding it to the specified host and port
    HOST = 'localhost'
    PORT = 24601

    server = ThreadedTCPServer((HOST, PORT), ClientHandler)
    server.createClientListAndLog() #Sets up a list of active clients; kept out of the init

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print