'''
KTN-project 2013 / 2014
Python daemon thread class for listening for events on
a socket and notifying a listener of new messages or
if the connection breaks.

A python thread object is started by calling the start()
method on the class. in order to make the thread do any
useful work, you have to override the run() method from
the Thread superclass. NB! DO NOT call the run() method
directly, this will cause the thread to block and suspend the
entire calling process' stack until the run() is finished.
it is the start() method that is responsible for actually
executing the run() method in a new thread.
'''
from threading import Thread


class ReceiveMessageWorker(Thread):

    def __init__(self, listener, connection):
    	Thread.__init__(self)
        self.daemon = True

        # Eirik: I interpret listener as the program that uses this listener,
        # and the connection as a socket
        self.listener = listener
        self.connection = connection

    def run(self):
    	# Continually listen for messages on the connected socket
    	while True:
	    	message = self.connection.recv(4096).strip()
	    	self.listener.message_received(message, self.connection)
