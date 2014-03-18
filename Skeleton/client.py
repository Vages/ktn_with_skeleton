'''
KTN-project 2013 / 2014
'''
import socket
import json
from MessageWorker import ReceiveMessageWorker
from datetime import datetime

class Client(object):

    def __init__(self):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, host, port):
        self.chatRunning = True
        self.connection.connect((host, port))
        self.messageWorker = ReceiveMessageWorker(self, self.connection)
        self.messageWorker.start()

        # Give user welcome message
        print '\nWelcome to KTN chat; you may now login with "/login <your username>". \
            \n(Type "/help" and press enter for a list of commands.)\n'
        
        while self.chatRunning:
            userInput = raw_input('')
            self.send(userInput)

    def printMessage(self, messageDict):
        # Print received message with timestamp
        print messageDict['username'] + " @ " + messageDict["timestamp"] + ": " + messageDict["message"]

    def message_received(self, message, connection):
        decodedMessage = json.loads(message)
        try:
            error = decodedMessage['error'] # Print an error if present
            print "SERVER ERROR: " + error
        except KeyError:
            response = decodedMessage['response'] # Determine action from service response
            if response == 'login':
                # print 'Successfully logged in as "%s"' % decodedMessage['username']
                for message in decodedMessage["messages"]:
                    self.printMessage(message)
            elif response == "logout":
                print 'Successfully logged out from "%s"' % decodedMessage['username']
                
            elif response == 'message':
                self.printMessage(decodedMessage)
            elif response == 'notification':
                self.print_notification(decodedMessage)
            else:  
                print 'LOCAL ERROR: Server response not recognized'

    def print_notification(self, messageDict):
        print messageDict["message"]

    def connection_closed(self, connection):
        self.connected = False

    def send(self, data):
        
        if data != '': # Check if data is empty

            if data[0] == '/': # Data is a command

                if len(data) > 1: # Check if command keyword is present
                    
                    data = data [1:] # Strip the string of the slash
                    splitData = data.split(' ', 1) # Split the keyword from potential arguments
                    keyword = splitData[0].lower()
                    if keyword == 'login':
                        try:
                            requestDict = {"request":"login", "username":splitData[1]}
                        except IndexError:
                            print "ERROR: No username found"
                            return
                    elif keyword == 'logout':
                        requestDict = {"request":"logout"}
                    elif keyword == 'help':
                        print '\nHELP:\n(1) Type "/login <your username>" and press enter to log in to the server.\
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
                timestamp = datetime.now().strftime("%H:%M:%S") # Create timestamp for message
                requestDict = {"request":"message", "message":data, "timestamp":timestamp}

            requestAsJSON = json.dumps(requestDict)
            self.connection.sendall(requestAsJSON)

    def force_disconnect(self):
        pass
        #self.connection_closed(self.connection)


if __name__ == "__main__":
    SERVERHOST = 'localhost'
    SERVERPORT = 24601
    client = Client()
    client.start(SERVERHOST, SERVERPORT)
