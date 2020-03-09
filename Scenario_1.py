''''
This is Scenario 1

'''

import random
import simpy

balk_limit = 5
mean_order_time = 2.0
mean_pickup_time = 2.0
mean_preparation_time = 5.0
close_time = 180.0 ### Using a 3 hours window
balk_out_count = 0 ### This variable keeps track of the number of customers who left the system
total_cars = 0 ### This variable keeps track of the total through put of the cars
mean_interarrival_time = 1.7


def cars_arrival(env, mean_interarrival_time , res):
    global balk_out_count
    global total_cars
    car_number = 1

    while (env.now <= close_time):

        print("Arrival occurs at time %5.3f" % (env.now))
        env.process(process_unit(env, car_number, mean_order_time, mean_pickup_time,  res))
        car_number += 1
        interarrival_time = random.expovariate(1.0 / mean_interarrival_time)
        yield env.timeout(interarrival_time)
    total_cars = car_number



def process_unit(env, car_number, mean_order_time, mean_pickup_time, res):
    global balk_out_count
    global total_cars
    wait_count1 = len(res[0].queue) ## This variable counts the number of cars waiting for order station 1
    wait_count2 = len(res[1].queue) ### This variable counts the number of cars waiting for order station 2

    print("the wait is", wait_count1, wait_count2)

    if ((wait_count1 <  balk_limit) | (wait_count2 < balk_limit)):
        if wait_count1 <= wait_count2:

            r1 = res[0].request()
            print("Car %d requests a unit of order station 1 at time %5.3f" % (car_number, env.now))
            yield r1

            print("Car %d acquired a unit of order station 1 at time %5.3f" % (car_number, env.now))
            order_time = random.expovariate(1.0 / mean_order_time)
            yield env.timeout(order_time)

            time_point = env.now
            prepare_time = random.expovariate(1.0 / mean_preparation_time)

            r2 = res[2].request()
            print("Car %d requests a unit of pickup wait line at time %5.3f" % (car_number, env.now))
            yield r2

            res[0].release(r1)
            print("Car %d released a unit of order station 1 at time %5.3f" % (car_number, env.now))
        else :
            r1 = res[1].request()
            print("Car %d requests a unit of order station 2 at time %5.3f" % (car_number, env.now))
            yield r1

            print("Car %d acquired a unit of order station 2 at time %5.3f" % (car_number, env.now))
            order_time = random.expovariate(1.0 / mean_order_time)
            yield env.timeout(order_time)

            time_point = env.now
            prepare_time = random.expovariate(1.0 / mean_preparation_time)

            r2 = res[2].request()
            print("Car %d requests a unit of pickup wait line at time %5.3f" % (car_number, env.now))
            yield r2

            res[1].release(r1)
            print("Car %d released a unit of order station 2 at time %5.3f" % (car_number, env.now))


        print("Car %d acquired a unit of pickup wait line at time %5.3f" % (car_number, env.now))

        r3 = res[3].request()
        print("Car %d requests a unit of pickup window at time %5.3f" % (car_number, env.now))

        yield r3

        res[2].release(r2)
        print("Car %d released a unit of pickup wait line at time %5.3f" % (car_number, env.now))


        print("Car %d acquired a unit of pickup window at time %5.3f" % (car_number, env.now))

        if ((env.now - time_point) >= prepare_time): #### In order to catch the food preparation delay
            timeout = 0 ### No delay and the food is ready when we approach the pick up window
        else:
            timeout = prepare_time - (env.now - time_point) ### This much is the delay if the food is not ready when we approach the pick up window

        yield env.timeout(timeout)

        pickup_time = random.expovariate(1.0 / mean_pickup_time)
        yield env.timeout(pickup_time)

        res[3].release(r3)
        print("Car %d released a unit of pickup window and exists the system at time %5.3f" % (car_number, env.now))
    else:
        print ("Car %d balked at time %5.3f" % (car_number, env.now))
        balk_out_count += 1

seed_value = [12324, 456554, 234324] ### Replicating the simulation over different seeds
car_matrix = [0, 0, 0]  #### This will show total through put per 180.00 minutes
balk_out_matrix = [0, 0, 0] ### This will show total number of cars that left the system per 180.00 minutes
for replicate in range(3):

    random_seed = seed_value[replicate]
    #Setup and start Simulation

    print("Scenario 1 Started")
    random.seed(random_seed)

    #Create Environment
    env = simpy.Environment()

    #Start processes and run

    order_station_1 = simpy.Resource(env, 1)
    order_station_2 = simpy.Resource(env, 1)
    pickup_wait_line = simpy.Resource(env, 6)
    pickup_window = simpy.Resource(env,1)

    res = [order_station_1, order_station_2, pickup_wait_line, pickup_window]

    env.process(cars_arrival(env, mean_interarrival_time , res))
    #Start the simulation
    env.run()
    car_matrix[replicate] = total_cars
    balk_out_matrix[replicate] = balk_out_count
print("The mean_interarrival_time is: " , mean_interarrival_time)
print("Total through put : " , (car_matrix))
print("Total number of cars balked : " , (balk_out_matrix))