import socket
import select
import pickle
import time
import datetime
import threading
import sys
import copy
import math

class OSPFRouter:
    def __init__(self, router_id):
        self.router_id = router_id
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('localhost', 10000 + self.router_id))
        self.neighbor_table = {}  # {neighbor_router_id: cost, state, DBD}
        self.routing_table = {} # {neighbor_router_id: cost, next_hop}
        self.LSDB = {} # {router_id: sequence, links} {links: neighbor_router_id, cost}
        self.LSDB[self.router_id] = [0, []]
        self.thread_running = True

    def compute_shortest_path(self):
        n = 0
        for router_id in self.LSDB:
            if n <= router_id:
                n = router_id + 1
            for neighbor in self.LSDB[router_id][1]:
                if n <= neighbor[0]:
                    n = neighbor[0] + 1
        source = self.router_id
        dijk = [float('inf') for i in range(n)]
        parent = [-1 for i in range(n)]
        next_hop = [-1 for i in range(n)]
        w = [[-1 for j in range(n)] for i in range(n)]
        visit = [False for i in range(n)]
        
        for router_id in self.LSDB:
            for neighbor in self.LSDB[router_id][1]:
                w[router_id][neighbor[0]] = neighbor[1]
                w[neighbor[0]][router_id] = neighbor[1]

        dijk[source] = 0
        parent[source] = self.router_id
        next_hop[source] = self.router_id
        
        for i in range(n):
            min_dijk = float('inf')
            for j in range(n):
                if not visit[j] and dijk[j] < min_dijk:
                    source = j
                    min_dijk = dijk[j]

            if math.isinf(min_dijk):
                break

            visit[source] = True

            for j in range(n):
                if w[source][j] != -1:
                    if not visit[j] and dijk[source] + w[source][j] < dijk[j]:
                        dijk[j] = dijk[source] + w[source][j]
                        parent[j] = source
        
        for i in range(1, n):
            current_node = i
            while parent[current_node] != self.router_id:
                current_node = parent[current_node]
            next_hop[i] = current_node
        
        return dijk, next_hop
    
    def receive_message(self, message):
        source = message[1]
        message_word =message[3]
        print(f"Recv message from {source}: {message_word}")

    def forward_message(self, message):
        source = message[1]
        destination = message[2]
        message_word = message[3]
        next_hop = self.routing_table[destination][1]
        self.send_message_to_neighbor(message, next_hop)
        print(f"Forward message from {source} to {destination}: {message_word}")

    def add_neighbor(self, router_id, cost, state, DBD):
        self.neighbor_table[router_id] = (cost, state, DBD)
        current_time = datetime.datetime.now().strftime('%H:%M:%S')
        print(f"{current_time} - add neighbor {router_id} {cost}")

    def update_neighbor(self, router_id, cost, state, DBD):
        if router_id in self.neighbor_table:
            self.neighbor_table[router_id] = (cost, state, DBD)
            current_time = datetime.datetime.now().strftime('%H:%M:%S')
            print(f"{current_time} - update neighbor {router_id} {cost}")
        else:
            self.add_neighbor(router_id, cost, state, DBD)

    def remove_neighbor(self, router_id):
        if router_id in self.neighbor_table:
            self.neighbor_table.pop(router_id)
            current_time = datetime.datetime.now().strftime('%H:%M:%S')
            print(f"{current_time} - remove neighbor {router_id}")

    def add_LSA(self, router_id, added_LSA):
        self.LSDB[router_id] = added_LSA
        current_time = datetime.datetime.now().strftime('%H:%M:%S')
        print(f"{current_time} - add LSA {router_id} {added_LSA[0]}")

    def update_LSA(self, updated_LSA):
        is_updated = False
        for router_id, LSA in updated_LSA.items():
            if router_id in self.LSDB:
                if self.LSDB[router_id][0] < LSA[0] or self.LSDB[router_id][1] != LSA[1]:
                    if self.LSDB[router_id][1] != LSA[1]:
                        current_time = datetime.datetime.now().strftime('%H:%M:%S')
                        print(f"{current_time} - update LSA {router_id} {self.LSDB[router_id][0] + 1}")
                    is_updated = True
                    self.LSDB[router_id] = LSA
            else:
                is_updated = True
                self.add_LSA(router_id, LSA)
        
        self.update_route()

        if is_updated:
            self.flood_LSU(updated_LSA)

    def remove_LSA(self, router_id):
        for router in self.LSDB[self.router_id][1]:
            if router[0] == router_id:
                self.LSDB[self.router_id][1].remove(router)
                self.LSDB[self.router_id][0] += 1
                current_time = datetime.datetime.now().strftime('%H:%M:%S')
                print(f"{current_time} - remove LSA {self.router_id} {self.LSDB[self.router_id][0]}")
                self.update_route()
                break

    def add_route(self, router_id, cost, next_hop):
        self.routing_table[router_id] = [cost, next_hop]
        current_time = datetime.datetime.now().strftime('%H:%M:%S')
        print(f"{current_time} - add route {router_id} {next_hop} {cost}")

    def update_route(self): # next hop
        dijk, next_hop = self.compute_shortest_path()
        for router_id in range(len(dijk)):
            if not math.isinf(dijk[router_id]) and dijk[router_id] != 0:
                if router_id in self.routing_table:
                    if dijk[router_id] != self.routing_table[router_id][0] or next_hop[router_id] != self.routing_table[router_id][1]:
                        self.routing_table[router_id] = [dijk[router_id], next_hop[router_id]]
                        current_time = datetime.datetime.now().strftime('%H:%M:%S')
                        print(f"{current_time} - update route {router_id} {next_hop[router_id]} {dijk[router_id]}")
                else:
                    self.add_route(router_id, dijk[router_id], next_hop[router_id])
            elif math.isinf(dijk[router_id]) and router_id in self.routing_table:
                self.remove_route(router_id)

        # for router_id in range(len(self.routing_table)):
        #     if not router_id in dijk:
        #         self.remove_route(router_id)

    def remove_route(self, router_id):
        self.routing_table.pop(router_id)
        current_time = datetime.datetime.now().strftime('%H:%M:%S')
        print(f"{current_time} - remove route {router_id}")
        
    def set_neighbor_state(self, router_id, state):
        cost = self.neighbor_table[router_id][0]
        DBD = self.neighbor_table[router_id][2]
        self.neighbor_table[router_id] = (cost, state, DBD)
        current_time = datetime.datetime.now().strftime('%H:%M:%S')
        print(f"{current_time} - set neighbor state {router_id} {state}")

    def flood_LSU(self, flooded_LSU):
        message = ["LSU", flooded_LSU]
        for neighbor in self.neighbor_table:
            if self.neighbor_table[neighbor][1] == "Full":
                self.send_message_to_neighbor(message, neighbor)

    def compare_with_LSDB(self, DBD):
        same = True
        need_to_update = []
        for router_id in DBD:
            if (not router_id in self.LSDB): # old version or not in the LSDB
                same = False
                need_to_update.append(router_id)
        return same, need_to_update

    def send_message_to_neighbor(self, message, router_id):
        host = '127.0.0.1'
        port = 10000 + router_id
        address = (host, port)
        message = pickle.dumps(message)
        self.socket.sendto(message, address)

    def handle_receive_message(self, message, address):
        message = pickle.loads(message)
        router_id = address[1] - 10000
        
        if router_id in self.neighbor_table:
            if message[0] == "hello":
                if message[1] == "hasn't received hello":
                    self.set_neighbor_state(router_id, "Init")
                elif message[1] == "has received hello":
                    if self.neighbor_table[router_id][1] != "Full" and self.neighbor_table[router_id][1] != "Exchange":
                        self.set_neighbor_state(router_id, "Exchange")
            elif message[0] == "DBD":
                DBD = message[1]
                same, need_to_update = self.compare_with_LSDB(DBD)
                if same == True:
                    if self.neighbor_table[router_id][1] != "Full":
                        new_DBD = {}
                        for LSA in self.LSDB:
                            new_DBD[LSA] = self.LSDB[LSA][0]
                        message = ["DBD",  new_DBD]
                        self.send_message_to_neighbor(message, router_id)
                        self.set_neighbor_state(router_id, "Full")
                else:
                    message = ["LSR", need_to_update]
                    self.send_message_to_neighbor(message, router_id)
            elif message[0] == "LSR":
                need_to_update = message[1]
                updated_LSA = {}
                for updated_router_id in need_to_update:
                    updated_LSA[updated_router_id] = self.LSDB[updated_router_id]
                message = ["LSU", updated_LSA]
                self.send_message_to_neighbor(message, router_id)
            elif message[0] == "LSU":
                updated_LSA = message[1]
                self.update_LSA(updated_LSA)
            elif message[0] == "message":
                destination = message[2]
                if destination == self.router_id:
                    self.receive_message(message)
                else:
                    self.forward_message(message)

    def handle_input(self, user_input):
        
        words = user_input.split()
        command = words[0]

        if command == "addlink": #addlink
            if len(words) == 3:
                router_id = int(words[1])
                cost = int(words[2])
                if router_id in self.neighbor_table:
                    print("neighbor already exist")
                else:
                    time.sleep(1)
                    cost = int(words[2])
                    self.update_neighbor(router_id, cost, "Down", "None")
                    updated_LSA = {}
                    updated_LSA[self.router_id] = copy.deepcopy(self.LSDB[self.router_id])
                    updated_LSA[self.router_id][0] += 1
                    updated_LSA[self.router_id][1].append([router_id, cost])
                    self.update_LSA(updated_LSA)
            else:
                print("wrong command format")
        elif command == "setlink":
            if len(words) == 3:
                router_id = int(words[1])
                cost = int(words[2])
                if router_id in self.neighbor_table:
                    state = self.neighbor_table[router_id][1]
                    DBD = self.neighbor_table[router_id][2]
                    self.update_neighbor(router_id, cost, state, DBD)
                    updated_LSA = {}
                    updated_LSA[self.router_id] = copy.deepcopy(self.LSDB[self.router_id])
                    updated_LSA[self.router_id][0] += 1
                    for router in updated_LSA[self.router_id][1]:
                        if router_id == router[0]:
                            router[1] = cost
                    self.update_LSA(updated_LSA)
                    self.update_route()
                else:
                    print("router is not in the neighbor table")
            else:
                print("wrong command format")
        elif command == "rmlink":
            if len(words) == 2:
                router_id = int(words[1])
                if router_id in self.neighbor_table:
                    self.remove_neighbor(router_id)
                    self.remove_LSA(router_id)
                    flooded_LSU = {}
                    flooded_LSU[self.router_id] = self.LSDB[self.router_id]
                    self.flood_LSU(flooded_LSU)
                else:
                    print("router is not in the neighbor table")
            else:
                print("wrong command format")
        elif command == "send": # send
            if len(words) == 3:
                source = self.router_id
                destination = int(words[1])
                message = ["message", source, destination, words[2]]
                if destination in self.routing_table:
                    next_hop = self.routing_table[destination][1]
                    self.send_message_to_neighbor(message, next_hop)
                else:
                    print(self.routing_table)
                    print("this router is not in routing table")
            else:
                print("wrong command format")
        elif command == "exit":
            # self.socket.close()
            self.thread_running = False
            sys.exit(0)
        # elif command == "p":
        #     if words[2] == "l":
        #         print(self.LSDB)
        #     elif words[2] == "r":
        #         print(self.routing_table)
        #     elif words[2] == "n":
        #         print(self.neighbor_table)
        else:
            print("wrong command")

    def check_neighbor_table(self):
        hello_time = time.time()
        DBD_time = time.time()
        LSA_time = time.time()
        while self.thread_running:
            time.sleep(0.1)
            
            if time.time() - LSA_time >= 15:
                self.LSDB[self.router_id][0] += 1
                flooded_LSA = {}
                flooded_LSA[self.router_id] = self.LSDB[self.router_id]
                self.flood_LSU(flooded_LSA)
                LSA_time = time.time()

            for router_id, (cost, state, DBD) in self.neighbor_table.items():
                if state == "Down":
                    if time.time() - hello_time >= 1:
                        message = ["hello", "hasn't received hello", cost]
                        self.send_message_to_neighbor(message, router_id)
                        hello_time = time.time()
                elif state == "Init":
                    if time.time() - hello_time >= 1:
                        message = ["hello", "has received hello", cost]
                        self.send_message_to_neighbor(message, router_id)
                        hello_time = time.time()
                elif state == "Exchange":
                    if time.time() - hello_time >= 1:
                        message = ["hello", "has received hello", cost]
                        self.send_message_to_neighbor(message, router_id)
                        hello_time = time.time()
                    if time.time() - DBD_time >= 1:
                        DBD = {}
                        for LSA in self.LSDB:
                            DBD[LSA] = self.LSDB[LSA][0]
                        message = ["DBD",  DBD]
                        self.send_message_to_neighbor(message, router_id)
                        DBD_time = time.time()

        sys.exit(0)

    def scan_LSDB(self):
        LSA_timer = {} # {router_id: [timer, sequence]}
        scanning = True
        while scanning and self.thread_running:
            removed_id = []
            time.sleep(1)
            for router_id in self.LSDB:
                current_time = time.time()
                if router_id in LSA_timer:
                    if LSA_timer[router_id][1] != self.LSDB[router_id][0]:
                        LSA_timer[router_id] = [current_time, self.LSDB[router_id][0]]
                    if current_time - LSA_timer[router_id][0] >= 30:
                        removed_id.append(router_id)
                else:
                    LSA_timer[router_id] = [current_time, self.LSDB[router_id][0]]

            for router_id in removed_id:
                self.LSDB.pop(router_id)
                LSA_timer.pop(router_id)

            if len(removed_id):
                self.update_route()
    
        sys.exit(0)

    def run(self):
        check_neighbor_table_thread = threading.Thread(target = self.check_neighbor_table, args = ())
        scan_LSDB_thread = threading.Thread(target = self.scan_LSDB, args = ())
        check_neighbor_table_thread.start()
        scan_LSDB_thread.start()
        
        stdin_fd = sys.stdin.fileno()
        while True:
            read, _, _ = select.select([self.socket, stdin_fd], [], [], 0.1)

            for readable_socket in read:
                if readable_socket == self.socket:
                    message,address = self.socket.recvfrom(1024)
                    self.handle_receive_message(message, address)
                elif readable_socket == stdin_fd:
                    user_input = input()
                    self.handle_input(user_input)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("error: number of argv < 2")
        sys.exit()
    server_num = int(sys.argv[1])
    router1 = OSPFRouter(server_num)
    router1.run()