import os
import subprocess
from flask import Flask, Response, request
import threading

lockF = threading.Lock()
lockG = threading.Lock()
lockH = threading.Lock()
lockHb = threading.Lock()
fcnt = 0
gcnt = 0
hcnt = 0
hbcnt = 0
FNAME = 'faas-router-f'
GNAME = 'faas-router-g'
HBNAME = 'faas-router-hb'
HNAME = 'faas-router-h'


app = Flask(__name__)

@app.route('/f')
def f():

   if request.args.get('wakeup'):
      threading.Thread(
         target=(lambda: os.system('curl faas-router-f.default.127.0.0.1.nip.io?wakeup=true'))).start()
      return 'preparing'

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

      return Response('', status=500 if error else 200)

@app.route('/g')
def g():

   if request.args.get('wakeup'):
      threading.Thread(
         target=(lambda: os.system('curl faas-router-g.default.127.0.0.1.nip.io?wakeup=true'))).start()
      return 'preparing'


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

      return Response('', status=500 if error else 200)

@app.route('/h')
def h():

   if request.args.get('wakeup'):
      threading.Thread(
         target=(lambda: os.system('curl faas-router-h.default.127.0.0.1.nip.io?wakeup=true'))).start()
      return 'preparing'

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

      return Response('', status=500 if error else 200)

@app.route('/hb')
def hb():

   if request.args.get('wakeup'):
      threading.Thread(
         target=(lambda: os.system('curl faas-router-hb.default.127.0.0.1.nip.io?wakeup=true'))).start()
      return 'preparing'

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

      return Response('', status=500 if error else 200)

@app.route('/info')
def info():

   running = [i.split() for i in subprocess.Popen(
      "kubectl get pods --all-namespaces -o jsonpath=\"{.items[*].spec.containers[*].image}\" |tr -s '[[:space:]]' '\n' |sort |uniq -c | grep faas-router-", shell=True, stdout=-1).stdout.read().decode('utf-8').split('\n')][:-1]

   available = {
      FNAME: 0,
      GNAME: 0,
      HNAME: 0,
      HBNAME: 0
   }

   for r in running:
      if FNAME in r[1]:
         available[FNAME] = int(r[0]) - fcnt
      elif GNAME in r[1]:
         available[GNAME] = int(r[0]) - gcnt
      elif HBNAME in r[1]:
         available[HBNAME] = int(r[0]) - hbcnt
      elif HNAME in r[1]:
         available[HNAME] = int(r[0]) - hcnt

   return str(available)



if __name__ == "__main__":
   app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))