from interface import (
    DOWN_PRESSED_EVENT, DOWN_RELEASED_EVENT, UP_PRESSED_EVENT,
    UP_RELEASED_EVENT, LEFT_PRESSED_EVENT, LEFT_RELEASED_EVENT,
    RIGHT_PRESSED_EVENT, RIGHT_RELEASED_EVENT, SPACE_PRESSED_EVENT,
    SPACE_RELEASED_EVENT)


class LocalPlayerManager:
    def __init__(self, gui):
        self.entityID = None
        self.downPressed = False
        self.upPressed = False
        self.leftPressed = False
        self.rightPressed = False
        self.spacePressed = False
        self.firedThisFrame = False
        gui.setEventHandler(DOWN_PRESSED_EVENT, self.onDownPressed)
        gui.setEventHandler(DOWN_RELEASED_EVENT, self.onDownReleased)
        gui.setEventHandler(UP_PRESSED_EVENT, self.onUpPressed)
        gui.setEventHandler(UP_RELEASED_EVENT, self.onUpReleased)
        gui.setEventHandler(LEFT_PRESSED_EVENT, self.onLeftPressed)
        gui.setEventHandler(LEFT_RELEASED_EVENT, self.onLeftReleased)
        gui.setEventHandler(RIGHT_PRESSED_EVENT, self.onRightPressed)
        gui.setEventHandler(RIGHT_RELEASED_EVENT, self.onRightReleased)
        gui.setEventHandler(SPACE_PRESSED_EVENT, self.onSpacePressed)
        gui.setEventHandler(SPACE_RELEASED_EVENT, self.onSpaceReleased)

    def setEntity(self, entityID):
        self.entityID = entityID

    def clearFiredThisFrame(self):
        self.firedThisFrame = False

    def onDownPressed(self):
        self.downPressed = True

    def onDownReleased(self):
        self.downPressed = False

    def onUpPressed(self):
        self.upPressed = True

    def onUpReleased(self):
        self.upPressed = False

    def onLeftPressed(self):
        self.leftPressed = True

    def onLeftReleased(self):
        self.leftPressed = False

    def onRightPressed(self):
        self.rightPressed = True

    def onRightReleased(self):
        self.rightPressed = False

    def onSpacePressed(self):
        self.spacePressed = True
        self.firedThisFrame = True

    def onSpaceReleased(self):
        self.spacePressed = False

    def getRotationStatus(self):
        if self.leftPressed and self.rightPressed:
            return "off"
        elif self.leftPressed:
            return "left"
        elif self.rightPressed:
            return "right"
        else:
            return "off"

    def getThrottleStatus(self):
        if self.upPressed and self.downPressed:
            return "off"
        elif self.upPressed:
            return "forward"
        elif self.downPressed:
            return "backward"
        else:
            return "off"

    def getShootingStatus(self):
        if self.spacePressed or self.firedThisFrame:
            return "on"
        else:
            return "off"

    def generateControlMessage(self):
        if self.entityID is None:
            return None
        else:
            # TODO: Replace with use of string.format
            return ("CONTROL\n"+str(self.entityID)+"\nThrottle:" +
                    self.getThrottleStatus()+"\nRotating:" +
                    self.getRotationStatus()+"\nShooting:" +
                    self.getShootingStatus())


class RemotePlayerManager:
    def __init__(self, ipAddress, name, color, ship):
        self.ipAddress = ipAddress
        self.name = name
        self.color = color
        self.ship = ship
        self.score = 0
        ship.playerManager = self
        self.timeLastHeardFrom = None

    def resetScore(self):
        self.score = 0
