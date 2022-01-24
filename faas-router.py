import time
from flask import Flask, Response
import urllib.request
import threading

from functions.f import app as _f
from functions.g import app as _g
from functions.h import app as _h
from functions.hb import app as _hb

functions = {
    'f': _f.f,
    'g': _g.f,
    'h': _h.f,
    'hb': _hb.f
}
remoteCount = {}
REMOTE_SERVER = "http://200.144.244.220:8081"
app = Flask(__name__)
rcLock = threading.Lock()

log = open('router.log', 'w+')

def write_log(function_name, t0, tf, cloud,error):
    log.write(str((function_name, t0, tf, cloud, error))[1:-1]+'\n')
    log.flush()


def set_remote_count(newCountStr, fromAsync=False):
    rcLock.acquire()
    global remoteCount
    try:
        remoteCount = eval(newCountStr)
    except:
        print('error setting remote count')
    rcLock.release()
    print(('async ' if fromAsync else '') + 'set remote count: ', remoteCount)


def async_set_remote_count(newCountStr):
    threading.Thread(target=set_remote_count, args=(newCountStr,)).start()

def atomic_increment_remote_count(function_name,inc):
    rcLock.acquire()
    remoteCount[function_name] += inc
    rcLock.release()
    print("local remote count update: ", str(remoteCount))

def async_increment_remote_count(function_name, inc):
    threading.Thread(target=atomic_increment_remote_count, args=(function_name, inc)).start()

def reset_remote_count():
    set_remote_count(str({('faas-router-'+fname):0 for fname in functions.keys()}))


def get_request(sufix):
    return urllib.request.urlopen(REMOTE_SERVER+sufix, timeout=120).read().decode('utf-8')


def signal_remote_scale_up(function_name):
    try:
        set_remote_count(get_request("/"+function_name+"?wakeup=true"), True)
    except:
        print('async update failed for '+function_name)


def update_remote_count():
    errcnt = 0
    while True:
        try:
            set_remote_count(get_request("/info"))
            errcnt = 0
        except Exception as e:
            errcnt += 1
            if errcnt == 3:
                reset_remote_count()
            print('Error in connection with remote cloud', e)
        finally:
            time.sleep(.5)


def cloud_has_warm_instance(function_name):
    return False


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello, Goodbye.'

@app.route('/f')
def f():
    return execute_function('f')


@app.route('/g')
def g():
    return execute_function('g')


@app.route('/h')
def h():
    return execute_function('h')


@app.route('/hb')
def hb():
    return execute_function('hb')


def execute_function(function_name):
    remote_function_name = 'faas-router-' + function_name
    run_in_cloud = cloud_has_warm_instance(remote_function_name)
    t0 = time.time_ns()
    error = False
    try:
        if run_in_cloud:
            print(f'running {function_name} in  cloud', str(remoteCount))
            async_increment_remote_count(remote_function_name, -1)
            try:
                async_set_remote_count(get_request(f'/{function_name}'))
            except:
                error = True
        else:
            threading.Thread(target=signal_remote_scale_up, args=(function_name,)).start()
            print(f'running {function_name} locally. ', str(remoteCount))
            functions[function_name]()
            print(f'done {function_name} local')
    except Exception as e:
        print(f'Error running {function_name}:', e)
        error = True
    finally:
        threading.Thread(target=write_log, args=(function_name, t0, time.time_ns(), run_in_cloud, error)).start()
        return Response('cloud' if run_in_cloud else 'local', status=500 if error else 200)


if __name__ == '__main__':
    reset_remote_count()
    threading.Thread(target=update_remote_count).start()
    app.run(port=8081)
