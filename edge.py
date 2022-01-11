import math
import threading
import random
import time
import urllib.request
import statistics

fname = ['f', 'g', 'h', 'hb']

def stat_metrics(data):
    mean = sum(data)/len(data)
    stddev = statistics.stdev(data)
    delta = 1.960 * stddev / math.sqrt(len(data) - 1)
    return mean, delta, delta/mean, stddev

def print_stat_metrics(key, executions):
    totalNumber = len(executions)
    if totalNumber == 0:
        return
    totalTime = sum(executions)
    maximum = max(executions)
    minimum = min(executions)
    print(f'{key}: \tn_exec: {totalNumber}'
          f'\tmed, delta, delperc, stddev: '
          f'{stat_metrics(executions) if totalNumber >= 2 else ""}'
          f'\tmin, max: {minimum, maximum}'
          f'\ttotal_time: {totalTime}')


def simulate_arrival():
    time.sleep(1)
    print("starting simulation arrivals")
    next_arrive = {'f': (lambda : random.expovariate(.25) + (random.random() > .875)*(random.expovariate(1/60))),
                   'g': (lambda : random.expovariate(.125) + (random.random() > .75)*(random.expovariate(1/120))),
                   'h': (lambda : random.expovariate(.125) + (random.random() > .75)*(random.expovariate(1/120))),
                   'hb': (lambda : random.expovariate(.25) + (random.random() > .875)*(random.expovariate(1/60)))}
    execution_log= {'f': {'cloud': [], 'local': []},
                    'g': {'cloud': [], 'local': []},
                    'h': {'cloud': [], 'local': []},
                    'hb': {'cloud': [], 'local': []},
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
            except:
                print("random call to "+function_name+" failed")
                error = True
            tf = time.time_ns()
            delta = tf - t0
            if not error and delta >= 0:
                execution_log[function_name][res].append(int(delta))
                execution_log[res].append(int(delta))
            else:
                execution_log['error'].append(int(delta))
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
            for key in execution_log.keys():
                if key in fname:
                    print_stat_metrics(key, execution_log[key]['cloud']+execution_log[key]['local'])
                    print_stat_metrics(key+'-cloud', execution_log[key]['cloud'])
                    print_stat_metrics(key+'-local', execution_log[key]['local'])
                else:
                    print_stat_metrics(key, execution_log[key])

        except:
            print("fail in main monitoring loop")
        finally:
            print('current: ', list(map(lambda x: current_executions[x][1], fname)))
            print('\n\n')
            t += 1
            time.sleep(1)


if __name__ == '__main__':
    simulate_arrival()
