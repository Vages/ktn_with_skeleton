'''
KTN-project 2013 / 2014
'''
import socket
import json
from MessageWorker import ReceiveMessageWorker

SERVERHOST = 'localhost'
SERVERPORT = 24602

class Client(object):

    def __init__(self):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, host, port):
        self.connection.connect((host, port))
        self.messageWorker = ReceiveMessageWorker(self, self.connection)
        self.messageWorker.start()
        while True:
            userInput = raw_input('')
            self.send(userInput)

    def message_received(self, message, connection):
        print message

    def connection_closed(self, connection):
        self.connected = False

    def send(self, data):
        # check that data is not empty
        if data != '':
            # A slash indicates that the program starts with a command            
            if data[0] == '/':
                # The data has a command
                if len(data) > 1:
                    
                    data = data [1:] # Strips the string of the slash
                    splitData = data.split(' ', 1) # splits out the command
                    keyword = splitData[0].lower()
                    arguments = splitData[1]
                    
                    if keyword == 'login':
                        messageDict = {"request":"login", "username":arguments}
                    elif keyword == 'logout':
                        messageDict = {"request":"logout"}
                else:
                    print "ERROR: No keyword found"
                    return
            else:
                # Send a pure message
                messageDict = {"request":"message", "message":data}

            requestAsJSON = json.dumps(messageDict)
            self.connection.sendall(requestAsJSON)

    def force_disconnect(self):
        pass
        #self.connection_closed(self.connection)


if __name__ == "__main__":
    client = Client()
    client.start(SERVERHOST, SERVERPORT)
