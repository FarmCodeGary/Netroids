import pygame

QUIT_EVENT = "QUIT"
LEFT_PRESSED_EVENT = "LEFT_PRESSED"
LEFT_RELEASED_EVENT = "LEFT_RELEASED"
RIGHT_PRESSED_EVENT = "RIGHT_PRESSED"
RIGHT_RELEASED_EVENT = "RIGHT_RELEASED"
UP_PRESSED_EVENT = "UP_PRESSED"
UP_RELEASED_EVENT = "UP_RELEASED"
DOWN_PRESSED_EVENT = "DOWN_PRESSED"
DOWN_RELEASED_EVENT = "DOWN_RELEASED"
SPACE_PRESSED_EVENT = "SPACE_PRESSED"
SPACE_RELEASED_EVENT = "SPACE_RELEASED"

COLOR_KEY = (64, 128, 128)  # Color used to indicate transparency

pygame.font.init()
pygame.display.init()

icon = pygame.image.load("media/asteroid1.png")
icon.set_colorkey(COLOR_KEY)
pygame.display.set_icon(icon)
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Netroids, by Garrison Benson")

_glyphs = {}

_glyphs["BLUESHIP"] = pygame.image.load("media/xwing_blue.png").convert()
_glyphs["BLUESHIP"].set_colorkey(COLOR_KEY)

_glyphs["YELLOWSHIP"] = pygame.image.load("media/naboo.png").convert()
_glyphs["YELLOWSHIP"].set_colorkey(COLOR_KEY)

_glyphs["REDSHIP"] = pygame.image.load("media/awing.png").convert()
_glyphs["REDSHIP"].set_colorkey(COLOR_KEY)

_glyphs["GREENSHIP"] = pygame.image.load("media/tie.png").convert()
_glyphs["GREENSHIP"].set_colorkey(COLOR_KEY)

_glyphs["ASTEROID1"] = pygame.image.load("media/asteroid1.png").convert()
_glyphs["ASTEROID1"].set_colorkey(COLOR_KEY)

_glyphs["ASTEROID2"] = pygame.image.load("media/asteroid2.png").convert()
_glyphs["ASTEROID2"].set_colorkey(COLOR_KEY)

_glyphs["LASER"] = pygame.image.load("media/laser.png").convert()
_glyphs["LASER"].set_colorkey(COLOR_KEY)

_glyphs["BACKGROUND"] = pygame.image.load("media/stars.jpg").convert()


class GUI:
    def __init__(self):
        self.eventHandlers = {}  # Maps event names to handlers
        self.clock = pygame.time.Clock()
        self.chatFont = pygame.font.Font(None, 24)

    def draw(self, dataModel):
        backgroundImage = _glyphs["BACKGROUND"]
        screen.blit(backgroundImage, (0, 0))
        for entity in dataModel.getEntities():
            originalImage = _glyphs[entity.glyph]
            rotatedImage = pygame.transform.rotate(
                originalImage, entity.rotation)
            halfWidth = rotatedImage.get_width() / 2.0
            halfHeight = rotatedImage.get_height() / 2.0
            screen.blit(rotatedImage, (
                int(entity.x - halfWidth), int(entity.y - halfHeight)))
        chatYCoord = 10
        for message in dataModel.getChatMessageStrings():
            textSurface = self.chatFont.render(message, False, (255, 255, 255))
            screen.blit(textSurface, (10, chatYCoord))
            chatYCoord += 24
        scoresYCoord = 600 - 24
        for color, scoreString in dataModel.getScoreStrings():
            textSurface = self.chatFont.render(scoreString, False, color)
            screen.blit(textSurface, (10, scoresYCoord))
            scoresYCoord -= 24
        pygame.display.update()

    def processEvents(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.callHandler(QUIT_EVENT)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.callHandler(QUIT_EVENT)
                elif event.key == pygame.K_UP:
                    self.callHandler(UP_PRESSED_EVENT)
                elif event.key == pygame.K_DOWN:
                    self.callHandler(DOWN_PRESSED_EVENT)
                elif event.key == pygame.K_LEFT:
                    self.callHandler(LEFT_PRESSED_EVENT)
                elif event.key == pygame.K_RIGHT:
                    self.callHandler(RIGHT_PRESSED_EVENT)
                elif event.key == pygame.K_SPACE:
                    self.callHandler(SPACE_PRESSED_EVENT)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    self.callHandler(UP_RELEASED_EVENT)
                elif event.key == pygame.K_DOWN:
                    self.callHandler(DOWN_RELEASED_EVENT)
                elif event.key == pygame.K_LEFT:
                    self.callHandler(LEFT_RELEASED_EVENT)
                elif event.key == pygame.K_RIGHT:
                    self.callHandler(RIGHT_RELEASED_EVENT)
                elif event.key == pygame.K_SPACE:
                    self.callHandler(SPACE_RELEASED_EVENT)

    def callHandler(self, eventType):
        handler = self.eventHandlers.get(eventType)
        if handler:
            handler()

    def setEventHandler(self, eventType, handler):
        self.eventHandlers[eventType] = handler

    def tick(self):
        self.clock.tick(25)
