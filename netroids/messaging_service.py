from __future__ import with_statement

import socket
import threading
import time


class MessagingService:
    def __init__(self, localAddress):
        # self.playerDict = {}  # Maps player names to addresses.
        self.messageQueue = []  # contains tuples of the form (message, address)
        self.receivedAcks = set()
        self.receivedAcksLock = threading.Lock()
        self.messagesLock = threading.Lock()
        self.listening = False
        self.udpStarted = False
        self.localAddress = localAddress
        self.nextImportantID = 1
        self.disconnectHandler = None
        self.importantIDs = {}  # Maps IP addresses to sets of importantIDs already received
        self.importantIDsLock = threading.Lock()

    def startListening(self):
        self.listening = True
        UdpListenThread = threading.Thread(target=self.listenOnUDP)
        UdpListenThread.start()
        while (not self.udpStarted):
            pass

    def stopListening(self):
        self.listening = False

    def getNextImportantID(self):
        retVal = self.nextImportantID
        self.nextImportantID += 1
        return retVal

    def sendMessage(self, message, recipientIPAddress, important=False):
        recipientAddress = (recipientIPAddress, 5005)
        if important:
            importantID = self.getNextImportantID()

            def threadCallable():
                self._sendImportantMessage(
                    message, recipientIPAddress, importantID)
            senderThread = threading.Thread(target=threadCallable)
            senderThread.start()
            # self._sendWholeMessage(wholeMessage, recipientIPAddress)
        else:
            wholeMessage = "N\n"+message
            self._sendWholeMessage(wholeMessage, recipientIPAddress)
            # print "Sent to "+str(recipientAddress)+" via UDP: "+message

    def _sendWholeMessage(self, wholeMessage, ipAddress):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(wholeMessage, (ipAddress, 5005))
        sock.close()

    def _sendImportantMessage(self, message, ipAddress, importantID):
        wholeMessage = "I"+str(importantID)+"\n"+message
        for i in range(5):
            self._sendWholeMessage(wholeMessage, ipAddress)
            time.sleep(2)
            with self.receivedAcksLock:
                if importantID in self.receivedAcks:
                    return
        if self.disconnectHandler:
            self.disconnectHandler(ipAddress)

    def acknowledgeMessage(self, message, ipAddress):
        lines = message.splitlines()
        importantID = lines[0][1:]
        reply = "R"+importantID
        self._sendWholeMessage(reply, ipAddress)

    # This should run on a separate thread:
    def listenOnUDP(self):
        listeningSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listeningSock.settimeout(0.2)  # 0.2 seconds, 200 ms
        listeningSock.bind((self.localAddress, 5005))
        self.udpStarted = True
        while self.listening:
            try:
                message, addressTuple = listeningSock.recvfrom(4096)
                ipAddress = addressTuple[0]
                # print "Received via UDP from "+str(addressTuple)+": "+str(message)
                parts = message.split("\n", 1)
                messageInfoLine = parts[0]
                if len(parts) > 1:
                    actualMessage = parts[1]
                else:
                    actualMessage = None
                if messageInfoLine[0] == "R":
                    importantID = int(messageInfoLine[1:])
                    with self.receivedAcksLock:
                        self.receivedAcks.add(importantID)
                else:
                    if messageInfoLine[0] == "I":
                        importantID = int(messageInfoLine[1:])
                        with self.importantIDsLock:
                            lastImportantIDSet = self.importantIDs.setdefault(
                                ipAddress, set())
                            if importantID not in lastImportantIDSet:
                                self._storeMessage(actualMessage, ipAddress)
                                lastImportantIDSet.add(importantID)
                        self.acknowledgeMessage(message, ipAddress)
                    else:
                        self._storeMessage(actualMessage, ipAddress)
            except socket.timeout:
                pass
        listeningSock.close()

    def _storeMessage(self, message, ipAddress):
        with self.messagesLock:
            self.messageQueue.append((message, ipAddress))

    def getNextMessage(self):
        with self.messagesLock:
            if self.messageQueue:
                return self.messageQueue.pop(0)
            else:
                return None

    def removeDataFor(self, ipAddress):
        with self.importantIDsLock:
            if ipAddress in self.importantIDs:
                del self.importantIDs[ipAddress]
