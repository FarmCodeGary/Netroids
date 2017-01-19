from interface import (
    DOWN_PRESSED_EVENT, DOWN_RELEASED_EVENT, UP_PRESSED_EVENT,
    UP_RELEASED_EVENT, LEFT_PRESSED_EVENT, LEFT_RELEASED_EVENT,
    RIGHT_PRESSED_EVENT, RIGHT_RELEASED_EVENT, SPACE_PRESSED_EVENT,
    SPACE_RELEASED_EVENT)


class LocalPlayerManager:
    def __init__(self, gui):
        self.entity_id = None
        self.down_pressed = False
        self.up_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.space_pressed = False
        self.fired_this_frame = False
        gui.set_event_handler(DOWN_PRESSED_EVENT, self.on_down_pressed)
        gui.set_event_handler(DOWN_RELEASED_EVENT, self.on_down_released)
        gui.set_event_handler(UP_PRESSED_EVENT, self.on_up_pressed)
        gui.set_event_handler(UP_RELEASED_EVENT, self.on_up_released)
        gui.set_event_handler(LEFT_PRESSED_EVENT, self.on_left_pressed)
        gui.set_event_handler(LEFT_RELEASED_EVENT, self.on_left_released)
        gui.set_event_handler(RIGHT_PRESSED_EVENT, self.on_right_pressed)
        gui.set_event_handler(RIGHT_RELEASED_EVENT, self.on_right_released)
        gui.set_event_handler(SPACE_PRESSED_EVENT, self.on_space_pressed)
        gui.set_event_handler(SPACE_RELEASED_EVENT, self.on_space_released)

    def set_entity(self, entity_id):
        self.entity_id = entity_id

    def clear_fired_this_frame(self):
        self.fired_this_frame = False

    def on_down_pressed(self):
        self.down_pressed = True

    def on_down_released(self):
        self.down_pressed = False

    def on_up_pressed(self):
        self.up_pressed = True

    def on_up_released(self):
        self.up_pressed = False

    def on_left_pressed(self):
        self.left_pressed = True

    def on_left_released(self):
        self.left_pressed = False

    def on_right_pressed(self):
        self.right_pressed = True

    def on_right_released(self):
        self.right_pressed = False

    def on_space_pressed(self):
        self.space_pressed = True
        self.fired_this_frame = True

    def on_space_released(self):
        self.space_pressed = False

    def get_rotation_status(self):
        if self.left_pressed and self.right_pressed:
            return "off"
        elif self.left_pressed:
            return "left"
        elif self.right_pressed:
            return "right"
        else:
            return "off"

    def get_throttle_status(self):
        if self.up_pressed and self.down_pressed:
            return "off"
        elif self.up_pressed:
            return "forward"
        elif self.down_pressed:
            return "backward"
        else:
            return "off"

    def get_shooting_status(self):
        if self.space_pressed or self.fired_this_frame:
            return "on"
        else:
            return "off"

    def generate_control_message(self):
        if self.entity_id is None:
            return None
        else:
            # TODO: Replace with use of string.format
            return ("CONTROL\n"+str(self.entity_id)+"\nThrottle:" +
                    self.get_throttle_status()+"\nRotating:" +
                    self.get_rotation_status()+"\nShooting:" +
                    self.get_shooting_status())


class RemotePlayerManager:
    def __init__(self, ip_address, name, color, ship):
        self.ip_address = ip_address
        self.name = name
        self.color = color
        self.ship = ship
        self.score = 0
        ship.player_manager = self
        self.time_last_heard_from = None

    def resetScore(self):
        self.score = 0
