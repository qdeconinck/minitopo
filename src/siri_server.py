import socket
import sys
import threading
import time

BUFFER_SIZE = 512
ENCODING = 'ascii'

MAX_SECURITY_HEADER_SIZE = 128
MIN_FIELDS_NB = 8

threads = {}
to_join = []
delay_results = {}
time_sent = {}
mac = {}


class HandleClientConnectionThread(threading.Thread):
    """ Handle requests given by the client """

    def __init__(self, connection, client_address, id):
        threading.Thread.__init__(self)
        self.connection = connection
        self.client_address = client_address
        self.id = id

    def run(self):
        try:
            print(self.id, ": Connection from", self.client_address)

            # Some useful variables
            first_data = True
            expected_req_size = 0
            res_size = 0
            waiting_time = 0
            expected_delay_results = 0
            buffer_data = ""
            next_buffer_data = ""
            message_sizes = []
            message_id = 0

            # Initialize logging variables
            delay_results[self.id] = []
            time_sent[self.id] = []

            # Receive the data and retransmit it
            while True:
                data = self.connection.recv(BUFFER_SIZE).decode(ENCODING)

                if len(data) == 0:
                    # Connection closed at remote; close the connection
                    break

                # Manage the case where the client is very very quick
                if not data.endswith("\n") and "\n" in data:
                    carriage_index = data.index("\n")
                    buffer_data += data[:carriage_index + 1]
                    next_buffer_data += data[carriage_index + 1:]
                    used_data = data[:carriage_index + 1]
                else:
                    buffer_data += data
                    used_data = data

                message_sizes.append(len(used_data))

                if first_data and len(buffer_data) <= MAX_SECURITY_HEADER_SIZE and len(buffer_data.split("&")) < MIN_FIELDS_NB:
                    continue

                if first_data:
                    split_data = buffer_data.split("&")
                    expected_delay_results = int(split_data[4])
                    if len(split_data) - MIN_FIELDS_NB == expected_delay_results:
                        message_id = int(split_data[0])
                        expected_req_size = int(split_data[1])
                        res_size = int(split_data[2])
                        waiting_time = int(split_data[3])
                        time_sent[self.id].append(int(split_data[5]))

                        # Little check, we never know
                        if self.id not in mac:
                            mac[self.id] = split_data[6]
                        elif not mac[self.id] == split_data[6]:
                            print(self.id, ": MAC changed from", mac[self.id], "to", split_data[6], ": close the connection", file=sys.stderr)
                            break

                        for i in range(expected_delay_results):
                            delay_results[self.id].append(int(split_data[7 + i]))
                        first_data = False
                    else:
                        # Avoid further processing, wait for additional packets
                        continue

                if len(buffer_data) == expected_req_size:
                    # print(self.id, ": Received request of size", expected_req_size, "; send response of", res_size, "after", waiting_time, "s")
                    time.sleep(waiting_time)
                    self.connection.sendall((str(message_id) + "&" + "0" * (res_size - len(str(message_id)) - 2) + "\n").encode(ENCODING))
                    first_data = True
                    buffer_data = ""
                    message_sizes = []
                    if len(next_buffer_data) > 0:
                        buffer_data = next_buffer_data
                        next_buffer_data = ""
                        message_sizes.append(len(buffer_data))

                elif len(buffer_data) > expected_req_size:
                    print(len(buffer_data), len(data), len(used_data), file=sys.stderr)
                    print(self.id, ": Expected request of size", expected_req_size, "but received request of size", len(buffer_data), "; close the connection", file=sys.stderr)
                    print(buffer_data, file=sys.stderr)
                    break

        finally:
            # Clean up the connection
            print(self.id, ": Closing connection")
            self.connection.close()
            to_join.append(self.id)


def join_finished_threads():
    """ Join threads whose connection is closed """
    while len(to_join) > 0:
        thread_to_join_id = to_join.pop()
        threads[thread_to_join_id].join()
        del threads[thread_to_join_id]

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Handle reusing the same 5-tuple if the previous one is still in TIME_WAIT
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

# Bind the socket to the port
server_address = ('0.0.0.0', 8080)
print("Stating the server on %s port %s" % server_address)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(4)

# Connection identifier
conn_id = 0

while True:
    # Wait for a connection
    connection, client_address = sock.accept()
    thread = HandleClientConnectionThread(connection, client_address, conn_id)
    threads[conn_id] = thread
    conn_id += 1
    thread.start()
    join_finished_threads()
