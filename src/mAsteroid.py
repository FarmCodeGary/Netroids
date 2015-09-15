import mEntity, random, math

class Asteroid(mEntity.Entity):
    def __init__(self, entityID, x, y):
        glyphNum = random.randint(1,2)
        glyph = "ASTEROID"+str(glyphNum)
        mEntity.Entity.__init__(self, entityID, glyph, x, y)
        direction = random.randint(0,359)
        speed = random.randint(1,4)
        self.xSpeed = math.cos(direction) * speed
        self.ySpeed = -math.sin(direction) * speed
        self.rotation = random.randint(0,359)
        self.rotationSpeed = random.randint(-4,4)
        
    
    def handleCollision(self,otherEntity,server):
        if isinstance(otherEntity,mBullet.Bullet):
            server.removeEntity(self)
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

import mBullet