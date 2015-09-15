from __future__ import with_statement
import mMessagingService, mGUI, mLocalPlayerManager, math, time, threading

CONTROLMESSAGE = "CONTROL"
CONNECTREQUESTMESSAGE = "CONNECTREQUEST"
PINGMESSAGE = "PING"

DISCONNECTMESSAGE = "DISCONNECT"

SNAPSHOTMESSAGE = "SNAPSHOT"
CONNECTACCEPTMESSAGE = "CONNECTACCEPT"
PINGREPLYMESSAGE = "PINGREPLY"
CHATMESSAGE = "CHATCAST"

WRAP_PADDING = 16

class NetroidsBase:
    def __init__(self, localAddress, playerName):
        self.entityMap = {} # Maps IDs to entities
        self.messagingService = mMessagingService.MessagingService(localAddress)
        
        self.playerName = playerName
        self.messageHandlers = {} # Maps message types to callback methods
        self.worldWidth = 800 # TODO: Make this something the server sends to the client.
        self.worldHeight = 600
        self.gui = mGUI.GUI()
        self.localPlayerManager = mLocalPlayerManager.LocalPlayerManager(self.gui)
        #self.chatMessages = [("Hello, world!",5),("You smell!",3), ("Ha ha ha ha ha!",4)] # Queue of tuples of form (string, creationTime)
        self.chatMessages = []
        self.stuffToExecuteLater = [] # Queue of callables
        self.stuffToExecuteLaterLock = threading.Lock()
    
    # Returns a list of Entities
    def getEntities(self):
        return self.entityMap.values()
    
    def getChatMessageStrings(self):
        currentTime = time.time()
        return [message for message,creationTime in self.chatMessages if currentTime - creationTime < 10]
    
    def addEntity(self, entity):
        self.entityMap[entity.entityID] = entity
    
    def removeEntity(self, entity):
        if entity.entityID in self.entityMap:
            del self.entityMap[entity.entityID]
    
    def setMessageHandler(self, messageType, handler):
        if messageType in self.messageHandlers:
            raise Exception("Overwriting message handler for "+messageType)
        self.messageHandlers[messageType] = handler
    
    def handleMessage(self, message, address):
        lines = message.splitlines()
        handler = self.messageHandlers.get(lines[0])
        if handler:
            handler(message, address)
    
    def handleAllMessages(self):
        nextMessageTuple = self.messagingService.getNextMessage()
        while nextMessageTuple != None:
            message, address = nextMessageTuple
            self.handleMessage(message, address)
            nextMessageTuple = self.messagingService.getNextMessage()
            
    def updateEntityPositions(self):
        for entity in self.entityMap.values():
            entity.updatePosition(self.worldWidth, self.worldHeight, WRAP_PADDING)
    
    def executeLater(self,callable):
        with self.stuffToExecuteLaterLock:
            self.stuffToExecuteLater.append(callable)
    
    def executeStuff(self):
        with self.stuffToExecuteLaterLock:
            while len(self.stuffToExecuteLater) > 0:
                callable = self.stuffToExecuteLater.pop(0)
                callable()
    