import random

def calculate_time(setting, hosts):
    
    success_time = 0
    idle_time = 0
    collision_time = 0
    for time in range(setting.total_time):
        check_idle = True
        check_success = False
        for host_idx in hosts:
            if host_idx["history"][time] == ">":
                check_success = True
            if host_idx["history"][time] != ".":
                check_idle = False
        if check_success:
            success_time += setting.packet_time
        if check_idle:
            idle_time += 1
    
    collision_time = setting.total_time - idle_time - success_time

    return (success_time / setting.total_time,
            idle_time / setting.total_time,
            collision_time / setting.total_time)

def aloha(setting, show_history = False):
    hosts = [
        {
            "id": i,
            "status": 0,         # 0: idle, 1: start sending, 2: send, 3: finish sending
            "packet_num_sending": 0,   
            "remain_time_to_send": 0,  # remain time to sending
            "wait_time": 0,      # time wait to send
            "collision": False,
            "success_num": 0,
            "collision_num": 0,
            "packets_arrive": "    ",
            "history": "",       # record history of host's actions
        }
        for i in range(setting.host_num)
    ]
    packets = setting.gen_packets()

    num_hosts_sending = []

    for current_time in range(setting.total_time):
        # 如果有封包 packet_num_sending += 1
        for host_idx in hosts:
            if len(packets[host_idx["id"]]) > 0 and packets[host_idx["id"]][0] == current_time:
                packets[host_idx["id"]].pop(0)
                host_idx["packets_arrive"] += "v"
                host_idx["packet_num_sending"] += 1
            else:
                host_idx["packets_arrive"] += " "
            # 如果沒有封包要送
            if host_idx["packet_num_sending"] == 0:
                host_idx["status"] = 0
            # 如果有封包正在送或者需要送
            else:
                # 如果不用等
                if host_idx["wait_time"] == 0:
                    # 正要送
                    if host_idx["status"] == 0 or host_idx["status"] == 3 or host_idx["status"] == 4:
                        host_idx["status"] = 1
                    # 正在送
                    elif host_idx["remain_time_to_send"] > 1:
                        host_idx["status"] = 2
                    # 送完了
                    else:
                        host_idx["status"] = 3

                    host_idx["remain_time_to_send"] -= 1
                #如果還在等(因為發生過碰撞)
                else:
                    host_idx["wait_time"] -= 1
                    host_idx["status"] = 0
        # 碰撞偵測
        num_hosts_sending.clear()
        for host_idx in hosts:
            if host_idx["status"] > 0:
                num_hosts_sending.append(host_idx["id"])
        if len(num_hosts_sending) > 1:
            for host_idx in hosts:
                if host_idx["id"] in num_hosts_sending:
                    host_idx["collision"] = True

        # history
        for host_idx in hosts:
            if host_idx["status"] == 0:
                host_idx["history"] += "."
            elif host_idx["status"] == 1:
                host_idx["history"] += "<"
                host_idx["remain_time_to_send"] += setting.packet_time
            elif host_idx["status"] == 2:
                host_idx["history"] += "-"
            elif host_idx["status"] == 3:
                if host_idx["collision"]:
                    host_idx["history"] += "|"
                    host_idx["collision"] = False
                    host_idx["wait_time"] = random.randint(0, setting.max_collision_wait_time)
                else:
                    host_idx["history"] += ">"
                    host_idx["collision"] = False
                    host_idx["packet_num_sending"] -= 1

    if show_history:
        for host_idx in hosts:
            print(host_idx["packets_arrive"])
            print(host_idx["id"], ": " + host_idx["history"])

    return calculate_time(setting, hosts)


def slotted_aloha(setting, show_history = False):
    hosts = [
        {
            "id": i,
            "status": 0,         # 0: idle, 1: start sending, 2: send, 3: finish sending
            "packet_num_sending": 0,
            "collision": False,
            "resend": False,
            "success_num": 0,
            "collision_num": 0,
            "packets_arrive": "    ",
            "history": "",       # record history of host's actions
        }
        for i in range(setting.host_num)
    ]
    packets = setting.gen_packets()
    num_hosts_sending = []
    
    for current_time in range(0, setting.total_time):
        # 如果有封包 packet_num_sending += 1
        for host_idx in hosts:
            if len(packets[host_idx["id"]]) > 0 and packets[host_idx["id"]][0] == current_time:
                packets[host_idx["id"]].pop(0)
                host_idx["packets_arrive"] += "v"
                host_idx["packet_num_sending"] += 1
            else:
                host_idx["packets_arrive"] += " "

            # 經過一個 slot
            if current_time % setting.packet_time == 0:
                # 如果沒有封包要送
                if host_idx["packet_num_sending"] == 0:
                    host_idx["status"] = 0
                # 如果有封包需要送
                else:
                    if host_idx["resend"]:
                        probability = random.random()
                        if probability <= setting.p_resend:
                            host_idx["status"] = 1
                        else:
                            host_idx["status"] = 0
                    else:
                        host_idx["status"] = 1
            # 正在送封包
            else:
                if host_idx["status"] == 1:
                    host_idx["status"] = 2
                elif host_idx["status"] == 2 and current_time % setting.packet_time == setting.packet_time - 1:
                    host_idx["status"] = 3
        # 碰撞偵測
        num_hosts_sending.clear()
        for host_idx in hosts:
            if host_idx["status"] > 0:
                num_hosts_sending.append(host_idx["id"])
        if len(num_hosts_sending) > 1:
            for host_idx in hosts:
                if host_idx["id"] in num_hosts_sending:
                    host_idx["collision"] = True

        # history
        for host_idx in hosts:
            if host_idx["status"] == 0:
                host_idx["history"] += "."
            elif host_idx["status"] == 1:
                host_idx["history"] += "<"
            elif host_idx["status"] == 2:
                host_idx["history"] += "-"
            elif host_idx["status"] == 3:
                if host_idx["collision"]:
                    host_idx["history"] += "|"
                    host_idx["collision"] = False
                    host_idx["resend"] = True
                else:
                    host_idx["history"] += ">"
                    host_idx["collision"] = False
                    host_idx["resend"] = False
                    host_idx["packet_num_sending"] -= 1

    if show_history:
        for host_idx in hosts:
            print(host_idx["packets_arrive"])
            print(host_idx["id"], ": " + host_idx["history"])

    return calculate_time(setting, hosts)


def csma(setting, one_persistent = False, show_history = False):
    hosts = [
        {
            "id": i,
            "status": 0,         # 0: idle, 1: start sending, 2: send, 3: finish sending
            "packet_num_sending": 0,   
            "remain_time_to_send": 0,  # remain time to sending
            "wait_time": 0,      # time wait to send
            "collision": False,
            "success_num": 0,
            "collision_num": 0,
            "packets_arrive": "    ",
            "history": "",       # record history of host's actions
        }
        for i in range(setting.host_num)
    ]
    packets = setting.gen_packets()
    
    num_hosts_sending = []

    for current_time in range(setting.total_time):
        # 如果有封包 packet_num_sending += 1
        for host_idx in hosts:
            if len(packets[host_idx["id"]]) > 0 and packets[host_idx["id"]][0] == current_time:
                packets[host_idx["id"]].pop(0)
                host_idx["packets_arrive"] += "v"
                host_idx["packet_num_sending"] += 1
            else:
                host_idx["packets_arrive"] += " "
            # 如果沒有封包要送
            if host_idx["packet_num_sending"] == 0:
                host_idx["status"] = 0
            # 如果有封包正在送或者需要送
            else:
                # 如果不用等
                if host_idx["wait_time"] == 0:
                    if host_idx["status"] == 0 or host_idx["status"] == 3:
                        # 先聽
                        collision_detect = False
                        for other_host in hosts:
                            if other_host == host_idx:
                                continue
                            if current_time - setting.link_delay - 1 >= 0:
                                if other_host["history"][current_time - setting.link_delay - 1] != "." and other_host["history"][current_time - setting.link_delay - 1] != ">":
                                    collision_detect = True
                        # 若會發生碰撞則等待
                        if collision_detect:
                            host_idx["wait_time"] = random.randint(0, setting.max_collision_wait_time)
                            host_idx["status"] = 0
                        # 不會發生碰撞則直接送
                        else:
                            host_idx["status"] = 1
                            host_idx["remain_time_to_send"] -= 1
                    # 正在送
                    elif host_idx["remain_time_to_send"] > 1:
                        host_idx["status"] = 2
                        host_idx["remain_time_to_send"] -= 1
                    # 送完了
                    else:
                        host_idx["status"] = 3
                        host_idx["remain_time_to_send"] -= 1
                #如果還在等(因為發生過碰撞)
                else:
                    host_idx["wait_time"] -= 1
                    host_idx["status"] = 0
        # 碰撞偵測
        num_hosts_sending.clear()
        for host_idx in hosts:
            if host_idx["status"] > 0:
                num_hosts_sending.append(host_idx["id"])
        if len(num_hosts_sending) > 1:
            for host_idx in hosts:
                if host_idx["id"] in num_hosts_sending:
                    host_idx["collision"] = True

        # history
        for host_idx in hosts:
            if host_idx["status"] == 0:
                host_idx["history"] += "."
            elif host_idx["status"] == 1:
                host_idx["history"] += "<"
                host_idx["remain_time_to_send"] += setting.packet_time
            elif host_idx["status"] == 2:
                host_idx["history"] += "-"
            elif host_idx["status"] == 3:
                if host_idx["collision"]:
                    host_idx["history"] += "|"
                    host_idx["collision"] = False
                    host_idx["wait_time"] = random.randint(0, setting.max_collision_wait_time)
                else:
                    host_idx["history"] += ">"
                    host_idx["collision"] = False
                    host_idx["packet_num_sending"] -= 1

    if show_history:
        for host_idx in hosts:
            print(host_idx["packets_arrive"])
            print(host_idx["id"], ": " + host_idx["history"])

    return calculate_time(setting, hosts)

def csma_cd(setting, one_persistent = False, show_history = False):
    hosts = [
        {
            "id": i,
            "status": 0,         # 0: idle, 1: start sending, 2: send, 3: finish sending
            "packet_num_sending": 0,   
            "remain_time_to_send": 0,  # remain time to sending
            "wait_time": 0,      # time wait to send
            "collision": False,
            "success_num": 0,
            "collision_num": 0,
            "packets_arrive": "    ",
            "history": "",       # record history of host's actions
        }
        for i in range(setting.host_num)
    ]
    packets = setting.gen_packets()
    
    num_hosts_sending = []

    for current_time in range(setting.total_time):
        # 如果有封包 packet_num_sending += 1
        for host_idx in hosts:
            if len(packets[host_idx["id"]]) > 0 and packets[host_idx["id"]][0] == current_time:
                packets[host_idx["id"]].pop(0)
                host_idx["packets_arrive"] += "v"
                host_idx["packet_num_sending"] += 1
            else:
                host_idx["packets_arrive"] += " "
            # 如果沒有封包要送
            if host_idx["packet_num_sending"] == 0:
                host_idx["status"] = 0
            # 如果有封包正在送或者需要送
            else:
                # 如果不用等
                if host_idx["wait_time"] == 0:
                    if host_idx["status"] == 0 or host_idx["status"] == 3:
                        # 先聽
                        collision_detect = False
                        for other_host in hosts:
                            if other_host == host_idx:
                                continue
                            if current_time - setting.link_delay - 1 >= 0:
                                if other_host["history"][current_time - setting.link_delay - 1] != "." and other_host["history"][current_time - setting.link_delay - 1] != ">":
                                    collision_detect = True
                        # 若會發生碰撞則等待
                        if one_persistent == False and collision_detect:
                            host_idx["wait_time"] = random.randint(0, setting.max_collision_wait_time)
                            host_idx["status"] = 0
                        # 不會發生碰撞則直接送
                        else:
                            host_idx["status"] = 1
                            host_idx["remain_time_to_send"] -= 1
                    # 正在送
                    elif host_idx["remain_time_to_send"] > 1:
                        # 碰撞偵測
                        for other_host in hosts:
                            if host_idx == other_host:
                                continue
                            if other_host["history"][current_time - setting.link_delay - 1] != "." and other_host["history"][current_time - setting.link_delay - 1] != ">":
                                host_idx["collision"] = True
                        if host_idx["collision"]:
                            host_idx["status"] = 3
                            host_idx["remain_time_to_send"] = 0
                        else:
                            host_idx["status"] = 2
                            host_idx["remain_time_to_send"] -= 1
                    # 送完了
                    else:
                        host_idx["status"] = 3
                        host_idx["remain_time_to_send"] -= 1
                #如果還在等(因為發生過碰撞)
                else:
                    host_idx["wait_time"] -= 1
                    host_idx["status"] = 0

        # history
        for host_idx in hosts:
            if host_idx["status"] == 0:
                host_idx["history"] += "."
            elif host_idx["status"] == 1:
                host_idx["history"] += "<"
                host_idx["remain_time_to_send"] += setting.packet_time
            elif host_idx["status"] == 2:
                host_idx["history"] += "-"
            elif host_idx["status"] == 3:
                if host_idx["collision"]:
                    host_idx["history"] += "|"
                    host_idx["collision"] = False
                    host_idx["wait_time"] = random.randint(0, setting.max_collision_wait_time)
                else:
                    host_idx["history"] += ">"
                    host_idx["collision"] = False
                    host_idx["packet_num_sending"] -= 1

    if show_history:
        for host_idx in hosts:
            print(host_idx["packets_arrive"])
            print(host_idx["id"], ": " + host_idx["history"])

    return calculate_time(setting, hosts)