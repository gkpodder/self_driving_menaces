import random
import matplotlib.pyplot as plt

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
PRINT_EVENTS = True
HUMAN_STOP_TIME = 5 # All of the following values should be adjusted to the desired times
SELF_DRIVEN_STOP_TIME = 4
STRAIGHT_CLEAR_TIME = 10
RIGHT_CLEAR_TIME = 11
LEFT_CLEAR_TIME = 12
xpoints = []
ypoints = []



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
        self.vertical, self.horizontal = [], []
        self.vertical_ready = False
        self.horizontal_ready = False
        self.intersection_free = True
        self.events = EventQueue()
        self.generate_arrival() #generate a car arriving at the intersection
        self.print_events = PRINT_EVENTS
        self.data = []

    #Enable printing events as the simulation runs
    def enable_print_events(self):
        self.print_events = True
    
    #Method that runs the simulation
    def run(self):
        while self.num_of_arrivals <= self.total_arrivals:
            # print("Executing new event: ")
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

        #Lots of "traffic logic" below. It's just a counter-clockwise round-robin.
        if event.direction == N or event.direction == S:
            if self.print_events: 
                print("departing from north and south")
            
            #No drivers left to depart from the North
            if self.vertical == []:
                if self.print_events: 
                    print("no drivers left to depart from the north/south")
                self.vertical_ready = False
        
            #Carry on to other direction waitlists
            if self.horizontal_ready:
                if self.print_events:
                    print("departing from west/east")
                self.depart_from(W)
            else:
                self.intersection_free = True

        
    
        if event.direction == E or event.direction == W:

            #No drivers left to depart from the East
            if self.horizontal == []:
                if self.print_events: 
                    print("no drivers left in horizontal direction to depart from east/west")
                self.horizontal_ready = False
        
            #Carry on to other direction waitlists
            if self.vertical_ready:
                if self.print_events:
                    print("departing from north/south next")
                self.depart_from(N)
            else:
                # print("intersection is free")
                self.intersection_free = True

           


    #Create departure event for the first driver from the queue in the passed direction
    def depart_from(self, direction):
        
        #Make departure event for first car in North queue
        if direction == N or direction == S:
            if(self.vertical): 
                clear_time = self.clock + self.vertical[0].get_clear_time()
                new_event = Event(DEPARTURE, clear_time, N)

                while len(self.vertical) != 0:  #pop everything in one direction 
                    driver = self.vertical.pop(0) #Car progessing into the intersection
                    driver.elapsed_time = clear_time - driver.arrival_time #how long it takes for the driver to clear the intersection
                    self.data.append(driver.elapsed_time) 

                if self.print_events: 
                    print("all drivers in vertical direction are passing through")
                    self.print_state()



        #Make departure event for first car in East queue 
        if direction == E or direction == W:
            if(self.horizontal): 
                clear_time = self.clock + self.horizontal[0].get_clear_time()
                new_event = Event(DEPARTURE, clear_time, E)

            
                while len(self.horizontal) != 0:  #pop everything in one direction 
                    driver = self.horizontal.pop(0) #Car progessing into the intersection
                    driver.elapsed_time = clear_time - driver.arrival_time #how long it takes for the driver to clear the intersection
                    self.data.append(driver.elapsed_time)
             
                
                if self.print_events: 
                    print("all drivers in horizontal direction are passing through")
                    self.print_state()
            
        
        self.events.add_event(new_event)
        # print("adding (next?) departure event to queue")
        self.intersection_free = False
        # print("intersection free set to false")
        
       

    #Stop driver at intersection, and call depart method to add depart event to queue
    #Only creates depart event if intersection is free
    def execute_stop(self, event):
        if self.print_events:
            print(str(self.clock)+ ": A driver from the " + event.direction + " has stopped.")
            self.print_state()
        
        if event.direction == N:
            self.vertical_ready = True
            if self.intersection_free:
                # print("INTERSECTION IS FREE, CREATING DEPARTURE EVENT")
                self.depart_from(N)
            # else: 
                # print("INTERSECTION NOT FREE, CAR CAN'T DEPART AND IS STILL STOPPING ")

        if event.direction == E:
            self.horizontal_ready = True
            if self.intersection_free:
                # print("INTERSECTION IS FREE, CREATING DEPARTURE EVENT")
                self.depart_from(E)
            # else: 
            #     print("INTERSECTION NOT FREE, CAR CAN'T DEPART ")
            

        if event.direction == S:
            self.vertical_ready = True
            if self.intersection_free:
                # print("INTERSECTION IS FREE, CREATING DEPARTURE EVENT")
                self.depart_from(S)
            # else: 
            #     print("INTERSECTION NOT FREE, CAR CAN'T DEPART ")

        if event.direction == W:
            self.horizontal_ready = True
            if self.intersection_free:
                # print("INTERSECTION IS FREE, CREATING DEPARTURE EVENT")
                self.depart_from(W)
            # else: 
            #     print("INTERSECTION NOT FREE, CAR CAN'T DEPART ")
                
    #Start arrival event 
    def execute_arrival(self, event):

        if self.print_events:
            print(str(self.clock)+ ": A driver arrives from the " + event.direction + ".")

        if random.random() < SELF_DRIVING_PROBABILITY:
            driver_type = SELF_DRIVEN
        else:
            driver_type = HUMAN_DRIVER
        driver = Driver(self.num_of_arrivals, self.clock, driver_type, event.direction, event.extra_info)

        if event.direction == N:
            if self.vertical == []: #Car needs to stop before clearing
                self.vertical_ready = False
            self.vertical.append(driver)
            if self.print_events:
                self.print_state()
            new_event = Event(STOP, self.clock + driver.get_stop_time(), N)
            # print("adding stop event")
            self.events.add_event(new_event)

        elif event.direction == S:
            if self.vertical == []: #Car needs to stop before clearing
                self.vertical_ready = False
            self.vertical.append(driver)
            if self.print_events:
                self.print_state()
            new_event = Event(STOP, self.clock + driver.get_stop_time(), S)
            # print("adding stop event")
            self.events.add_event(new_event)
        
            
        elif event.direction == E:
            if self.horizontal == []: #Car needs to stop before clearing
                self.horizontal_ready = False
            self.horizontal.append(driver)
            if self.print_events:
                self.print_state()
            new_event = Event(STOP, self.clock + driver.get_stop_time(), E)
            # print("adding stop event")
            self.events.add_event(new_event)

        elif event.direction == W:
            if self.horizontal == []: #Car needs to stop before clearing
                self.horizontal_ready = False
            self.horizontal.append(driver)
            if self.print_events:
                self.print_state()
            new_event = Event(STOP, self.clock + driver.get_stop_time(), W)
            # print("adding stop event")
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
        print("[N/S, E/W] = ["+ str(len(self.vertical)) + ","+ str(len(self.horizontal)) +"]")

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

#Graph of average clear time vs number of arrivals on the system
def makeClearTimeGraph():
    numOfArrivals = 0 
    avg_clear = []
    ypoints.clear
    xpoints.clear

    
    for _ in range(20):
        numOfArrivals += 1000 
        sim = Simulation(numOfArrivals)

        for _ in range(100):
            sim.run()
            avg_clear.append(average(sim.data))

        ypoints.append(average(avg_clear))
        xpoints.append(numOfArrivals)
    
    plt.plot(xpoints, ypoints)
    plt.show()
        


def average(L):
    return sum(L)/len(L)

def main():
    sim = Simulation(10)
    sim.run()
    # sim.average_time()
    print("Done!")


main()
