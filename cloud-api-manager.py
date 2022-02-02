#!/usr/bin/python3

import os
import subprocess
import time
from flask import Flask, Response, request
import threading
import urllib.request

log = open('cloud.log', 'w+')

FNAME = 'f'
GNAME = 'g'
HNAME = 'h'
HBNAME = 'hb'
prefix = 'faas-router-'

FUNCTION_NAMES = [FNAME, GNAME, HNAME, HBNAME]

context = {}
for function_name in FUNCTION_NAMES:
    context[function_name] = {
        'ready': 0,
        'executing': 0,
        'lock': threading.Lock()
    }

app = Flask(__name__)


def get_request(function_name, wakeup=False):
    return urllib.request.urlopen('http://' + prefix +
                                  function_name +
                                  '.default.127.0.0.1.nip.io'
                                  + ('?wakeup=True' if wakeup else ''), timeout=120).read().decode('utf-8')


def monitor():
    errcnt = 0
    global context
    while True:

        try:
            running = [i.split() for i in subprocess.Popen(
                "kubectl get pods --all-namespaces --field-selector=status.phase==Running"
                " -o jsonpath=\"{.items[*].spec.containers[*].image}\" |tr -s '[["
                ":space:]]' '\n' |sort |uniq -c | grep faas-router-",
                shell=True, stdout=-1).stdout.read().decode('utf-8').split('\n')][:-1]
            aux = {}
            for r in running:
                aux[r[1]] = int(r[0])

            for function_name in FUNCTION_NAMES:
                found = False
                for k in aux.keys():
                    if (prefix + function_name + '-') in k:
                        context[function_name]['ready'] = aux[k]
                        found = True
                        break
                if not found:
                    context[function_name]['ready'] = 0
            errcnt = 0
        except:
            print('error running kubectl list pods')
            errcnt += 1
            if errcnt == 3:
                for name in FUNCTION_NAMES:
                    context[name]['ready'] = 0
        finally:
            time.sleep(.05)


def send_wakeup_request(function_name):
    try:
        get_request(function_name, wakeup=True)
    except:
        print('Error in wakeup requesto to ' + function_name)


def run_function(function_name):
    t0 = time.time_ns()
    if request.args.get('wakeup'):
        threading.Thread(
            target=send_wakeup_request, args=(function_name,)).start()
        return info()

    global context
    context[function_name]['lock'].acquire()
    context[function_name]['executing'] += 1
    context[function_name]['lock'].release()
    error = False

    try:
        get_request(function_name)
    except:
        error = True
    finally:
        context[function_name]['lock'].acquire()
        context[function_name]['executing'] -= 1
        context[function_name]['lock'].release()

        threading.Thread(target=write_log, args=(function_name, t0, time.time_ns(), error)).start()

        return Response(info(), status=500 if error else 200)

def write_log(function_name, t0, tf, error):
    log.write(str((function_name, t0, tf, error))[1:-1]+'\n')
    log.flush()


@app.route('/' + FNAME)
def f():
    return run_function(FNAME)

@app.route('/' + GNAME)
def g():
    return run_function(GNAME)

@app.route('/' + HNAME)
def h():
    return run_function(HNAME)

@app.route('/' + HBNAME)
def hb():
    return run_function(HBNAME)

@app.route('/info')
def info():
    global context
    free_instances = {}
    for function_name in FUNCTION_NAMES:
        free_instances[function_name] = context[function_name]['ready'] - context[function_name]['executing']
    return str(free_instances)


if __name__ == "__main__":
    threading.Thread(target=monitor).start()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 50005)))
