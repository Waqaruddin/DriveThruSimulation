'''
This is Scenario 2

'''

import random
import simpy

balk_limit = 5
mean_order_time = 1.5
mean_pickup_time = 1.0
mean_preparation_time = 5.0
close_time = 180.0 ### Using a 3 hours window
balk_out_count = 0 ### This variable keeps track of the number of customers who left the system
total_cars = 0  ### This variable keeps track of the total through put of the cars
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
    wait_count1 = len(res[0].users) ## This variable counts the number of cars waiting to approach the server 1
    wait_count2 = len(res[1].users) ### This variable counts the number of cars waiting to approach the server 2

    print("the numbers of car in the wait lines is", wait_count1, wait_count2)

    if ((wait_count1 <  balk_limit) | (wait_count2 < balk_limit)):
        if wait_count1 <= wait_count2:

            r1 = res[0].request()
            print("Car %d requests a unit of order station 1 line at time %5.3f" % (car_number, env.now))
            yield r1
            print("Car %d acquired a unit of order station 1 line at time %5.3f" % (car_number, env.now))

            print("Car %d requests a unit of waiter of station 1 at time %5.3f" % (car_number, env.now))
            rwaiter = res[4].request()
            yield rwaiter

            order_time = random.expovariate(1.0 / mean_order_time)
            yield env.timeout(order_time)

            res[4].release(rwaiter)
            time_point = env.now
            prepare_time = random.expovariate(1.0 / mean_preparation_time)
            print("Car %d released a unit of waiter of station 1 at time %5.3f" % (car_number, env.now))
            r2 = res[2].request()
            print("Car %d requests a unit of pickup wait line at time %5.3f" % (car_number, env.now))
            yield r2

            res[0].release(r1)
            print("Car %d released a unit of order station 1 at time %5.3f" % (car_number, env.now))
        else :
            r1 = res[1].request()
            print("Car %d requests a unit of order station 2 line at time %5.3f" % (car_number, env.now))
            yield r1
            print("Car %d acquired a unit of order station 2 line at time %5.3f" % (car_number, env.now))

            print("Car %d requests a unit of waiter of station 2 at time %5.3f" % (car_number, env.now))
            rwaiter = res[5].request()
            yield rwaiter

            order_time = random.expovariate(1.0 / mean_order_time)
            yield env.timeout(order_time)

            res[5].release(rwaiter)
            time_point = env.now
            prepare_time = random.expovariate(1.0 / mean_preparation_time)

            res[4].release(rwaiter)
            print("Car %d released a unit of waiter of station 2 at time %5.3f" % (car_number, env.now))
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

        if ((env.now-time_point) >= prepare_time) :
               timeout = 0
        else:
               timeout = prepare_time - (env.now-time_point)

        yield env.timeout(timeout)


        pickup_time = random.expovariate(1.0 / mean_pickup_time)
        yield env.timeout(pickup_time)

        res[3].release(r3)
        print("Car %d released a unit of pickup window and exists the system at time %5.3f" % (car_number, env.now))
    else:
        print ("Car %d balked at time %5.3f" % (car_number, env.now))
        balk_out_count += 1

seed_value = [12324, 456554, 234324] ### Replicating the simulation over different seeds
car_matrix = [0, 0, 0]
balk_out_matrix = [0, 0, 0]
for replicate in range(3):

    random_seed = seed_value[replicate]
    #Setup and start Simulation

    print("Scenario 1 Started")
    random.seed(random_seed)

    #Create Environment
    env = simpy.Environment()

    #Start processes and run

    order_station_1_line = simpy.Resource(env, 5)
    order_station_2_line = simpy.Resource(env, 5)
    waiter1 = simpy.Resource(env, 1)
    waiter2 = simpy.Resource(env, 1)
    pickup_wait_line = simpy.Resource(env, 6)
    pickup_window = simpy.Resource(env,1)

    res = [order_station_1_line, order_station_2_line, pickup_wait_line, pickup_window, waiter1, waiter2]

    env.process(cars_arrival(env, mean_interarrival_time, res))
    #Start the simulation
    env.run()
    car_matrix[replicate] = total_cars
    balk_out_matrix[replicate] = balk_out_count
print("The mean_interarrival_time is: ", mean_interarrival_time)
print("Total go though out cars number is : ", (car_matrix))
print("Total balk out number is : ", (balk_out_matrix))