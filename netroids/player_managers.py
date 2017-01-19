import mGUI


class LocalPlayerManager:
    def __init__(self, gui):
        self.entityID = None
        self.downPressed = False
        self.upPressed = False
        self.leftPressed = False
        self.rightPressed = False
        self.spacePressed = False
        self.firedThisFrame = False
        gui.setEventHandler(mGUI.DOWN_PRESSED_EVENT, self.onDownPressed)
        gui.setEventHandler(mGUI.DOWN_RELEASED_EVENT, self.onDownReleased)
        gui.setEventHandler(mGUI.UP_PRESSED_EVENT, self.onUpPressed)
        gui.setEventHandler(mGUI.UP_RELEASED_EVENT, self.onUpReleased)
        gui.setEventHandler(mGUI.LEFT_PRESSED_EVENT, self.onLeftPressed)
        gui.setEventHandler(mGUI.LEFT_RELEASED_EVENT, self.onLeftReleased)
        gui.setEventHandler(mGUI.RIGHT_PRESSED_EVENT, self.onRightPressed)
        gui.setEventHandler(mGUI.RIGHT_RELEASED_EVENT, self.onRightReleased)
        gui.setEventHandler(mGUI.SPACE_PRESSED_EVENT, self.onSpacePressed)
        gui.setEventHandler(mGUI.SPACE_RELEASED_EVENT, self.onSpaceReleased)

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
