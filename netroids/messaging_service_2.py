from __future__ import with_statement

import socket
import threading


class MessagingService:
    def __init__(self, localAddress):
        # self.playerDict = {}  # Maps player names to addresses.
        self.messageQueue = []  # contains tuples of the form (message, address)
        self.messagesLock = threading.Lock()
        self.listening = False
        self.udpStarted = False
        self.tcpStarted = False
        self.localAddress = localAddress

    def startListening(self):
        self.listening = True
        UdpListenThread = threading.Thread(target=self.listenOnUDP)
        UdpListenThread.start()
        TcpListenThread = threading.Thread(target=self.listenOnTCP)
        TcpListenThread.start()
        while (not self.udpStarted) and (not self.tcpStarted):
            pass

    def stopListening(self):
        self.listening = False

    def sendMessage(self, message, recipientIPAddress, important=False):
        recipientAddress = (recipientIPAddress, 5005)
        important = False
        if important:
            wholeMessage = "I\n"+message
            # print "Attempting to connect to "+str(recipientAddress)
            # sock = socket.create_connection(recipientAddress)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(recipientAddress)
            sock.send(message)
            sock.close()
            # print "Sent to "+str(recipientAddress)+" via TCP: "+message
        else:
            wholeMessage = "N\n"+message
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(message, recipientAddress)
            sock.close()
            # print "Sent to "+str(recipientAddress)+" via UDP: "+message

    def definitelySendMessage(self):
        for i in range(5):
            pass

    # This should run on a separate thread:
    def listenOnUDP(self):
        listeningSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listeningSock.settimeout(0.2)  # 0.2 seconds, 200 ms
        listeningSock.bind((self.localAddress, 5005))
        self.udpStarted = True
        print "Starting to listen for UDP messages to "+self.localAddress+"..."
        while self.listening:
            try:
                message, addressTuple = listeningSock.recvfrom(4096)
                ipAddress = addressTuple[0]
                # print "Received via UDP from "+str(addressTuple)+": "+str(message)
                with self.messagesLock:
                    self.messageQueue.append((message, ipAddress))
            except socket.timeout:
                pass
        listeningSock.close()
        print "Done listening for UDP messages."

    # This too:
    def listenOnTCP(self):
        listeningSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # listeningSock.settimeout(1) # 0.2 seconds, 200 ms
        listeningSock.bind((self.localAddress, 5005))
        listeningSock.listen(2)
        self.tcpStarted = True
        print "Starting to listen for TCP messages to "+self.localAddress+"..."
        while self.listening:
            try:
                connSock, addressTuple = listeningSock.accept()
                ipAddress = addressTuple[0]
                while True:
                    message = connSock.recv(4096)
                    if not message:  # The socket is closed
                        break
                    else:
                        # print "Received via TCP from "+str(addressTuple)+": "+str(message)
                        with self.messagesLock:
                            self.messageQueue.append((message, ipAddress))
                connSock.close()
            except socket.timeout:
                pass
        listeningSock.close()
        print "Done listening for TCP messages."

    def getNextMessage(self):
        with self.messagesLock:
            if self.messageQueue:
                return self.messageQueue.pop(0)
            else:
                return None
