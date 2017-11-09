#!/usr/bin/python
# Run with cd C:\Users\Joshua Bowe\Downloads\python code downloaded\Chapter 16
#Then do py PythonChatServer.py 127.0.0.1 20000
# or py -3 PythonChatServer.py 127.0.0.1 8000
import socketserver
import re
import socket
import socketserver as SocketServer
import os
#####STARTING LOG FILE#########
import time##import time, so you can create the log file for the day
foo=time.asctime().split(' ')
l=[foo[4], foo[1], foo[2]]
def make_log_name(l):
    """you take in a list.  It contains the year, month, and day in that order.  It
returns a nicely formatted name"""
    f="%s_%s-%s"%(l[0],l[1],l[2])
    f=f.replace(':',';')
    print(f)
    return f
filen=os.path.join('logs',make_log_name(l))
bar=open(filen,'a')
bar.write("Started server at \"%s\"\n"%time.asctime())
bar.close()
print("Wrote to log file %s"%filen)
def write_text(text):
    bar=open(filen,'a')
    bar.write(text)
    bar.close()
    del bar
def write_p(text,p=0):
    if p==1:print(text)
    write_text(text)
del foo,l,make_log_name,bar

#############END LOG FILE SECTION
def b(string):return string.encode()
def d(Bytes):return Bytes.decode()
def join(S,it):
    foo=""
    it=list(it)
    for i in range(len(it)-1):
        foo+="%s%s"%(d(it[i]),S)
    foo+='%s'%d(it[-1])
    return foo
##users={'joshb':'Woof!!!','bowej':'!!!fooW'}##Testing
##print(join(', ',users.keys()))##Testing
class ClientError(Exception):
    "An exception thrown because the client gave bad input to the server."
    pass

class PythonChatServer(socketserver.ThreadingTCPServer):
    "The server class."

    def __init__(self, server_address, RequestHandlerClass):
        """Set up an initially empty mapping between a user's nickname
        and the file-like object used to send data to that user."""
        SocketServer.ThreadingTCPServer.__init__(self, server_address,
                                                 RequestHandlerClass)
        self.users = {}

class RequestHandler(SocketServer.StreamRequestHandler):
    """Handles the life cycle of a user's connection to the chat
    server: connecting, chatting, running server commands, and
    disconnecting."""

    NICKNAME = re.compile('^[A-Za-z0-9_-]+$') #Regex for a valid nickname

    def handle(self):
        """Handles a connection: gets the user's nickname, then
        processes input from the user until they quit or drop the
        connection."""
        self.nickname = None

        self.privateMessage('Who are you?')
        nickname = self._readline()
        done = False
        try:
            self.nickCommand(nickname)
            self.privateMessage('Hello %s, welcome to the Python Chat Server.'\
                                % d(nickname))
            self.broadcast('%s has joined the chat.' % d(nickname), False)
        except ClientError as error:
            self.privateMessage(error.args[0])        
            done = True
        except socket.error:
            done = True
##        print("\"%s\" has logged in."%d(self.nickname))
        write_p("\"%s\" has logged in.\n"%d(self.nickname),1)
        #Now they're logged in; let them chat.
        while not done:
            try:
                done = self.processInput()
            except ClientError as error:
                self.privateMessage(str(error))
            except socket.error as e:
                done = True

    def finish(self):                        
        "Automatically called when handle() is done."
        if self.nickname:
            #The user successfully connected before disconnecting. 
            #Broadcast that they're quitting to everyone else.
            message = '%s has quit.' % d(self.nickname)
            if hasattr(self, 'partingWords'):
                message = '%s has quit: %s' % (d(self.nickname),
                                               self.partingWords)
            self.broadcast(message, False)

            #Remove the user from the list so we don't keep trying to
            #send them messages.
            if self.server.users.get(self.nickname):
                write_p("\"%s\" has quit.\n"%d(self.nickname),1)
                del(self.server.users[self.nickname])
        self.request.shutdown(2)
        self.request.close()

    def processInput(self):
        """Reads a line from the socket input and either runs it as a
        command, or broadcasts it as chat text."""
        done = False
        l = self._readline()
        command, arg = self._parseCommand(l)
        if command:
            done = command(arg)
        else:
            l = '<%s> %s\n' % (d(self.nickname), d(l))
            write_p("To all: %s"%l)
            self.broadcast(l)
        return done
    #Each server command is implemented as a method. The _parseCommand method, defined later, takes a line that looks like /nick and calls the corresponding method (in this case, nickCommand):
    #Below are implementations of the server commands.

    def nickCommand(self, nickname):
        """Attempts to change a user's nickname.

The new(and not working code is below
if not nickname:
            raise ClientError ('No nickname provided.')
##        print(self.NICKNAME,type(self.NICKNAME),'\n',
##              nickname,type(nickname))#Testing
        if type(nickname)==str:nickname.encode()
        if type(nickname)==bytes:
            if not self.NICKNAME.match(d(nickname)):
                raise ClientError ('Invalid nickname: %s' % nickname)
        elif type(nickname)==str:
            if not self.NICKNAME.match(nickname):
                raise ClientError ('Invalid nickname: %s' % nickname)
        if nickname == self.nickname:
            raise ClientError ('You are already known as %s.' % nickname)
        if self.server.users.get(nickname, None):
            raise ClientError ('There\'s already a user named "%s" here.' % nickname)
        oldNickname = None
        if self.nickname:
            oldNickname = self.nickname
            del(self.server.users[self.nickname])
        self.server.users[nickname] = self.wfile
        self.nickname = nickname
        if oldNickname:"""
        if not nickname:
            raise ClientError ('No nickname provided.')
        if type(nickname)==str:
            nickname=b(nickname)
        if not self.NICKNAME.match(d(nickname)):
            raise ClientError ('Invalid nickname: %s' % nickname)
        if nickname == self.nickname:
            raise ClientError ('You are already known as %s.' % nickname)
        if self.server.users.get(nickname, None):
            raise ClientError ('There\'s already a user named "%s" here.' % nickname)
        oldNickname = None
        if self.nickname:
            oldNickname = self.nickname
            del(self.server.users[self.nickname])
        self.server.users[nickname] = self.wfile
        self.nickname = nickname
        if oldNickname:
            self.broadcast('%s is now known as %s' % (d(oldNickname),
                                                      d(self.nickname)))
    def quitCommand(self, partingWords):
        """Tells the other users that this user has quit, then makes
        sure the handler will close this connection."""
        if partingWords:
            self.partingWords = partingWords
        #Returning True makes sure the user will be disconnected.
        return True

    def namesCommand(self, ignored):
        "Returns a list of the users in this chat room."
        user_list=join(', ',self.server.users.keys())
        self.privateMessage(user_list)
    def msgCommand(self,nickAndMsg):
        "Send a private message to another user"
        if type(nickAndMsg)==None or type(nickAndMsg)==type(None):
            self.privateMessage("No input given")
            return
        if len(nickAndMsg)==0:
            self.privateMessage("No input given")
            return
        if not ' ' in nickAndMsg:
            self.privateMessage("No message given, use a space ' ' to give one")
            return
        nick,msg=nickAndMsg.split(' ',1)
        if nick==self.nickname:
            self.privateMessage("What, send a message to yourself?")
            return
        user = self.server.users.get(b(nick))
##        print(user,nick,self.server,self.server.users)
        if not user:
            self.privateMessage("No such user: '%s'"%nick)
            return
        msg="[Private from %s] %s\r\n"%(d(self.nickname),msg)
        write_p(msg)
##        write_p("%s:%s"%(user,type(user)),1)
        user.write(b(msg))
        return
    # Below are helper methods.
    
    def broadcast(self, message, includeThisUser=True):
        """Send a message to every connected user, possibly exempting the
        user who's the cause of the message."""
        message = self._ensureNewline(message)
        for user, output in self.server.users.items():
            if includeThisUser or user != self.nickname:
                output.write(b(message))

    def privateMessage(self, message):
        "Send a private message to this user."
        n=self._ensureNewline(message).encode()
        self.wfile.write(n)

    def _readline(self):
        "Reads a line, removing any whitespace."
        return self.rfile.readline().strip()

    def _ensureNewline(self, s):
        "Makes sure a string ends in a newline."
        if s and s[-1] != '\n':
            s += '\r\n'
        return s

    def _parseCommand(self, i):
        """Try to parse a string as a command to the server. If it's an
        implemented command, run the corresponding method."""
        i=d(i)
        commandMethod, arg = None, None
        if i and i[0] == '/':
            if len(i) < 2:
                raise ClientError( 'Invalid command: "%s"' % i)
            commandAndArg = i[1:].split(' ', 1)
            if len(commandAndArg) == 2:
                command, arg = commandAndArg
            else:
                command, = commandAndArg
            commandMethod = getattr(self, command + 'Command', None)
            if not commandMethod:
                raise ClientError( 'No such command: "%s"' % command)
        return commandMethod, arg

if __name__ == '__main__':
    import sys
##    sys.argv.append('127.0.0.1');sys.argv.append('27272')
    if len(sys.argv) < 3:
        print('Usage: %s [hostname] [port number]' % sys.argv[0])
        sys.exit(1)
    hostname = sys.argv[1]
    port = int(sys.argv[2])
    PythonChatServer((hostname, port), RequestHandler).serve_forever()
