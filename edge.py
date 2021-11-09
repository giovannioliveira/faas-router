import math
import threading
import random
import time
import urllib.request
import statistics

def stat_metrics(data):
    mean = sum(data)/len(data)
    if (mean < 0):
        print(data)
        exit(0)
    stddev = statistics.stdev(data)
    delta = 1.960 * stddev / math.sqrt(len(data) - 1)
    return mean, mean - delta, mean + delta, delta/mean, stddev

def simulate_arrival():
    time.sleep(1)
    print("starting simulation arrivals")
    next_arrive = {'f': (lambda : random.expovariate(.25) + (random.random() > .875)*(random.expovariate(1/60))),
                   'g': (lambda : random.expovariate(.125) + (random.random() > .75)*(random.expovariate(1/120))),
                   'h': (lambda : random.expovariate(.125) + (random.random() > .75)*(random.expovariate(1/120))),
                   'hb': (lambda : random.expovariate(.25) + (random.random() > .875)*(random.expovariate(1/60)))}
    execution_history = {'f': [], 'g': [], 'h': [], 'hb': [],
                         'error': [], 'cloud': [], 'local': [], }
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
            error = False
            res = None
            try:
                res = urllib.request.urlopen("http://localhost:5000/"+function_name,
                                       timeout=120).read().decode('utf-8')
            except Exception as e:
                print("random call to "+function_name+" failed:", e)
                error = True
            tf = time.time_ns()
            delta = tf - t0
            if not error and delta >= 0:
                execution_history[function_name].append(int(delta))
                execution_history[res].append(int(delta))
            elif delta < 0:
                print("Delta is minor than zero !!!")
                execution_history['error'].append(int(delta))
            else:
                execution_history['error'].append(int(delta))
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
        try:
            print(f'---------------------------------\nIteration:{t}')
            for key in execution_history.keys():
                executions = execution_history[key]
                totalNumber = len(executions)
                if totalNumber == 0:
                    continue
                totalTime = sum(executions)
                maximum = max(executions)
                minimum = min(executions)
    
                print(f'{key}: \tn_exec: {totalNumber}'
                      f'\tmed, medl, medh, delperc, stddev: '
                      f'{stat_metrics(executions) if totalNumber >= 2 else ""}'
                      f'\tmin, max: {minimum, maximum}'
                      f'\ttotal_time: {totalTime}')
            print('current: ', list(map(lambda x: current_executions[x][1], ['f', 'g', 'h', 'hb'])))
            print('\n\n')
        except:
            print("fail in main monitoring loop")
        finally:    
            t += 1
            time.sleep(1)


if __name__ == '__main__':
    simulate_arrival()
