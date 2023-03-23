import random

"""
2PX3 Intersection Simulation Starting Code 

Simulation for a "cautious" intersection. Modelling choices:
1) A vehicles arrives from N, E, S, or W and must wait for other cars
ahead of them to clear the intersection.
2) Only one car can be "clearing" the intersection at once.
3) Before a car can begin to clear the intersection, it must come to a stop
4) Cars will clear the intersection in a one-at-a-time counter-clockwise manner

Dr. Vincent Maccio 2022-02-01 
"""

#Constants
ARRIVAL = "Arrival"
DEPARTURE = "Departure"
STOP = "Stop"
N = "North"
E = "East"
S = "South"
W = "West"
RIGHT = "Right"
STRAIGHT = "Straight"
LEFT = "Left"
SELF_DRIVEN = "Self Driven"
HUMAN_DRIVER = "Human Driver"
TURN_PROBABILITY = 0.25 #Probability that a new car will turn
RIGHT_PROBABILITY = 0.5 #Probability that a car that is turning will turn right
SELF_DRIVING_PROBABILITY = 0.5 #Probability a new car is self driving
MEAN_ARRIVAL_TIME = 15
PRINT_EVENTS = False
HUMAN_STOP_TIME = 5 # All of the following values should be adjusted to the desired times
SELF_DRIVEN_STOP_TIME = 4
STRAIGHT_CLEAR_TIME = 10
RIGHT_CLEAR_TIME = 11
LEFT_CLEAR_TIME = 12


class Driver:

    def __init__(self, name, arrival_time, driver_type, source, destination):
        self.name = name
        self.driver_type = driver_type
        self.arrival_time = arrival_time
        self.source = source
        self.destination = destination
        self.elapsed_time = 0
    
    #Returns driver instance stop time
    def get_stop_time(self):
        if self.driver_type == SELF_DRIVEN:
            self.stop_time = SELF_DRIVEN_STOP_TIME
        else:
            self.stop_time = HUMAN_STOP_TIME
        return self.stop_time

    #Returns driver instance clear time
    def get_clear_time(self):
        if self.destination == STRAIGHT:
            self.clear_time = STRAIGHT_CLEAR_TIME
        elif self.destination == RIGHT:
            self.clear_time = RIGHT_CLEAR_TIME
        else:
            self.clear_time = LEFT_CLEAR_TIME
        return self.clear_time


class Event:

    def __init__(self, event_type, time, direction, extra_info = None):
        self.type = event_type
        self.time = time
        self.direction = direction
        self.extra_info = extra_info # This can be used to define the desired turn direction or a type of crash, defaults to None


class EventQueue:

    def __init__(self):
        self.events = []

    #Add event (will get sent to the back of the queue)
    def add_event(self, event):
        #print("Adding event: " + event.type + ", clock: " + str(event.time))
        self.events.append(event)

    #Get the next event in the queue and pop it (remove it)
    #Returns removed next event
    def get_next_event(self):
        min_time = 9999999999999
        min_index = 0
        for i in range(len(self.events)):
            if self.events[i].time < min_time:
                min_time = self.events[i].time
                min_index = i
        event = self.events.pop(min_index)
        #print("Removing event: " + event.type + ", clock: " + str(event.time))
        return event


class Simulation:

    upper_arrival_time = 2 * MEAN_ARRIVAL_TIME

    def __init__(self, total_arrivals):
        self.num_of_arrivals = 0
        self.total_arrivals = total_arrivals
        self.clock = 0

        """
        Each road is represented as a list of waiting cars. You may
        want to consider making a "road" a class.
        """
        self.north, self.east, self.south, self.west = [], [], [], []
        self.north_ready = False
        self.east_ready = False
        self.south_ready = False
        self.west_ready = False
        self.intersection_free = True
        self.events = EventQueue()
        self.generate_arrival()
        self.print_events = PRINT_EVENTS
        self.data = []

    #Enable printing events as the simulation runs
    def enable_print_events(self):
        self.print_events = True
    
    #Method that runs the simulation
    def run(self):
        while self.num_of_arrivals <= self.total_arrivals:
            if self.print_events:
                self.print_state()
            self.execute_next_event()
            
    #Execute the next event in the queue
    #(Get next event, and execute appropriate method depending on event type)
    def execute_next_event(self):
        event = self.events.get_next_event()
        self.clock = event.time
        if event.type == ARRIVAL:
            self.execute_arrival(event)
        if event.type == DEPARTURE:
            self.execute_departure(event)
        if event.type == STOP:
            self.execute_stop(event)

    #Driver leaving intersection event
    def execute_departure(self, event):
        if self.print_events:
            print(str(self.clock)+ ": A driver from the " + event.direction + " has cleared the intersection.")

        #Lots of "traffic logic" below. It's just a counter-clockwise round-robin.
        if event.direction == N:
            
            #No drivers left to depart from the North
            if self.north == []:
                self.north_ready = False
        
            #Carry on to other direction waitlists
            if self.west_ready:
                self.depart_from(W)
            elif self.south_ready:
                self.depart_from(S)
            elif self.east_ready:
                self.depart_from(E)
            elif self.north_ready:
                self.depart_from(N)
            else:
                self.intersection_free = True

        if event.direction == E:

            #No drivers left to depart from the East
            if self.east == []:
                self.east_ready = False
        
            #Carry on to other direction waitlists
            if self.north_ready:
                self.depart_from(N)
            elif self.west_ready:
                self.depart_from(W)
            elif self.south_ready:
                self.depart_from(S)
            elif self.east_ready:
                self.depart_from(E)
            else:
                self.intersection_free = True

        if event.direction == S:

            #No drivers left to depart from the South
            if self.south == []:
                self.south_ready = False
        
            #Carry on to other direction waitlists
            if self.east_ready:
                self.depart_from(E)
            elif self.north_ready:
                self.depart_from(N)
            elif self.west_ready:
                self.depart_from(W)
            elif self.south_ready:
                self.depart_from(S)
            else:
                self.intersection_free = True

        if event.direction == W:

            #No drivers left to depart from the West
            if self.west == []:
                self.west_ready = False
        
            #Carry on to other direction waitlists
            if self.south_ready:
                self.depart_from(S)
            elif self.east_ready:
                self.depart_from(E)
            elif self.north_ready:
                self.depart_from(N)
            elif self.west_ready:
                self.depart_from(W)
            else:
                self.intersection_free = True
    
    #Create departure event for the first driver from the queue in the passed direction
    def depart_from(self, direction):
        
        #Make departure event for first car in North queue
        if direction == N:
            clear_time = self.clock + self.north[0].get_clear_time()
            new_event = Event(DEPARTURE, clear_time, N)
            driver = self.north.pop(0) #Car progessing into the intersection

        #Make departure event for first car in East queue 
        if direction == E:
            clear_time = self.clock + self.east[0].get_clear_time()
            new_event = Event(DEPARTURE, clear_time, E)
            driver = self.east.pop(0) #Car progessing into the intersection
            
        #Make departure event for first car in South queue
        if direction == S:
            clear_time = self.clock + self.south[0].get_clear_time()
            new_event = Event(DEPARTURE, clear_time, S)
            driver = self.south.pop(0) #Car progessing into the intersection

        #Make departure event for first car in West queue 
        if direction == W:
            clear_time = self.clock + self.west[0].get_clear_time()
            new_event = Event(DEPARTURE, clear_time, W)
            driver = self.west.pop(0) #Car progessing into the intersection
            
        self.events.add_event(new_event)
        self.intersection_free = False
        driver.elapsed_time = clear_time - driver.arrival_time
        self.data.append(driver)

    #Stop driver at intersection, and call depart method to add depart event to queue
    def execute_stop(self, event):
        if self.print_events:
            print(str(self.clock)+ ": A driver from the " + event.direction + " has stopped.")
        
        if event.direction == N:
            self.north_ready = True
            if self.intersection_free:
                self.depart_from(N)

        if event.direction == E:
            self.east_ready = True
            if self.intersection_free:
                self.depart_from(E)

        if event.direction == S:
            self.south_ready = True
            if self.intersection_free:
                self.depart_from(S)

        if event.direction == W:
            self.west_ready = True
            if self.intersection_free:
                self.depart_from(W)
                
    #Start arrival event 
    def execute_arrival(self, event):

        if random.random() < SELF_DRIVING_PROBABILITY:
            driver_type = SELF_DRIVEN
        else:
            driver_type = HUMAN_DRIVER
        driver = Driver(self.num_of_arrivals, self.clock, driver_type, event.direction, event.extra_info)
        if self.print_events:
            print(str(self.clock)+ ": A driver arrives from the " + event.direction + ".")

        if event.direction == N:
            if self.north == []: #Car needs to stop before clearing
                self.north_ready = False
            self.north.append(driver)
            new_event = Event(STOP, self.clock + driver.get_stop_time(), N)
            self.events.add_event(new_event)
            
        elif event.direction == E:
            if self.east == []: #Car needs to stop before clearing
                self.east_ready = False
            self.east.append(driver)
            new_event = Event(STOP, self.clock + driver.get_stop_time(), E)
            self.events.add_event(new_event)
            
        elif event.direction == S:
            if self.south == []: #Car needs to stop before clearing
                self.south_ready = False
            self.south.append(driver)
            new_event = Event(STOP, self.clock + driver.get_stop_time(), S)
            self.events.add_event(new_event)
            
        else:
            if self.west == []: #Car needs to stop before clearing
                self.west_ready = False
            self.west.append(driver)
            new_event = Event(STOP, self.clock + driver.get_stop_time(), W)
            self.events.add_event(new_event)
            
        self.generate_arrival() #Generate the next arrival

    #Generate a car arriving at the intersection
    def generate_arrival(self):
        #Generates a random number uniformily between 0 and upper_arrival_time
        inter_arrival_time = random.random() * self.upper_arrival_time
        time = self.clock + inter_arrival_time

        #Decides which direction car will travel
        if random.random() < TURN_PROBABILITY:
            if random.random() < RIGHT_PROBABILITY:
                destination = RIGHT
            else:
                destination = LEFT
        else:
            destination = STRAIGHT
            
        r = random.random()
        #Equally likely to arrive from each direction
        if r < 0.25: #From North
            self.events.add_event(Event(ARRIVAL, time, N, destination))
        elif r < 0.5: #From East
            self.events.add_event(Event(ARRIVAL, time, E, destination))
        elif r < 0.75: #From South
            self.events.add_event(Event(ARRIVAL, time, S, destination))
        else: #From West
            self.events.add_event(Event(ARRIVAL, time, W, destination))
        self.num_of_arrivals += 1 #Needed for the simulation to terminate

    def print_state(self):
        print("[N,E,S,W] = ["+ str(len(self.north)) + ","+ str(len(self.east)) +","+ str(len(self.south)) +","+ str(len(self.west)) +"]")

    def generate_report(self):
        #Define a method to generate statistical results based on the time values stored in self.data
        #These could included but are not limited to: mean, variance, quartiles, etc. 
        print()

    def output_times(self):
        times = []
        for driver in self.data:
            times.append(driver.elapsed_time)
        print(times)

    def average_time(self):
        times = []
        for driver in self.data:
            times.append(driver.elapsed_time)
        print(average(times))

        
    def output_to_csv(self):
        f = open("output.csv", 'w')
        f.write("Name,Type,Start Time,Elapsed Time,Start Direction,End Direction\n")
        for driver in self.data:
            f.write(str(driver.name) + "," + str(driver.type) + "," + str(driver.arrival_time) + "," + str(driver.elapsed_time) + "," + str(driver.source) + "," + str(driver.destination) + "\n")
        f.close()
        


def average(L):
    return sum(L)/len(L)

def main():
    sim = Simulation(1000)
    sim.run()
    sim.average_time()
    print("Done!")

main()
