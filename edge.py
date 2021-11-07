import threading
import random
import time
import urllib.request


def simulate_arrival():
    time.sleep(1)
    print("starting simulation arrivals")
    next_arrive = {'f': (lambda : random.expovariate(10)),
                   'g': (lambda : random.expovariate(1)),
                   'h': (lambda : random.expovariate(1)),
                   'hb': (lambda : random.expovariate(10))}
    execution_history = {'f': [], 'g': [], 'h': [], 'hb': []}
    current_executions = {'f': [threading.Lock(), 0],
                          'g': [threading.Lock(), 0],
                          'h': [threading.Lock(), 0],
                          'hb': [threading.Lock(), 0]}

    def atomic_modify(function_name, value):
        current_executions[function_name][0].acquire()
        current_executions[function_name][1] += value
        current_executions[function_name][0].release()

    def random_caller(function_name):
        def caller(function_name):
            atomic_modify(function_name, 1)
            t0 = time.time_ns()
            try:
                urllib.request.urlopen("http://localhost:5000/"+function_name)
            except Exception as e:
                print("random call to "+function_name+" failed")
                print(e)
            tf = time.time_ns()
            execution_history[function_name].append(tf-t0)
            atomic_modify(function_name, -1)

        while True:
            threading.Thread(target=caller, args=(function_name,)).start()
            time.sleep(next_arrive[function_name]())

    threading.Thread(target=random_caller, args=('f',)).start()
    threading.Thread(target=random_caller, args=('g',)).start()
    threading.Thread(target=random_caller, args=('h',)).start()
    threading.Thread(target=random_caller, args=("hb",)).start()

    t = 0
    while True:
        print(f'---------------------------------\nIteration:{t}')
        for key in execution_history.keys():
            executions = execution_history[key]
            totalNumber = len(executions)
            if totalNumber == 0:
                continue
            totalTime = sum(executions)
            meanTime = totalTime / totalNumber
            maximum = max(executions)
            minimum = min(executions)
            print(f'{key}: \tn_exec: {totalNumber}'
                  f'\tmean_time: {meanTime}'
                  f'\tmaximum: {maximum}'
                  f'\tminimum: {minimum}'
                  f'\ttime_exec: {totalTime}')
        print('current: ', list(map(lambda x: current_executions[x][1], ['f', 'g', 'h', 'hb'])))
        print('\n\n')
        t += 1
        time.sleep(1)

if __name__ == '__main__':
    simulate_arrival()