from __future__ import with_statement

import socket
import threading
import time


class MessagingService:
    def __init__(self, local_address):
        # self.playerDict = {}  # Maps player names to addresses.
        self.message_queue = []  # contains tuples of the form (message, address)
        self.received_acks = set()
        self.received_acks_lock = threading.Lock()
        self.messages_lock = threading.Lock()
        self.listening = False
        self.udp_started = False
        self.local_address = local_address
        self.next_important_id = 1
        self.disconnect_handler = None
        self.important_ids = {}  # Maps IP addresses to sets of important_ids already received
        self.important_ids_lock = threading.Lock()

    def start_listening(self):
        self.listening = True
        UdpListenThread = threading.Thread(target=self.listen_on_udp)
        UdpListenThread.start()
        while (not self.udp_started):
            pass

    def stop_listening(self):
        self.listening = False

    def get_next_important_id(self):
        retVal = self.next_important_id
        self.next_important_id += 1
        return retVal

    def send_message(self, message, recipient_ip_address, important=False):
        recipient_address = (recipient_ip_address, 5005)
        if important:
            important_id = self.get_next_important_id()

            def thread_callable():
                self._send_important_message(
                    message, recipient_ip_address, important_id)
            sender_thread = threading.Thread(target=thread_callable)
            sender_thread.start()
            # self._send_whole_message(whole_message, recipient_ip_address)
        else:
            whole_message = "N\n"+message
            self._send_whole_message(whole_message, recipient_ip_address)
            # print "Sent to "+str(recipient_address)+" via UDP: "+message

    def _send_whole_message(self, whole_message, ip_address):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(whole_message, (ip_address, 5005))
        sock.close()

    def _send_important_message(self, message, ip_address, important_id):
        whole_message = "I"+str(important_id)+"\n"+message
        for i in range(5):
            self._send_whole_message(whole_message, ip_address)
            time.sleep(2)
            with self.received_acks_lock:
                if important_id in self.received_acks:
                    return
        if self.disconnect_handler:
            self.disconnect_handler(ip_address)

    def acknowledge_message(self, message, ip_address):
        lines = message.splitlines()
        important_id = lines[0][1:]
        reply = "R"+important_id
        self._send_whole_message(reply, ip_address)

    # This should run on a separate thread:
    def listen_on_udp(self):
        listening_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listening_sock.settimeout(0.2)  # 0.2 seconds, 200 ms
        listening_sock.bind((self.local_address, 5005))
        self.udp_started = True
        while self.listening:
            try:
                message, address_tuple = listening_sock.recvfrom(4096)
                ip_address = address_tuple[0]
                # print "Received via UDP from "+str(address_tuple)+": "+str(message)
                parts = message.split("\n", 1)
                message_info_line = parts[0]
                if len(parts) > 1:
                    actual_message = parts[1]
                else:
                    actual_message = None
                if message_info_line[0] == "R":
                    important_id = int(message_info_line[1:])
                    with self.received_acks_lock:
                        self.received_acks.add(important_id)
                else:
                    if message_info_line[0] == "I":
                        important_id = int(message_info_line[1:])
                        with self.important_ids_lock:
                            last_important_id_set = self.important_ids.setdefault(
                                ip_address, set())
                            if important_id not in last_important_id_set:
                                self._store_message(actual_message, ip_address)
                                last_important_id_set.add(important_id)
                        self.acknowledge_message(message, ip_address)
                    else:
                        self._store_message(actual_message, ip_address)
            except socket.timeout:
                pass
        listening_sock.close()

    def _store_message(self, message, ip_address):
        with self.messages_lock:
            self.message_queue.append((message, ip_address))

    def get_next_message(self):
        with self.messages_lock:
            if self.message_queue:
                return self.message_queue.pop(0)
            else:
                return None

    def remove_data_for(self, ip_address):
        with self.important_ids_lock:
            if ip_address in self.important_ids:
                del self.important_ids[ip_address]
