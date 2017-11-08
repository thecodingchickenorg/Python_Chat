#!/usr/bin/python
import socket
import select
import sys
import os
from threading import Thread
def binery(string):
    """Convert """
    result =  tuple(' '.join(format(ord(x), 'b') for x in string).split())
    result=string.encode()
    return result
def b(string):return string.encode()
def d(Bytes):return Bytes.decode()
class ChatClient:
    """run with the following commands
cd C:\\Users\\Joshua Bowe\\Downloads\\python code downloaded\\Chapter 16
python PythonChatClient.py 127.0.0.1 20000 joshb"""
    def __init__(self, host, port, nickname):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.input = self.socket.makefile('rb', 0)
        self.output = self.socket.makefile('wb', 0)

        #Send the given nickname to the server.
        authenticationDemand = self.input.readline()
        print(d(authenticationDemand))
        if not authenticationDemand[:12]==binery("Who are you?"):
            raise Exception ("This doesn't seem to be a Python Chat Server.")
        self.output.write(b(nickname + '\r\n'))
        response = self.input.readline().strip()
##        print(response,type(response))##Testing
        if not d(response).startswith("Hello"):
            raise Exception (response)
        print(d(response))

        #Start out by printing out the list of members.
        self.output.write(b'/names\r\n')
        print("Currently in the chat room:  \n\t", d(self.input.readline().strip()))

        self.run()

    def run(self):
        """Start a separate thread to gather the input from the
        keyboard even as we wait for messages to come over the
        network. This makes it possible for the user to simultaneously
        send and receive chat text."""
        
        propagateStandardInput = self.PropagateStandardInput(self.output)
        propagateStandardInput.start()

        #Read from the network and print everything received to standard
        #output. Once data stops coming in from the network, it means
        #we've disconnected.
        inputText = True
        while inputText:
            inputText = self.input.readline()
            if inputText:
                print(d(inputText.strip()))
        propagateStandardInput.done = True

    class PropagateStandardInput(Thread):
        """A class that mirrors standard input to the chat server
        until it's told to stop."""

        def __init__(self, output):
            """Make this thread a daemon thread, so that if the Python
            interpreter needs to quit it won't be held up waiting for this
            thread to die."""
            Thread.__init__(self)
            self.setDaemon(True)
            self.output = output
            self.done = False

        def run(self):
            "Echo standard input to the chat server until told to stop."
            while not self.done:
                inputText = sys.stdin.readline().strip()
                if inputText:
                    self.output.write(b(inputText + '\r\n'))

if __name__ == '__main__':
    import sys
    #See if the user has an OS-provided 'username' we can use as a default 
    #chat nickname. If not, they have to specify a nickname.
    try:
        import pwd
        defaultNickname = pwd.getpwuid(os.getuid())[0]
    except ImportError:
        defaultNickname = None

    if len(sys.argv) < 3 or not defaultNickname and len(sys.argv) < 4:
        print('Usage: %s [hostname] [port number] [username]' % sys.argv[0])
        sys.exit(1)

    hostname = sys.argv[1]
    port = int(sys.argv[2])

    if len(sys.argv) > 3:
        nickname = sys.argv[3]
    else:
        #We must be on a system with usernames, or we would have
        #exited earlier.
        nickname = defaultNickname

    ChatClient(hostname, port, nickname)
##    josh = ChatClient('127.0.0.1',20000,'joshb')
