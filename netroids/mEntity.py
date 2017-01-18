import math


def createFromSnapshotLine(line):
    parts = line.split()
    entityID = int(parts[0])
    entity = Entity(entityID)
    entity.glyph = parts[1]
    entity.x = float(parts[2])
    entity.y = float(parts[3])
    entity.xSpeed = float(parts[4])
    entity.ySpeed = float(parts[5])
    entity.rotation = float(parts[6])
    # entity.rotationSpeed = float(parts[7])
    entity.rotationSpeed = 0
    return entity


class Entity:
    def __init__(self, entityID, glyph=None, x=0, y=0):
        # These values are sent in SNAPSHOTs
        self.entityID = entityID
        self.glyph = glyph
        self.x = x
        self.y = y
        self.xSpeed = 0
        self.ySpeed = 0
        self.accel = 0  # Acceleration in the current direction
        self.rotation = 0
        self.rotationSpeed = 0
        self.maxSpeed = 15
        self.radius = 16

        # These are not sent in SNAPSHOTs:
        self.thrusterPower = 0.5

    def createSnapshotLine(self):
        # TODO: Replace with use of string.format.
        return (str(self.entityID)+" "+self.glyph+" "+str(self.x)+" " +
                str(self.y)+" "+str(self.xSpeed)+" "+str(self.ySpeed)+" " +
                str(self.rotation)+" "+str(self.rotationSpeed))

    def updatePosition(self, worldWidth, worldHeight, wrapPadding):
        radians = math.radians(self.rotation)
        xAccel = math.cos(radians) * self.accel
        yAccel = -math.sin(radians) * self.accel

        self.xSpeed = self.xSpeed + xAccel
        self.ySpeed = self.ySpeed + yAccel

        speed = math.hypot(self.xSpeed, self.ySpeed)
        if speed > self.maxSpeed:
            ratio = self.maxSpeed / speed
            self.xSpeed = self.xSpeed * ratio
            self.ySpeed = self.ySpeed * ratio

        self.x = self.x + self.xSpeed
        self.y = self.y + self.ySpeed

        if self.x > worldWidth + wrapPadding:
            self.x -= (worldWidth + wrapPadding*2)
        elif self.x < -wrapPadding:
            self.x += (worldWidth + wrapPadding*2)
        if self.y > worldHeight + wrapPadding:
            self.y -= (worldHeight + wrapPadding*2)
        elif self.y < -wrapPadding:
            self.y += (worldHeight + wrapPadding*2)

        # May want to move this to be the first thing processed:
        self.rotation = self.rotation + self.rotationSpeed

    def testForCollision(self, otherEntity):
        distance = math.hypot(otherEntity.x - self.x, otherEntity.y - self.y)
        return distance < (self.radius + otherEntity.radius)

    def handleCollision(self, otherEntity, server):
        pass

    def act(self, currentTime, server):
        pass
