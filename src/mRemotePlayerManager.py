

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
    