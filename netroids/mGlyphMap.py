import pygame

pygame.display.init()

__glyphMap = {}

__glyphMap["BLUESHIP"] = pygame.image.load("xwing_blue.png").convert()
__glyphMap["BLUESHIP"].set_colorkey((64,128,128))

__glyphMap["YELLOWSHIP"] = pygame.image.load("naboo.png").convert()
__glyphMap["YELLOWSHIP"].set_colorkey((64,128,128))

__glyphMap["REDSHIP"] = pygame.image.load("awing.png").convert()
__glyphMap["REDSHIP"].set_colorkey((64,128,128))

__glyphMap["GREENSHIP"] = pygame.image.load("tie.png").convert()
__glyphMap["GREENSHIP"].set_colorkey((64,128,128))

__glyphMap["ASTEROID1"] = pygame.image.load("asteroid1.png").convert()
__glyphMap["ASTEROID1"].set_colorkey((64,128,128))

__glyphMap["ASTEROID2"] = pygame.image.load("asteroid2.png").convert()
__glyphMap["ASTEROID2"].set_colorkey((64,128,128))

__glyphMap["LASER"] = pygame.image.load("laser.png").convert()
__glyphMap["LASER"].set_colorkey((64,128,128))

__glyphMap["BACKGROUND"] = pygame.image.load("stars.jpg").convert()


def getImage(glyph):
    return __glyphMap.get(glyph)
