import mEntity, time

class Bullet(mEntity.Entity):
    def __init__(self, entityID, parentEntity, x, y, rotation):
        mEntity.Entity.__init__(self, entityID, "LASER", x, y)
        self.creationTime = time.time()
        self.parentEntity = parentEntity
        self.radius = 2
        self.rotation = rotation
    
    def act(self, currentTime, server):
        if (currentTime - self.creationTime) > 1.0:
            # Destroy the bullet.
            server.removeEntity(self)
            
    def handleCollision(self,otherEntity,server):
        if isinstance(otherEntity,mAsteroid.Asteroid):
            server.removeEntity(self)

import mAsteroid