import time
from flask import Flask, Response
import local
import urllib.request
import edge
import threading

app = Flask(__name__)

FNAME = 'faas-router-f'
GNAME = 'faas-router-g'
HBNAME = 'faas-router-hb'
HNAME = 'faas-router-h'

rcLock = threading.Lock()

remoteCount = {
    FNAME: 0,
    GNAME: 0,
    HNAME: 0,
    HBNAME: 0
}


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


def reset_remote_count():
    set_remote_count(str({
        FNAME: 0,
        GNAME: 0,
        HNAME: 0,
        HBNAME: 0
    }))


def get_request(sufix):
    return urllib.request.urlopen("http://192.168.56.105:8080"+sufix).read().decode('utf-8')

def async_update_remote_count(function_name):
    threading.Thread(
        target=(lambda: set_remote_count(get_request("/"+function_name+"?wakeup=true"), True))
    ).start()


def update_remote_count():
    errcnt = 0
    while True:
        try:
            set_remote_count(get_request("/info"))
            errcnt = 0
        except:
            errcnt += 1
            if errcnt == 3:
                reset_remote_count()
            print('Error in connection with remote cloud')
        finally:
            time.sleep(1)


def cloud_has_warm_instance(function_name):
    return remoteCount[function_name] > 0


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello, Goodbye.'


@app.route('/f')
def f():
    run_in_cloud = cloud_has_warm_instance(FNAME)
    error = False
    try:
        if run_in_cloud:
            print('running f cloud')
            async_set_remote_count(get_request("/f"))
            print("done f cloud")
        else:
            async_update_remote_count('f')
            print('running f local')
            local.f()
            print('done f local')
    except:
        print('Error running f', run_in_cloud)
        error = True
    finally:
        return Response('', status=500 if error else 200)


@app.route('/g')
def g():
    run_in_cloud = cloud_has_warm_instance(GNAME)
    error = False
    try:
        if run_in_cloud:
            print('running g cloud')
            async_set_remote_count(get_request("/g"))
            print("done g cloud")
        else:
            async_update_remote_count('g')
            print('running g local')
            local.g()
            print("done g local")
    except:
        print('Error running g', run_in_cloud)
        error = True
    finally:
        return Response('', status=500 if error else 200)



@app.route('/h')
def h():
    run_in_cloud = cloud_has_warm_instance(HNAME)
    error = False
    try:
        if run_in_cloud:
            print('running h cloud')
            async_set_remote_count(get_request("/h"))
            print("done h cloud")
        else:
            async_update_remote_count('h')
            print('running h local')
            local.h()
            print("done h local")
    except:
        print('Error running h', run_in_cloud)
        error = True
    finally:
        return Response('', status=500 if error else 200)


@app.route('/hb')
def hb():
    run_in_cloud = cloud_has_warm_instance(HBNAME)
    error = False
    try:
        if run_in_cloud:
            print('running hb cloud')
            async_set_remote_count(get_request("/hb"))
            print("done hb cloud")
        else:
            async_update_remote_count('hb')
            print('running hb cloud')
            local.hb()
            print("done hb local")
    except:
        print('Error running hb', run_in_cloud)
        error = True
    finally:
        return Response('', status=500 if error else 200)


if __name__ == '__main__':
    #threading.Thread(target=edge.simulate_arrival).start()
    threading.Thread(target=update_remote_count).start()
    app.run()
