from __future__ import with_statement

import time
import threading

from messaging_service import MessagingService
from interface import GUI
from player_managers import LocalPlayerManager

CONTROL_MESSAGE = "CONTROL"
CONNECT_REQUEST_MESSAGE = "CONNECTREQUEST"
PING_MESSAGE = "PING"

DISCONNECT_MESSAGE = "DISCONNECT"

SNAPSHOT_MESSAGE = "SNAPSHOT"
CONNECT_ACCEPT_MESSAGE = "CONNECTACCEPT"
PING_REPLY_MESSAGE = "PINGREPLY"
CHAT_MESSAGE = "CHATCAST"

WRAP_PADDING = 16


class NetroidsEngine:
    def __init__(self, local_address, player_name):
        self.entity_map = {}  # Maps IDs to entities
        self.messaging_service = MessagingService(
            local_address)

        self.player_name = player_name
        self.message_handlers = {}  # Maps message types to callback methods
        self.world_width = 800  # TODO: Make this something the server sends to the client.
        self.world_height = 600
        self.gui = GUI()
        self.local_player_manager = LocalPlayerManager(self.gui)
        # self.chat_messages = [("Hello, world!",5),("You smell!",3), ("Ha ha ha ha ha!",4)] # Queue of tuples of form (string, creation_time)
        self.chat_messages = []
        self.stuff_to_execute_later = []  # Queue of callables
        self.stuff_to_execute_later_lock = threading.Lock()

    # Returns a list of Entities
    def get_entities(self):
        return self.entity_map.values()

    def get_chat_message_strings(self):
        current_time = time.time()
        return [message for message, creation_time in self.chat_messages
                if current_time - creation_time < 10]

    def add_entity(self, entity):
        self.entity_map[entity.entity_id] = entity

    def remove_entity(self, entity):
        if entity.entity_id in self.entity_map:
            del self.entity_map[entity.entity_id]

    def set_message_handler(self, message_type, handler):
        if message_type in self.message_handlers:
            raise Exception("Overwriting message handler for "+message_type)
        self.message_handlers[message_type] = handler

    def handle_message(self, message, address):
        lines = message.splitlines()
        handler = self.message_handlers.get(lines[0])
        if handler:
            handler(message, address)

    def handle_all_messages(self):
        next_message_tuple = self.messaging_service.get_next_message()
        while next_message_tuple is not None:
            message, address = next_message_tuple
            self.handle_message(message, address)
            next_message_tuple = self.messaging_service.get_next_message()

    def update_entity_positions(self):
        for entity in self.entity_map.values():
            entity.update_position(
                self.world_width, self.world_height, WRAP_PADDING)

    def execute_later(self, callable):
        with self.stuff_to_execute_later_lock:
            self.stuff_to_execute_later.append(callable)

    def execute_stuff(self):
        with self.stuff_to_execute_later_lock:
            while len(self.stuff_to_execute_later) > 0:
                callable = self.stuff_to_execute_later.pop(0)
                callable()
