import mNetroidsBase, mEntity, mGUI, sys, time

class Client(mNetroidsBase.NetroidsBase):
    def __init__(self, localAddress, serverAddress, playerName):
        mNetroidsBase.NetroidsBase.__init__(self, localAddress, playerName)
        self.lastSnapshotNumber = -1
        self.lastSnapshotTime = None
        self.lastPingNumber = 0
        self.lastPingTime = 0
        self.rtts = [] # RTTs for last 30 seconds
        self.avgRTT = 0 # Average RTT over last 30 seconds
        self.serverAddress = serverAddress
        self.snapshotReceived = False
        self.finished = False
        self.scoreStrings = []
        self.setMessageHandler(mNetroidsBase.CONNECTACCEPTMESSAGE, self.handleConnectAcceptMessage)
        self.setMessageHandler(mNetroidsBase.SNAPSHOTMESSAGE, self.handleSnapshotMessage)
        self.setMessageHandler(mNetroidsBase.CHATMESSAGE, self.handleChatCast)
        self.setMessageHandler(mNetroidsBase.PINGREPLYMESSAGE, self.handlePingReply)
        self.setMessageHandler(mNetroidsBase.DISCONNECTMESSAGE, self.handleDisconnectMessage)
        self.gui.setEventHandler(mGUI.QUIT_EVENT, self.quit)
    
    def getScoreStrings(self):
        return self.scoreStrings
        #return [(p.color,p.name+": "+str(p.score)) for p in self.getAllPlayers()]
    
    def handleConnectAcceptMessage(self, message, address):
        lines = message.splitlines()
        entityID = int(lines[1].strip())
        self.localPlayerManager.setEntity(entityID)
        self.lastSnapshotTime = time.time()
        
    def handleChatCast(self,message, address):
        lines = message.splitlines()
        color = tuple([int(comp) for comp in lines[1].split(",")])
        chatMessage = lines[2]
        self.chatMessages.append((chatMessage,time.time()))
    
    def handleSnapshotMessage(self, message, address):
        # TODO: Add position extrapolation (after it works without it!)
        lines = message.splitlines()
        snapshotNumber = int(lines[1])
        self.lastSnapshotTime = time.time()
        if snapshotNumber > self.lastSnapshotNumber:
            self.snapshotReceived = True
            self.lastSnapshotNumber = snapshotNumber
            self.entityMap.clear()
            self.scoreStrings = []
            i = 2
            while True:
                line = lines[i]
                i += 1
                if line == "":
                    break
                else:
                    parts = line.split("|")
                    color = tuple([int(comp) for comp in parts[0].split(",")])
                    scoreString = parts[1]
                    self.scoreStrings.append((color,scoreString))
            
            for line in lines[i:]:
                entity = mEntity.createFromSnapshotLine(line)
                self.addEntity(entity)
    
    def handlePingReply(self, message, address):
        lines = message.splitlines()
        pingNumber = int(lines[1])
        if pingNumber == self.lastPingNumber:
            rtt = time.time() - self.lastPingTime
            if self.rtts:
                self.rtts.pop(0) # Remove first item.
            self.rtts.append(rtt)
            self.avgRTT = sum(self.rtts) / len(self.rtts)
    
    def handleDisconnectMessage(self, message, address):
        self.onAddressDisconnected(None)
    
    def sendConnectRequest(self):
        self.lastSnapshotTime = time.time()
        self.messagingService.sendMessage("CONNECTREQUEST\n"+self.playerName, self.serverAddress, True)
    
    def sendControlUpdate(self):
        message = self.localPlayerManager.generateControlMessage()
        self.localPlayerManager.clearFiredThisFrame()
        if message: # message will be none if we are not actually connected
            self.messagingService.sendMessage(message, self.serverAddress, False)
    
    def sendPing(self):
        self.lastPingNumber += 1
        message = "PING\n"+str(self.lastPingNumber)
        self.messagingService.sendMessage(message, self.serverAddress, False)
        self.lastPingTime = time.time()
    
    def checkForDisconnection(self,currentTime):
        if currentTime - self.lastSnapshotTime > 10:
            # Disconnected!
            self.onAddressDisconnected(None)
    
    def onAddressDisconnected(self,address):
        print "Connection to server lost!"
        self.quit()
    
    def quit(self):
        self.messagingService.sendMessage("DISCONNECT", self.serverAddress, False)
        self.finished = True
    
    def go(self):
        self.messagingService.startListening()
        self.sendConnectRequest()
        lastUpdateTime = 0
        lastDisconnectCheckTime = time.time()
        while not self.finished:
            currentTime = time.time()
            self.snapshotReceived = False
            self.handleAllMessages()
            if not self.snapshotReceived: # Add this in later to increase smoothness of motion.
                self.updateEntityPositions()
            if currentTime - lastDisconnectCheckTime > 1.0:
                self.checkForDisconnection(currentTime)
            self.executeStuff()
            self.gui.processEvents()
            if (currentTime - lastUpdateTime) > 0.1:
                self.sendControlUpdate()
                lastUpdateTime = currentTime
            if (currentTime - self.lastPingTime) > 1.0:
                self.sendPing()
            self.gui.draw(self)
            self.gui.tick()
        self.messagingService.stopListening()
    