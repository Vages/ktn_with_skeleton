'''
KTN-project 2013 / 2014
'''
import socket
import json
from MessageWorker import ReceiveMessageWorker
from datetime import datetime


"""Hei, jeg er en mann"""

class Client(object):
    """
    A client that connects to a server with the specified protocol.
    """

    def __init__(self, host, port):
        """Initializes a client object.

        :param host: Server host
        :param port: Server port
        :return: Client object
        """
        self.chat_running = True
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((host, port))
        self.message_worker = ReceiveMessageWorker(self, self.connection)
        self.message_worker.start()
        print '\nWelcome to KTN chat; you may now login with "/login <your username>". \
            \n(Type "/help" and press enter for a list of commands.)\n'

        while self.chat_running:
            user_input = raw_input('')
            self.send(user_input)

    def print_message(self, message_dict):
        """Prints a received message.

        :param message_dict: The message in dict form
        :return:
        """
        # Print received message with timestamp
        print message_dict['username'] + " @ " + message_dict["timestamp"] + ": " + message_dict["message"]

    def message_received(self, message, connection):
        """Method called by message worker to print a received message

        :param message: Message in JSON format
        :param connection: The socket that is connected
        :return:
        """
        decoded_message = json.loads(message)
        try:
            error = decoded_message['error']  # Print an error if present
            print "SERVER ERROR: " + error
        except KeyError:
            response = decoded_message['response']  # Determine action from service response
            if response == 'login':
                # print 'Successfully logged in as "%s"' % decoded_message['username']
                for message in decoded_message["messages"]:
                    self.print_message(message)
            elif response == "logout":
                print 'Successfully logged out from "%s"' % decoded_message['username']
                
            elif response == 'message':
                self.print_message(decoded_message)
            elif response == 'notification':
                self.print_notification(decoded_message)
            else:  
                print 'LOCAL ERROR: Server response not recognized'

    def print_notification(self, message_dict):
        """Prints a response of the notification type.

        :param message_dict: The message in dict form
        :return:
        """
        print message_dict["message"]

    def connection_closed(self, connection):
        """Does the cleanup when connection closes.

        :param connection:
        :return:
        """
        self.connected = False

    def send(self, data):
        """Sends a user message.

        :param data:
        :return:
        """
        
        if data != '':  # Check if data is empty

            if data[0] == '/':  # Data is a command

                if len(data) > 1:  # Check if command keyword is present
                    
                    data = data[1:]  # Strip the string of the slash
                    split_data = data.split(' ', 1)  # Split the keyword from potential arguments
                    keyword = split_data[0].lower()
                    if keyword == 'login':
                        try:
                            request_dict = {"request": "login", "username": split_data[1]}
                        except IndexError:
                            print "ERROR: No username found"
                            return
                    elif keyword == 'logout':
                        request_dict = {"request":"logout"}
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
                timestamp = datetime.now().strftime("%H:%M:%S")  # Create timestamp for message
                request_dict = {"request": "message", "message": data, "timestamp": timestamp}

            request_as_json = json.dumps(request_dict)
            self.connection.sendall(request_as_json)

    def force_disconnect(self):
        pass
        #self.connection_closed(self.connection)


"""Dette er selve programmet"""

if __name__ == "__main__":
    SERVER_HOST = 'localhost'
    SERVER_PORT = 24601
    client = Client(SERVER_HOST, SERVER_PORT)
