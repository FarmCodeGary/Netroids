import math
import random
import time


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

    def destroys_asteroid(self):
        return False

    def destroys_ship(self):
        return False

    def destroys_bullet(self):
        return False


class Asteroid(Entity):
    def __init__(self, entityID, x, y):
        glyphNum = random.randint(1, 2)
        glyph = "ASTEROID"+str(glyphNum)
        # TODO: Use super()
        Entity.__init__(self, entityID, glyph, x, y)
        direction = random.randint(0, 359)
        speed = random.randint(1, 4)
        self.xSpeed = math.cos(direction) * speed
        self.ySpeed = -math.sin(direction) * speed
        self.rotation = random.randint(0, 359)
        self.rotationSpeed = random.randint(-4, 4)

    def handleCollision(self, otherEntity, server):
        if otherEntity.destroys_asteroid():
            server.removeEntity(self)
            # TODO: Fix this--only bullets have parent entities.
            server.onAsteroidDestroyed(otherEntity.parentEntity)
#        elif isinstance(otherEntity,Asteroid):
#            mySpeed = math.hypot(self.xSpeed, self.ySpeed)
#            angleBetween = math.atan2(self.y - otherEntity.y, self.x - otherEntity.x) + math.pi
#            myAngle = math.atan2(self.ySpeed, self.xSpeed)
#            diff = angleBetween - myAngle
#            newAngle = angleBetween + 2*diff
#            self.xSpeed = math.cos(newAngle) * mySpeed
#            self.ySpeed = math.sin(newAngle) * mySpeed
#            self.x += self.xSpeed
#            self.y += self.ySpeed
            # Bounce!

    def destroys_ship(self):
        return True

    def destroys_bullet(self):
        return True


class Spaceship(Entity):
    def __init__(self, entityID, glyph, x, y):
        # TODO: Use super()
        Entity.__init__(self, entityID, glyph, x, y)
        self.lastBulletTime = 0
        self.shooting = False
        self.radius = 10
        self.playerManager = None

    def thrustForward(self):
        self.accel = self.thrusterPower

    def thrustBackward(self):
        self.accel = -self.thrusterPower

    def turnOffThrusters(self):
        self.accel = 0

    def rotateLeft(self):
        self.rotationSpeed = 7

    def rotateRight(self):
        self.rotationSpeed = -7

    def stopRotation(self):
        self.rotationSpeed = 0

    def startShooting(self):
        self.shooting = True

    def stopShooting(self):
        self.shooting = False

    def act(self, currentTime, server):
        if self.shooting and (currentTime - self.lastBulletTime) > 0.5:
            self.lastBulletTime = currentTime
            server.spawnBullet(self.x, self.y, self.rotation, self)

    def handleCollision(self, otherEntity, server):
        if otherEntity.destroys_ship():
            server.onPlayerDeath(self)


class Bullet(Entity):
    def __init__(self, entityID, parentEntity, x, y, rotation):
        # TODO: Use super()
        Entity.__init__(self, entityID, "LASER", x, y)
        self.creationTime = time.time()
        self.parentEntity = parentEntity
        self.radius = 2
        self.rotation = rotation

    def act(self, currentTime, server):
        if (currentTime - self.creationTime) > 1.0:
            # Destroy the bullet.
            server.removeEntity(self)

    def handleCollision(self, otherEntity, server):
        if otherEntity.destroys_bullet():
            server.removeEntity(self)

    def destroys_asteroid(self):
        return True
