import json
import random
import threading
import time
from datetime import datetime

class Switch:
    def __init__(self, switch_id):
        self.switch_id = switch_id
        self.flows = {}

    def add_flow(self, flow_id, flow_info):
        self.flows[flow_id] = flow_info
        print(f"[{datetime.now()}] Flow {flow_id} added to switch {self.switch_id}.")

    def remove_flow(self, flow_id):
        if flow_id in self.flows:
            del self.flows[flow_id]
            print(f"[{datetime.now()}] Flow {flow_id} removed from switch {self.switch_id}.")
        else:
            print(f"[{datetime.now()}] Flow {flow_id} not found in switch {self.switch_id}.")

    def get_flow_info(self):
        return self.flows

class Controller:
    def __init__(self):
        self.switches = {}

    def register_switch(self, switch_id):
        self.switches[switch_id] = Switch(switch_id)
        print(f"[{datetime.now()}] Switch {switch_id} registered to controller.")

    def deregister_switch(self, switch_id):
        if switch_id in self.switches:
            del self.switches[switch_id]
            print(f"[{datetime.now()}] Switch {switch_id} deregistered from controller.")
        else:
            print(f"[{datetime.now()}] Switch {switch_id} not found in controller.")

    def add_flow(self, switch_id, flow_id, flow_info):
        if switch_id in self.switches:
            self.switches[switch_id].add_flow(flow_id, flow_info)
        else:
            print(f"[{datetime.now()}] Switch {switch_id} not found.")

    def remove_flow(self, switch_id, flow_id):
        if switch_id in self.switches:
            self.switches[switch_id].remove_flow(flow_id)
        else:
            print(f"[{datetime.now()}] Switch {switch_id} not found.")

    def get_network_state(self):
        network_state = {
            switch_id: switch.get_flow_info() for switch_id, switch in self.switches.items()
        }
        return json.dumps(network_state, indent=4)

class FlowGenerator:
    def __init__(self, controller, switch_id):
        self.controller = controller
        self.switch_id = switch_id

    def generate_flow(self):
        flow_id = f"flow_{random.randint(1, 1000)}"
        flow_info = {
            "source": f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
            "destination": f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
            "protocol": random.choice(["TCP", "UDP"]),
            "priority": random.randint(1, 10),
            "action": random.choice(["ALLOW", "DENY"])
        }
        self.controller.add_flow(self.switch_id, flow_id, flow_info)

class NetworkSimulator:
    def __init__(self, controller, num_switches=5):
        self.controller = controller
        self.num_switches = num_switches

    def create_network(self):
        for i in range(self.num_switches):
            switch_id = f"switch_{i+1}"
            self.controller.register_switch(switch_id)

    def start_flow_generation(self):
        threads = []
        for switch_id in self.controller.switches:
            flow_gen = FlowGenerator(self.controller, switch_id)
            thread = threading.Thread(target=self.run_flow_generator, args=(flow_gen,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    def run_flow_generator(self, flow_gen):
        for _ in range(10):  # Generate 10 flows per switch
            flow_gen.generate_flow()
            time.sleep(random.uniform(0.5, 1.5))

    def report_network_state(self):
        print("\nCurrent Network State:")
        print(self.controller.get_network_state())

if __name__ == "__main__":
    controller = Controller()
    simulator = NetworkSimulator(controller)
    simulator.create_network()
    simulator.start_flow_generation()
    simulator.report_network_state()