import time
from flask import Flask, request, Response
import local
import urllib.request
import edge
import threading

app = Flask(__name__)

FNAME = 'faas-router-f'
GNAME = 'faas-router-g'
HBNAME = 'faas-router-hb'
HNAME = 'faas-router-h'

remoteCount = {
    FNAME: 0,
    GNAME: 0,
    HNAME: 0,
    HBNAME: 0
}

def reset_remote_count():
    for key in remoteCount.keys():
        remoteCount[key] = 0


def update_remote_count():
    errcnt = 0
    while True:
        try:
            global remoteCount
            remoteCount = eval(urllib.request.urlopen("http://192.168.56.105:8080/info").read().decode('utf-8'))
            errcnt = 0
        except:
            errcnt += 1
            if errcnt == 3:
                reset_remote_count()
            print('Error in connection with remote cloud')
        finally:
            print('remoteCount:', remoteCount, '\n')
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
            urllib.request.urlopen("http://192.168.56.105:8080/f")
            print("done f cloud")
        else:
            threading.Thread(
                target=(lambda:
                        urllib.request.urlopen("http://192.168.56.105:8080/f?wakeup=true"))).start()
            local.f()
            print("done f local")
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
            urllib.request.urlopen("http://192.168.56.105:8080/g")
            print("done g cloud")
        else:
            threading.Thread(
                target=(lambda :
                        urllib.request.urlopen("http://192.168.56.105:8080/g?wakeup=true"))).start()
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
            urllib.request.urlopen("http://192.168.56.105:8080/h")
            print("done h cloud")
        else:
            threading.Thread(
                target=(lambda :
                        urllib.request.urlopen("http://192.168.56.105:8080/h?wakeup=true"))).start()
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
            urllib.request.urlopen("http://192.168.56.105:8080/hb")
            print("done hb cloud")
        else:
            threading.Thread(
                target=(lambda :
                        urllib.request.urlopen("http://192.168.56.105:8080/hb?wakeup=true"))).start()
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
    print('kjashrhkj')
    app.run()
