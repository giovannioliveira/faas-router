import os
import subprocess
import time
from flask import Flask, Response, request
import threading

FNAME = 'faas-router-f'
GNAME = 'faas-router-g'
HBNAME = 'faas-router-hb'
HNAME = 'faas-router-h'

lockF = threading.Lock()
lockG = threading.Lock()
lockH = threading.Lock()
lockHb = threading.Lock()
fcnt = 0
gcnt = 0
hcnt = 0
hbcnt = 0

running_count = {
      FNAME: 0,
      GNAME: 0,
      HNAME: 0,
      HBNAME: 0
}

app = Flask(__name__)

def monitor():
   errcnt = 0
   while True:
      try:
         running = [i.split() for i in subprocess.Popen(
            "kubectl get pods --all-namespaces -o jsonpath=\"{.items[*].spec.containers[*].image}\" |tr -s '[[:space:]]' '\n' |sort |uniq -c | grep faas-router-", shell=True, stdout=-1).stdout.read().decode('utf-8').split('\n')][:-1]

         aux = {
            FNAME: 0,
            GNAME: 0,
            HNAME: 0,
            HBNAME: 0
         }
         for r in running:
            if FNAME in r[1]:
               aux[FNAME] = int(r[0])
            elif GNAME in r[1]:
               aux[GNAME] = int(r[0])
            elif HBNAME in r[1]:
               aux[HBNAME] = int(r[0])
            elif HNAME in r[1]:
               aux[HNAME] = int(r[0])
         global running_count
         running_count = aux
         errcnt = 0
      except:
         print('error running kubectl list pods')
         errcnt += 1
         if errcnt == 3:
            running_count = {
               FNAME: 0,
               GNAME: 0,
               HNAME: 0,
               HBNAME: 0
            }
      finally:
         time.sleep(.05)


def send_wakeup_request(function_name):
   try:
      os.system('curl faas-router-'+function_name+'.default.127.0.0.1.nip.io?wakeup=true')
   except:
      print('Error in wakeup requesto to '+function_name)


@app.route('/f')
def f():
   if request.args.get('wakeup'):
      threading.Thread(
         target=send_wakeup_request, args=('f',)).start()
      return info()

   global fcnt
   lockF.acquire()
   fcnt += 1
   lockF.release()
   error = False

   try:
      os.system('curl faas-router-f.default.127.0.0.1.nip.io')
   except:
      error = True
   finally:
      lockF.acquire()
      fcnt -= 1
      lockF.release()

      return Response(info(), status=500 if error else 200)

@app.route('/g')
def g():

   if request.args.get('wakeup'):
      threading.Thread(
         target=send_wakeup_request, args=('g',)).start()
      return info()


   global gcnt
   lockG.acquire()
   gcnt += 1
   lockG.release()
   error = False

   try:
      os.system('curl faas-router-g.default.127.0.0.1.nip.io')
   except:
      error = True
   finally:
      lockG.acquire()
      gcnt -= 1
      lockG.release()

      return Response(info(), status=500 if error else 200)

@app.route('/h')
def h():

   if request.args.get('wakeup'):
      threading.Thread(
         target=send_wakeup_request, args=('h',)).start()
      return info()

   global hcnt
   lockH.acquire()
   hcnt += 1
   lockH.release()
   error = False

   try:
      os.system('curl faas-router-h.default.127.0.0.1.nip.io')
   except:
      error = True
   finally:
      lockH.acquire()
      hcnt -= 1
      lockH.release()

      return Response(info(), status=500 if error else 200)

@app.route('/hb')
def hb():

   if request.args.get('wakeup'):
      threading.Thread(
         target=send_wakeup_request, args=('hb',)).start()
      return info()

   global hbcnt
   lockHb.acquire()
   hbcnt += 1
   lockHb.release()
   error = False

   try:
      os.system('curl faas-router-hb.default.127.0.0.1.nip.io')
   except:
      error = True
   finally:
      lockHb.acquire()
      hbcnt -= 1
      lockHb.release()

      return Response(info(), status=500 if error else 200)

@app.route('/info')
def info():
   global running_count
   return str({
      FNAME: running_count[FNAME] - fcnt,
      GNAME: running_count[GNAME] - gcnt,
      HNAME: running_count[HNAME] - hcnt,
      HBNAME: running_count[HBNAME] - hbcnt
   })



if __name__ == "__main__":
   threading.Thread(target=monitor).start()
   app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))