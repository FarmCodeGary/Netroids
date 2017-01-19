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
        self.event_handlers = {}  # Maps event names to handlers
        self.clock = pygame.time.Clock()
        self.chat_font = pygame.font.Font(None, 24)

    def draw(self, data_model):
        background_image = _glyphs["BACKGROUND"]
        screen.blit(background_image, (0, 0))
        for entity in data_model.get_entities():
            original_image = _glyphs[entity.glyph]
            rotated_image = pygame.transform.rotate(
                original_image, entity.rotation)
            half_width = rotated_image.get_width() / 2.0
            half_height = rotated_image.get_height() / 2.0
            screen.blit(rotated_image, (
                int(entity.x - half_width), int(entity.y - half_height)))
        chat_y_coord = 10
        for message in data_model.get_chat_message_strings():
            text_surface = self.chat_font.render(message, False, (255, 255, 255))  # TODO: Use color constants.
            screen.blit(text_surface, (10, chat_y_coord))
            chat_y_coord += 24
        scores_y_coord = 600 - 24  # TODO: Use actual world/screen height.
        for color, score_string in data_model.get_score_strings():
            text_surface = self.chat_font.render(score_string, False, color)
            screen.blit(text_surface, (10, scores_y_coord))
            scores_y_coord -= 24
        pygame.display.update()

    def process_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.call_handler(QUIT_EVENT)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.call_handler(QUIT_EVENT)
                elif event.key == pygame.K_UP:
                    self.call_handler(UP_PRESSED_EVENT)
                elif event.key == pygame.K_DOWN:
                    self.call_handler(DOWN_PRESSED_EVENT)
                elif event.key == pygame.K_LEFT:
                    self.call_handler(LEFT_PRESSED_EVENT)
                elif event.key == pygame.K_RIGHT:
                    self.call_handler(RIGHT_PRESSED_EVENT)
                elif event.key == pygame.K_SPACE:
                    self.call_handler(SPACE_PRESSED_EVENT)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    self.call_handler(UP_RELEASED_EVENT)
                elif event.key == pygame.K_DOWN:
                    self.call_handler(DOWN_RELEASED_EVENT)
                elif event.key == pygame.K_LEFT:
                    self.call_handler(LEFT_RELEASED_EVENT)
                elif event.key == pygame.K_RIGHT:
                    self.call_handler(RIGHT_RELEASED_EVENT)
                elif event.key == pygame.K_SPACE:
                    self.call_handler(SPACE_RELEASED_EVENT)

    def call_handler(self, event_type):
        handler = self.event_handlers.get(event_type)
        if handler:
            handler()

    def set_event_handler(self, event_type, handler):
        self.event_handlers[event_type] = handler

    def tick(self):
        self.clock.tick(25)
