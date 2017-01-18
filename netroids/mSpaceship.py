import mEntity


class Spaceship(mEntity.Entity):
    def __init__(self, entityID, glyph, x, y):
        mEntity.Entity.__init__(self, entityID, glyph, x, y)
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
        if isinstance(otherEntity, mAsteroid.Asteroid):
            server.onPlayerDeath(self)

# TODO: Remove circular dependency!
import mAsteroid
