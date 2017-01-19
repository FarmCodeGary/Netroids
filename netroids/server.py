import time
import random
import math

from entities import Spaceship, Asteroid, Bullet
import engine
from interface import QUIT_EVENT
from player_managers import RemotePlayerManager


class Server(engine.NetroidsEngine):
    def __init__(self, localAddress, playerName):
        engine.NetroidsEngine.__init__(self, localAddress, playerName)

        self.playerLookPool = []
        self.playerLookPool.append(("BLUESHIP", (0, 0, 255)))
        self.playerLookPool.append(("REDSHIP", (255, 0, 0)))
        self.playerLookPool.append(("GREENSHIP", (0, 255, 0)))
        self.playerLookPool.append(("YELLOWSHIP", (255, 242, 0)))

        self.asteroidsPerRound = 15
        self.nextSnapshotNumber = 1
        self.nextEntityID = 1
        self.playerMap = {}  # Maps addresses to RemotePlayerManagers.
        self.firstRound = True

        localPlayerLook = random.choice(self.playerLookPool)
        self.playerLookPool.remove(localPlayerLook)
        glyph, color = localPlayerLook
        self.localPlayerShip = Spaceship(
            self.getNextEntityID(), glyph, 400, 300)
        self.localPlayer = RemotePlayerManager(
            None, self.playerName, color, self.localPlayerShip)
        self.addEntity(self.localPlayerShip)
        self.finished = False
        self.setMessageHandler(
            engine.CONTROLMESSAGE, self.handleControlMessage)
        self.setMessageHandler(
            engine.CONNECTREQUESTMESSAGE, self.handleConnectRequest)
        self.setMessageHandler(engine.PINGMESSAGE, self.handlePing)
        self.gui.setEventHandler(QUIT_EVENT, self.endGame)
        self.messagingService.disconnectHandler = self.onAddressDisconnected
        self.setMessageHandler(
            engine.DISCONNECTMESSAGE, self.handleDisconnectMessage)

    def addPlayer(self, address, name):
        look = random.choice(self.playerLookPool)
        self.playerLookPool.remove(look)
        glyph, color = look
        playerShip = Spaceship(
            self.getNextEntityID(), glyph, 400, 300)
        self.resetShipPosition(playerShip)
        self.addEntity(playerShip)
        playerManager = RemotePlayerManager(address, name, color, playerShip)
        playerManager.timeLastHeardFrom = time.time()
        self.playerMap[address] = playerManager
        reply = "CONNECTACCEPT\n"+str(playerShip.entityID)
        self.messagingService.sendMessage(reply, address, True)
        self.broadcastChatMessage(name+" joined the game.", (255, 255, 255))

    def removePlayer(self, address):
        playerManager = self.playerMap[address]
        playerShip = playerManager.ship
        glyph = playerShip.glyph
        color = playerManager.color
        self.removeEntity(playerShip)
        del self.playerMap[address]
        self.messagingService.removeDataFor(address)
        self.playerLookPool.append((glyph, color))  # "Replenish" the pool

    def getAllPlayers(self):
        return self.playerMap.values() + [self.localPlayer]

    def getScoreStrings(self):
        return [(p.color, p.name+": "+str(p.score))
                for p in self.getAllPlayers()]

    def getNextEntityID(self):
        retVal = self.nextEntityID
        self.nextEntityID += 1
        return retVal

    def onAddressDisconnected(self, address):
        def doLater():
            remotePlayerManager = self.playerMap.get(address)
            if remotePlayerManager:
                self.broadcastChatMessage(
                    remotePlayerManager.name+" left the game.",
                    (255, 255, 255))
                self.removePlayer(address)
        self.executeLater(doLater)

    def onPlayerDeath(self, playerShip):
        playerManager = playerShip.playerManager
        playerManager.score -= 3
        self.resetShipPosition(playerShip)

    def resetShipPosition(self, ship):
        placed = False
        while not placed:
            ship.x = random.randint(
                engine.WRAP_PADDING,
                self.worldWidth - engine.WRAP_PADDING)
            ship.y = random.randint(
                engine.WRAP_PADDING,
                self.worldHeight - engine.WRAP_PADDING)
            placed = not self.testForCollision(ship)
        ship.xSpeed = 0
        ship.ySpeed = 0
        ship.rotation = random.randint(0, 359)

    def startRound(self):
        for i in range(self.asteroidsPerRound):
            placed = False
            asteroid = Asteroid(self.getNextEntityID(), 0, 0)
            while not placed:
                asteroid.x = random.randint(0, self.worldWidth)
                asteroid.y = random.randint(0, self.worldHeight)
                placed = not self.testForCollision(asteroid)  # True if there was no collision
            self.addEntity(asteroid)
        topScore = None
        winningPlayers = []
        for playerManager in self.getAllPlayers():
            self.resetShipPosition(playerManager.ship)
            if topScore is None or playerManager.score > topScore:
                topScore = playerManager.score
                winningPlayers = [playerManager]
            elif playerManager.score == topScore:
                winningPlayers.append(playerManager)
            playerManager.resetScore()
        if self.firstRound:
            self.firstRound = False
        else:
            self.broadcastWinners(winningPlayers, topScore)
        self.broadcastChatMessage("New round starting!", (255, 255, 255))

    def broadcastWinners(self, winningPlayers, topScore):
        if len(winningPlayers) == 1:
            winningPlayer = winningPlayers[0]

            # TODO: Replace with use of string.format.
            message = winningPlayer.name + " wins the round with "+str(topScore)+" points!"
        else:
            # TODO: Replace with use of string.format.
            names = " and ".join([winningPlayer.name for winningPlayer in winningPlayers])
            message = names + " win the round with "+str(topScore)+" points!"
        self.broadcastChatMessage(message, (255, 255, 255))

    def onAsteroidDestroyed(self, playerShipEntity):
        playerManager = playerShipEntity.playerManager
        playerManager.score += 1
        self.checkAsteroids()

    def checkAsteroids(self):
        asteroidsLeft = False
        for entity in self.entityMap.values():
            if isinstance(entity, Asteroid):
                asteroidsLeft = True
                break
        if not asteroidsLeft:
            self.startRound()

    def handleControlMessage(self, message, address):
        lines = message.splitlines()
        entityID = int(lines[1])
        entity = self.entityMap[entityID]
        for line in lines[2:]:
            if line.startswith("Throttle:"):
                thrustDir = line.split(":")[1].strip()
            elif line.startswith("Rotating:"):
                rotation = line.split(":")[1].strip()
            elif line.startswith("Shooting:"):
                shooting = line.split(":")[1].strip()
        self.updateShip(entityID, thrustDir, rotation, shooting)
        playerManager = self.playerMap[address]
        playerManager.timeLastHeardFrom = time.time()

    def handleConnectRequest(self, message, address):
        lines = message.splitlines()
        playerName = lines[1]
        self.addPlayer(address, playerName)

    def handleDisconnectMessage(self, message, address):
        self.onAddressDisconnected(address)

    def handleChatSend(self, message, address):
        playerManager = self.playerMap[address]
        lines = message.splitlines()
        chatMessage = playerManager.name+": "+lines[1]
        self.broadcastChatMessage(chatMessage, playerManager.color)

    def handlePing(self, message, address):
        lines = message.splitlines()
        reply = "PINGREPLY\n"+lines[1]
        self.messagingService.sendMessage(reply, address, False)

    def sendSnapshot(self):
        # TODO: Replace with use of string.format.
        message = "SNAPSHOT\n"+str(self.nextSnapshotNumber)
        for playerManager in self.getAllPlayers():
            colorString = ",".join([str(comp) for comp in playerManager.color])
            message += "\n"+colorString+"|"+playerManager.name+": "+str(playerManager.score)
        message += "\n"
        for entity in self.getEntities():
            message += "\n"+entity.createSnapshotLine()
        for playerAddress in self.playerMap.keys():
            self.messagingService.sendMessage(message, playerAddress, False)
        self.nextSnapshotNumber += 1

    def endGame(self):
        for ipAddress in self.playerMap.keys():
            self.messagingService.sendMessage("DISCONNECT", ipAddress, False)
        self.finished = True

    def updatePlayerShip(self):
        throttleStatus = self.localPlayerManager.getThrottleStatus()
        rotationStatus = self.localPlayerManager.getRotationStatus()
        shootingStatus = self.localPlayerManager.getShootingStatus()
        self.updateShip(
            self.localPlayerShip.entityID,
            throttleStatus, rotationStatus, shootingStatus)

    def updateShip(
            self, entityID, throttleStatus, rotationStatus, shootingStatus):
        ship = self.entityMap[entityID]
        if throttleStatus == "forward":
            ship.thrustForward()
        elif throttleStatus == "backward":
            ship.thrustBackward()
        elif throttleStatus == "off":
            ship.turnOffThrusters()
        elif throttleStatus is None:
            pass
        else:
            raise Exception("Invalid Throttle value")

        if rotationStatus == "left":
            ship.rotateLeft()
        elif rotationStatus == "right":
            ship.rotateRight()
        elif rotationStatus == "off":
            ship.stopRotation()
        elif rotationStatus is None:
            pass
        else:
            raise Exception("Invalid Rotating value")

        if shootingStatus == "on":
            ship.startShooting()
        elif shootingStatus == "off":
            ship.stopShooting()
        elif shootingStatus is None:
            pass
        else:
            raise Exception("Invalid shooting status")

    def letEntitiesAct(self):
        currentTime = time.time()
        for entity in self.entityMap.values():
            entity.act(currentTime, self)

    def handleCollisions(self):
        entities = self.entityMap.values()
        for i, entity1 in enumerate(entities):
            for entity2 in entities[(i+1):]:
                if entity1.testForCollision(entity2):
                    entity1.handleCollision(entity2, self)
                    entity2.handleCollision(entity1, self)

    def testForCollision(self, entity):
        for otherEntity in self.entityMap.values():
            if otherEntity != entity and entity.testForCollision(otherEntity):
                return True
        return False

    def spawnBullet(self, x, y, direction, parentEntity):
        bullet = Bullet(self.getNextEntityID(), parentEntity, x, y, direction)
        radians = math.radians(direction)
        bullet.xSpeed = math.cos(radians) * 15
        bullet.ySpeed = -math.sin(radians) * 15
        self.addEntity(bullet)

    def broadcastChatMessage(self, message, color):
        colorString = ",".join([str(comp) for comp in color])
        for playerAddress in self.playerMap.keys():
            self.messagingService.sendMessage(
                "CHATCAST\n"+colorString+"\n"+message, playerAddress, True)
        self.chatMessages.append((message, time.time()))

    def checkForDisconnections(self, currentTime):
        for remotePlayerManager in self.playerMap.values():
            if currentTime - remotePlayerManager.timeLastHeardFrom > 10.0:
                self.onAddressDisconnected(remotePlayerManager.ipAddress)

    def go(self):
        self.messagingService.startListening()
        self.startRound()
        lastSnapshotTime = 0
        lastDisconnectCheckTime = 0
        while not self.finished:
            currentTime = time.time()
            self.handleAllMessages()
            if currentTime - lastDisconnectCheckTime > 1.0:
                self.checkForDisconnections(currentTime)
            self.executeStuff()
            self.gui.processEvents()
            self.localPlayerManager.clearFiredThisFrame()  # Todo: Make this cleaner
            self.updatePlayerShip()
            self.updateEntityPositions()
            self.letEntitiesAct()
            if (currentTime - lastSnapshotTime) > 0.05:
                self.sendSnapshot()
                lastSnapshotTime = currentTime
            self.gui.draw(self)
            self.gui.tick()
            self.handleCollisions()
        self.messagingService.stopListening()
