import time
import random
import math

from entities import Spaceship, Asteroid, Bullet
from engine import (
    NetroidsEngine, CONNECT_REQUEST_MESSAGE, CONTROL_MESSAGE, PING_MESSAGE,
    DISCONNECT_MESSAGE, WRAP_PADDING)
from interface import QUIT_EVENT
from player_managers import RemotePlayerManager


class Server(NetroidsEngine):
    def __init__(self, localAddress, player_name):
        NetroidsEngine.__init__(self, localAddress, player_name)

        self.player_look_pool = []
        self.player_look_pool.append(("BLUESHIP", (0, 0, 255)))
        self.player_look_pool.append(("REDSHIP", (255, 0, 0)))
        self.player_look_pool.append(("GREENSHIP", (0, 255, 0)))
        self.player_look_pool.append(("YELLOWSHIP", (255, 242, 0)))

        self.asteroids_per_round = 15
        self.next_snapshot_number = 1
        self.next_entity_id = 1
        self.player_map = {}  # Maps addresses to RemotePlayerManagers.
        self.first_round = True

        local_player_look = random.choice(self.player_look_pool)
        self.player_look_pool.remove(local_player_look)
        glyph, color = local_player_look
        self.local_player_ship = Spaceship(
            self.get_next_entity_id(), glyph, 400, 300)
        self.local_player = RemotePlayerManager(
            None, self.player_name, color, self.local_player_ship)
        self.add_entity(self.local_player_ship)
        self.finished = False
        self.set_message_handler(
            CONTROL_MESSAGE, self.handle_control_message)
        self.set_message_handler(
            CONNECT_REQUEST_MESSAGE, self.handle_connect_request)
        self.set_message_handler(PING_MESSAGE, self.handle_ping)
        self.gui.set_event_handler(QUIT_EVENT, self.end_game)
        self.messaging_service.disconnect_handler = self.on_address_disconnected
        self.set_message_handler(
            DISCONNECT_MESSAGE, self.handle_disconnect_message)

    def add_player(self, address, name):
        look = random.choice(self.player_look_pool)
        self.player_look_pool.remove(look)
        glyph, color = look
        player_ship = Spaceship(
            self.get_next_entity_id(), glyph, 400, 300)
        self.reset_ship_position(player_ship)
        self.add_entity(player_ship)
        player_manager = RemotePlayerManager(address, name, color, player_ship)
        player_manager.time_last_heard_from = time.time()
        self.player_map[address] = player_manager
        reply = "CONNECTACCEPT\n"+str(player_ship.entity_id)
        self.messaging_service.send_message(reply, address, True)
        self.broadcast_chat_message(name+" joined the game.", (255, 255, 255))

    def remove_player(self, address):
        player_manager = self.player_map[address]
        player_ship = player_manager.ship
        glyph = player_ship.glyph
        color = player_manager.color
        self.remove_entity(player_ship)
        del self.player_map[address]
        self.messaging_service.remove_data_for(address)
        self.player_look_pool.append((glyph, color))  # "Replenish" the pool

    def get_all_players(self):
        return self.player_map.values() + [self.local_player]

    def get_score_strings(self):
        return [(p.color, p.name+": "+str(p.score))
                for p in self.get_all_players()]

    def get_next_entity_id(self):
        ret_val = self.next_entity_id
        self.next_entity_id += 1
        return ret_val

    def on_address_disconnected(self, address):
        def do_later():
            remote_player_manager = self.player_map.get(address)
            if remote_player_manager:
                self.broadcast_chat_message(
                    remote_player_manager.name+" left the game.",
                    (255, 255, 255))
                self.remove_player(address)
        self.execute_later(do_later)

    def on_player_death(self, player_ship):
        player_manager = player_ship.player_manager
        player_manager.score -= 3
        self.reset_ship_position(player_ship)

    def reset_ship_position(self, ship):
        placed = False
        while not placed:
            ship.x = random.randint(
                WRAP_PADDING,
                self.world_width - WRAP_PADDING)
            ship.y = random.randint(
                WRAP_PADDING,
                self.world_height - WRAP_PADDING)
            placed = not self.test_for_collision(ship)
        ship.x_speed = 0
        ship.y_speed = 0
        ship.rotation = random.randint(0, 359)

    def start_round(self):
        for i in range(self.asteroids_per_round):
            placed = False
            asteroid = Asteroid(self.get_next_entity_id(), 0, 0)
            while not placed:
                asteroid.x = random.randint(0, self.world_width)
                asteroid.y = random.randint(0, self.world_height)
                placed = not self.test_for_collision(asteroid)  # True if there was no collision
            self.add_entity(asteroid)
        top_score = None
        winning_players = []
        for player_manager in self.get_all_players():
            self.reset_ship_position(player_manager.ship)
            if top_score is None or player_manager.score > top_score:
                top_score = player_manager.score
                winning_players = [player_manager]
            elif player_manager.score == top_score:
                winning_players.append(player_manager)
            player_manager.resetScore()
        if self.first_round:
            self.first_round = False
        else:
            self.broadcast_winners(winning_players, top_score)
        self.broadcast_chat_message("New round starting!", (255, 255, 255))

    def broadcast_winners(self, winning_players, top_score):
        if len(winning_players) == 1:
            winning_player = winning_players[0]

            # TODO: Replace with use of string.format.
            message = winning_player.name + " wins the round with "+str(top_score)+" points!"
        else:
            # TODO: Replace with use of string.format.
            names = " and ".join([winning_player.name for winning_player in winning_players])
            message = names + " win the round with "+str(top_score)+" points!"
        self.broadcast_chat_message(message, (255, 255, 255))

    def on_asteroid_destroyed(self, player_ship_entity):
        player_manager = player_ship_entity.player_manager
        player_manager.score += 1
        self.check_asteroids()

    def check_asteroids(self):
        asteroids_left = False
        for entity in self.entity_map.values():
            if isinstance(entity, Asteroid):
                asteroids_left = True
                break
        if not asteroids_left:
            self.start_round()

    def handle_control_message(self, message, address):
        lines = message.splitlines()
        entity_id = int(lines[1])
        entity = self.entity_map[entity_id]
        for line in lines[2:]:
            if line.startswith("Throttle:"):
                thrustDir = line.split(":")[1].strip()
            elif line.startswith("Rotating:"):
                rotation = line.split(":")[1].strip()
            elif line.startswith("Shooting:"):
                shooting = line.split(":")[1].strip()
        self.update_ship(entity_id, thrustDir, rotation, shooting)
        player_manager = self.player_map[address]
        player_manager.time_last_heard_from = time.time()

    def handle_connect_request(self, message, address):
        lines = message.splitlines()
        player_name = lines[1]
        self.add_player(address, player_name)

    def handle_disconnect_message(self, message, address):
        self.on_address_disconnected(address)

    def handle_chat_send(self, message, address):
        player_manager = self.player_map[address]
        lines = message.splitlines()
        chat_message = player_manager.name+": "+lines[1]
        self.broadcast_chat_message(chat_message, player_manager.color)

    def handle_ping(self, message, address):
        lines = message.splitlines()
        reply = "PINGREPLY\n"+lines[1]
        self.messaging_service.send_message(reply, address, False)

    def send_snapshot(self):
        # TODO: Replace with use of string.format.
        message = "SNAPSHOT\n"+str(self.next_snapshot_number)
        for player_manager in self.get_all_players():
            color_string = ",".join([str(comp) for comp in player_manager.color])
            message += "\n"+color_string+"|"+player_manager.name+": "+str(player_manager.score)
        message += "\n"
        for entity in self.get_entities():
            message += "\n"+entity.create_snapshot_line()
        for player_address in self.player_map.keys():
            self.messaging_service.send_message(message, player_address, False)
        self.next_snapshot_number += 1

    def end_game(self):
        for ip_address in self.player_map.keys():
            self.messaging_service.send_message("DISCONNECT", ip_address, False)
        self.finished = True

    def update_player_ship(self):
        throttle_status = self.local_player_manager.get_throttle_status()
        rotation_status = self.local_player_manager.get_rotation_status()
        shooting_status = self.local_player_manager.get_shooting_status()
        self.update_ship(
            self.local_player_ship.entity_id,
            throttle_status, rotation_status, shooting_status)

    def update_ship(
            self, entity_id, throttle_status, rotation_status, shooting_status):
        ship = self.entity_map[entity_id]
        if throttle_status == "forward":
            ship.thrust_forward()
        elif throttle_status == "backward":
            ship.thrust_backward()
        elif throttle_status == "off":
            ship.turn_off_thrusters()
        elif throttle_status is None:
            pass
        else:
            raise Exception("Invalid Throttle value")

        if rotation_status == "left":
            ship.rotate_left()
        elif rotation_status == "right":
            ship.rotate_right()
        elif rotation_status == "off":
            ship.stop_rotation()
        elif rotation_status is None:
            pass
        else:
            raise Exception("Invalid Rotating value")

        if shooting_status == "on":
            ship.start_shooting()
        elif shooting_status == "off":
            ship.stop_shooting()
        elif shooting_status is None:
            pass
        else:
            raise Exception("Invalid shooting status")

    def let_entities_act(self):
        current_time = time.time()
        for entity in self.entity_map.values():
            entity.act(current_time, self)

    def handle_collisions(self):
        entities = self.entity_map.values()
        for i, entity1 in enumerate(entities):
            for entity2 in entities[(i+1):]:
                if entity1.test_for_collision(entity2):
                    entity1.handle_collision(entity2, self)
                    entity2.handle_collision(entity1, self)

    def test_for_collision(self, entity):
        for other in self.entity_map.values():
            if other != entity and entity.test_for_collision(other):
                return True
        return False

    def spawn_bullet(self, x, y, direction, parent_entity):
        bullet = Bullet(
            self.get_next_entity_id(), parent_entity, x, y, direction)
        radians = math.radians(direction)
        bullet.x_speed = math.cos(radians) * 15
        bullet.y_speed = -math.sin(radians) * 15
        self.add_entity(bullet)

    def broadcast_chat_message(self, message, color):
        color_string = ",".join([str(comp) for comp in color])
        for player_address in self.player_map.keys():
            self.messaging_service.send_message(
                "CHATCAST\n"+color_string+"\n"+message, player_address, True)
        self.chat_messages.append((message, time.time()))

    def check_for_disconnection(self, current_time):
        for remote_player_manager in self.player_map.values():
            if (
                    current_time - remote_player_manager.time_last_heard_from
                    > 10.0):
                self.on_address_disconnected(remote_player_manager.ip_address)

    def go(self):
        self.messaging_service.start_listening()
        self.start_round()
        last_snapshot_time = 0
        last_disconnect_check_time = 0
        while not self.finished:
            current_time = time.time()
            self.handle_all_messages()
            if current_time - last_disconnect_check_time > 1.0:
                self.check_for_disconnection(current_time)
            self.execute_stuff()
            self.gui.process_events()
            self.local_player_manager.clear_fired_this_frame()  # Todo: Make this cleaner
            self.update_player_ship()
            self.update_entity_positions()
            self.let_entities_act()
            if (current_time - last_snapshot_time) > 0.05:
                self.send_snapshot()
                last_snapshot_time = current_time
            self.gui.draw(self)
            self.gui.tick()
            self.handle_collisions()
        self.messaging_service.stop_listening()
