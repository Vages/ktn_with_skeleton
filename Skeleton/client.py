'''
KTN-project 2013 / 2014
'''
import socket
import json
from MessageWorker import ReceiveMessageWorker
from datetime import datetime

SERVERHOST = 'localhost'
SERVERPORT = 24601

class Client(object):

    def __init__(self):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, host, port):
        self.connection.connect((host, port))
        print '\nWelcome to KTN chat; your session is ready. \
            \n(Type "/help" and press enter for a list of commands.)\n'
        self.messageWorker = ReceiveMessageWorker(self, self.connection)
        self.messageWorker.start()
        while True:
            userInput = raw_input('')
            self.send(userInput)

    def printMessage(self, messageDict):
        print messageDict['username'] + " @ " + messageDict["timestamp"] + ": " + messageDict["message"]

    def message_received(self, message, connection):
        decodedMessage = json.loads(message)
        try:
            error = decodedMessage['error']
            print "SERVER ERROR: " + error
        except KeyError:
            response = decodedMessage['response']
            if response == 'login':
                print 'Successfully logged in as "%s"' % decodedMessage['username']
                # Some logic should be here and give the user the backlog of messages
            elif response == "logout":
                print 'Successfully logged out from "%s"' % decodedMessage['username']
            elif response == 'message':
                self.printMessage(decodedMessage)
            else:  
                print 'LOCAL ERROR: Server response not recognized'


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
                    if keyword == 'login':
                        try:
                            messageDict = {"request":"login", "username":splitData[1]}
                        except IndexError:
                            print "ERROR: No username found"
                            return
                    elif keyword == 'logout':
                        messageDict = {"request":"logout"}
                    elif keyword == 'help':
                        print '\nHELP:\n(1) Type "/login <your username>" and press enter to log in to the server. \
                            \n(2) Type "/logout" to log out of a chatting session\
                            \n(3) Type a normal message and press enter to send it to all other logged in clients.\n'
                        return
                    else:
                        print 'ERROR: Command not recognized. \n\tType "/help" for a list of available commands.'
                        return
                else:
                    print "ERROR: No keyword found"
                    return
            else:
                # Send a pure message
                timestamp = datetime.now().strftime("%H:%M:%S")
                messageDict = {"request":"message", "message":data, "timestamp":timestamp}

            requestAsJSON = json.dumps(messageDict)
            self.connection.sendall(requestAsJSON)

    def force_disconnect(self):
        pass
        #self.connection_closed(self.connection)


if __name__ == "__main__":
    client = Client()
    client.start(SERVERHOST, SERVERPORT)
