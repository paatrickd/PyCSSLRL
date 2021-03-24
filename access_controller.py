# Imports
import simpy
import random
import time

# Global variables
free_servers = 10
total_reward = 0

# Random policy
def get_random_action(state):
    req_prio, free_servers = state
    if free_servers == 0:
        return 0
    else :
        return random.randint(0,1)

# Customer generation process
def create_customer(env):
    i=0
    while True:
        i += 1
        prios = [1,2,4,8]
        prio = random.sample(prios,k=1)[0]
        processing_time = random.uniform(10,30)
        c = Customer(i, prio, processing_time)
        assert free_servers >=0
        state = (prio, free_servers)
        action = get_random_action(state)
        env.process(c.cust_process(action))
        yield env.timeout(1)

class Customer:

    def __init__(self, name, priority, processing_time):
        self.name = name
        self.priority = priority
        self.processing_time = processing_time

    def cust_process(self, action):
        # refer to global variables
        global free_servers
        global total_reward

        # print(f"Customer {self.name} arrived at {env.now}")
        if action == 0:
            # print(f"Customer {self.name} with prio {self.priority} was rejected, free servers: {free_servers}")
            return
        else:
            free_servers -= 1
            yield env.timeout(self.processing_time)
            free_servers += 1

            # print(self.priority)
            # print (f"Customer {self.name} with prio {self.priority} was processed, free servers: {free_servers}, left at {env.now}")
            total_reward += self.priority

reps = 100
total_dur = 0

for i in range(0, reps):

    before = time.time()

    # Initialize simulation
    env = simpy.Environment()
    # Start the customer generation process
    env.process(create_customer(env))
    # Run for 1 hour
    env.run(until=6000)
    # Summarize total reward
    # print(f"Total reward: {total_reward}")

    dur = time.time() - before
    total_dur += dur

print('Average duration:', total_dur / reps, 'seconds.')