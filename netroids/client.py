import time

from engine import (NetroidsEngine, CHAT_MESSAGE, CONNECT_ACCEPT_MESSAGE,
                    DISCONNECT_MESSAGE, PING_REPLY_MESSAGE, SNAPSHOT_MESSAGE)
from entities import entity_from_snapshot_line
from interface import QUIT_EVENT


class Client(NetroidsEngine):
    def __init__(self, local_address, server_address, player_name):
        # TODO: Switch to super()
        NetroidsEngine.__init__(self, local_address, player_name)
        self.last_snapshot_number = -1
        self.last_snapshot_time = None
        self.last_ping_number = 0
        self.last_ping_time = 0
        self.rtts = []  # RTTs for last 30 seconds
        self.avg_rtt = 0  # Average RTT over last 30 seconds
        self.server_address = server_address
        self.snapshot_received = False
        self.finished = False
        self.score_strings = []
        self.set_message_handler(
            CONNECT_ACCEPT_MESSAGE,
            self.handle_connect_accept_message)
        self.set_message_handler(
            SNAPSHOT_MESSAGE, self.handle_snapshot_message)
        self.set_message_handler(CHAT_MESSAGE, self.handle_chat_cast)
        self.set_message_handler(
            PING_REPLY_MESSAGE, self.handle_ping_reply)
        self.set_message_handler(
            DISCONNECT_MESSAGE, self.handle_disconnect_message)
        self.gui.set_event_handler(QUIT_EVENT, self.quit)

    def get_score_strings(self):
        return self.score_strings
        # return [(p.color,p.name+": "+str(p.score)) for p in self.getAllPlayers()]

    def handle_connect_accept_message(self, message, address):
        lines = message.splitlines()
        entityID = int(lines[1].strip())
        self.local_player_manager.setEntity(entityID)
        self.last_snapshot_time = time.time()

    def handle_chat_cast(self, message, address):
        lines = message.splitlines()
        color = tuple([int(comp) for comp in lines[1].split(",")])
        chat_message = lines[2]
        self.chat_messages.append((chat_message, time.time()))

    def handle_snapshot_message(self, message, address):
        # TODO: Add position extrapolation (after it works without it!)
        lines = message.splitlines()
        snapshot_number = int(lines[1])
        self.last_snapshot_time = time.time()
        if snapshot_number > self.last_snapshot_number:
            self.snapshot_received = True
            self.last_snapshot_number = snapshot_number
            self.entity_map.clear()
            self.score_strings = []
            i = 2
            while True:
                line = lines[i]
                i += 1
                if line == "":
                    break
                else:
                    parts = line.split("|")
                    color = tuple([int(comp) for comp in parts[0].split(",")])
                    score_string = parts[1]
                    self.score_strings.append((color, score_string))

            for line in lines[i:]:
                entity = entity_from_snapshot_line(line)
                self.add_entity(entity)

    def handle_ping_reply(self, message, address):
        lines = message.splitlines()
        ping_number = int(lines[1])
        if ping_number == self.last_ping_number:
            rtt = time.time() - self.last_ping_time
            if self.rtts:
                self.rtts.pop(0)  # Remove first item.
            self.rtts.append(rtt)
            self.avg_rtt = sum(self.rtts) / len(self.rtts)

    def handle_disconnect_message(self, message, address):
        self.on_address_disconnected(None)

    def send_connect_request(self):
        self.last_snapshot_time = time.time()
        self.messaging_service.send_message(
            "CONNECTREQUEST\n"+self.player_name, self.server_address, True)

    def send_control_update(self):
        message = self.local_player_manager.generate_control_message()
        self.local_player_manager.clear_fired_this_frame()
        if message:  # message will be none if we are not actually connected
            self.messaging_service.send_message(
                message, self.server_address, False)

    def send_ping(self):
        self.last_ping_number += 1
        message = "PING\n"+str(self.last_ping_number)
        self.messaging_service.send_message(message, self.server_address, False)
        self.last_ping_time = time.time()

    def check_for_disconnection(self, current_time):
        if current_time - self.last_snapshot_time > 10:
            # Disconnected!
            self.on_address_disconnected(None)

    def on_address_disconnected(self, address):
        print "Connection to server lost!"
        self.quit()

    def quit(self):
        self.messaging_service.send_message(
            "DISCONNECT", self.server_address, False)
        self.finished = True

    def go(self):
        self.messaging_service.start_listening()
        self.send_connect_request()
        last_update_time = 0
        last_disconnect_check_time = time.time()
        while not self.finished:
            current_time = time.time()
            self.snapshot_received = False
            self.handle_all_messages()
            if not self.snapshot_received:  # Add this in later to increase smoothness of motion.
                self.update_entity_positions()
            if current_time - last_disconnect_check_time > 1.0:
                self.check_for_disconnection(current_time)
            self.execute_stuff()
            self.gui.process_events()
            if (current_time - last_update_time) > 0.1:
                self.send_control_update()
                last_update_time = current_time
            if (current_time - self.last_ping_time) > 1.0:
                self.send_ping()
            self.gui.draw(self)
            self.gui.tick()
        self.messaging_service.stop_listening()
