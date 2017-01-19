import math
import random
import time


def entity_from_snapshot_line(line):
    parts = line.split()
    entity_id = int(parts[0])
    entity = Entity(entity_id)
    entity.glyph = parts[1]
    entity.x = float(parts[2])
    entity.y = float(parts[3])
    entity.x_speed = float(parts[4])
    entity.y_speed = float(parts[5])
    entity.rotation = float(parts[6])
    # entity.rotation_speed = float(parts[7])
    entity.rotation_speed = 0
    return entity


class Entity:
    def __init__(self, entity_id, glyph=None, x=0, y=0):
        # These values are sent in SNAPSHOTs
        self.entity_id = entity_id
        self.glyph = glyph
        self.x = x
        self.y = y
        self.x_speed = 0
        self.y_speed = 0
        self.accel = 0  # Acceleration in the current direction
        self.rotation = 0
        self.rotation_speed = 0
        self.maxSpeed = 15
        self.radius = 16

        # These are not sent in SNAPSHOTs:
        self.thruster_power = 0.5

    def create_snapshot_line(self):
        # TODO: Replace with use of string.format.
        return (str(self.entity_id)+" "+self.glyph+" "+str(self.x)+" " +
                str(self.y)+" "+str(self.x_speed)+" "+str(self.y_speed)+" " +
                str(self.rotation)+" "+str(self.rotation_speed))

    def update_position(self, world_width, world_height, wrap_padding):
        radians = math.radians(self.rotation)
        x_accel = math.cos(radians) * self.accel
        y_accel = -math.sin(radians) * self.accel

        self.x_speed = self.x_speed + x_accel
        self.y_speed = self.y_speed + y_accel

        speed = math.hypot(self.x_speed, self.y_speed)
        if speed > self.maxSpeed:
            ratio = self.maxSpeed / speed
            self.x_speed = self.x_speed * ratio
            self.y_speed = self.y_speed * ratio

        self.x = self.x + self.x_speed
        self.y = self.y + self.y_speed

        if self.x > world_width + wrap_padding:
            self.x -= (world_width + wrap_padding*2)
        elif self.x < -wrap_padding:
            self.x += (world_width + wrap_padding*2)
        if self.y > world_height + wrap_padding:
            self.y -= (world_height + wrap_padding*2)
        elif self.y < -wrap_padding:
            self.y += (world_height + wrap_padding*2)

        # May want to move this to be the first thing processed:
        self.rotation = self.rotation + self.rotation_speed

    def test_for_collision(self, other):
        distance = math.hypot(other.x - self.x, other.y - self.y)
        return distance < (self.radius + other.radius)

    def handle_collision(self, other, server):
        pass

    def act(self, current_time, server):
        pass

    def destroys_asteroid(self):
        return False

    def destroys_ship(self):
        return False

    def destroys_bullet(self):
        return False


class Asteroid(Entity):
    def __init__(self, entity_id, x, y):
        glyph_num = random.randint(1, 2)
        glyph = "ASTEROID"+str(glyph_num)
        # TODO: Use super()
        Entity.__init__(self, entity_id, glyph, x, y)
        direction = random.randint(0, 359)
        speed = random.randint(1, 4)
        self.x_speed = math.cos(direction) * speed
        self.y_speed = -math.sin(direction) * speed
        self.rotation = random.randint(0, 359)
        self.rotation_speed = random.randint(-4, 4)

    def handle_collision(self, other, server):
        if other.destroys_asteroid():
            server.remove_entity(self)
            # TODO: Fix this--only bullets have parent entities.
            server.on_asteroid_destroyed(other.parent_entity)

    def destroys_ship(self):
        return True

    def destroys_bullet(self):
        return True


class Spaceship(Entity):
    def __init__(self, entity_id, glyph, x, y):
        # TODO: Use super()
        Entity.__init__(self, entity_id, glyph, x, y)
        self.last_bullet_time = 0
        self.shooting = False
        self.radius = 10
        self.player_manager = None

    def thrust_forward(self):
        self.accel = self.thruster_power

    def thrust_backward(self):
        self.accel = -self.thruster_power

    def turn_off_thrusters(self):
        self.accel = 0

    def rotate_left(self):
        self.rotation_speed = 7

    def rotate_right(self):
        self.rotation_speed = -7

    def stop_rotation(self):
        self.rotation_speed = 0

    def start_shooting(self):
        self.shooting = True

    def stop_shooting(self):
        self.shooting = False

    def act(self, current_time, server):
        if self.shooting and (current_time - self.last_bullet_time) > 0.5:
            self.last_bullet_time = current_time
            server.spawn_bullet(self.x, self.y, self.rotation, self)

    def handle_collision(self, other, server):
        if other.destroys_ship():
            server.on_player_death(self)


class Bullet(Entity):
    def __init__(self, entity_id, parent_entity, x, y, rotation):
        # TODO: Use super()
        Entity.__init__(self, entity_id, "LASER", x, y)
        self.creation_time = time.time()
        self.parent_entity = parent_entity
        self.radius = 2
        self.rotation = rotation

    def act(self, current_time, server):
        if (current_time - self.creation_time) > 1.0:
            # Destroy the bullet.
            server.remove_entity(self)

    def handle_collision(self, other, server):
        if other.destroys_bullet():
            server.remove_entity(self)

    def destroys_asteroid(self):
        return True
