import argparse
import datetime
import random
import socket
import string
import threading
import time

BUFFER_SIZE = 2048
ENCODING = 'ascii'

threads = {}
to_join = []

parser = argparse.ArgumentParser(description="Msg server")
parser.add_argument("-s", "--sleep", type=float, help="sleep time between reception and sending", default=5.0)
parser.add_argument("-b", "--bytes", type=int, help="number of bytes to send and receive", default=1200)

args = parser.parse_args()


def string_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class HandleClientConnectionThread(threading.Thread):
    """ Handle requests given by the client """

    def __init__(self, connection, client_address, id, msg_size):
        threading.Thread.__init__(self)
        self.connection = connection
        self.client_address = client_address
        self.id = id
        self.msg_size = msg_size
        self.delays = []

    def run(self):
        try:
            print(self.id, ": Connection from", self.client_address)
            start_time = None
            buffer_data = ""

            # Receive the data and retransmit it
            while True:
                data = self.connection.recv(BUFFER_SIZE).decode(ENCODING)

                if len(data) == 0:
                    # Connection closed at remote; close the connection
                    break

                buffer_data += data

                if len(buffer_data) >= self.msg_size:
                    stop_time = datetime.datetime.now()
                    if start_time:
                        self.delays.append(stop_time - start_time)
                    time.sleep(args.sleep)
                    response = string_generator(size=self.msg_size, chars=string.digits)
                    start_time = datetime.datetime.now()
                    self.connection.sendall(response.encode(ENCODING))
                    buffer_data = buffer_data[self.msg_size:]

        finally:
            # Clean up the connection
            print(self.id, ": Closing connection")
            self.connection.close()
            print(self.delays)
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
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK, 0)

# Bind the socket to the port
server_address = ('0.0.0.0', 8000)
print("Stating the server on %s port %s" % server_address)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(4)

# Connection identifier
conn_id = 0

while True:
    # Wait for a connection
    connection, client_address = sock.accept()
    thread = HandleClientConnectionThread(connection, client_address, conn_id, args.bytes)
    threads[conn_id] = thread
    conn_id += 1
    thread.start()
    join_finished_threads()
