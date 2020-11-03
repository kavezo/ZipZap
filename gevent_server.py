from gevent.pywsgi import WSGIServer
from app import app

from multiprocessing import Process, freeze_support
from dnserver import startDNS

if __name__ == '__main__':
    freeze_support()
    dnsprocess = Process(target=startDNS)
    dnsprocess.start()
    http_server = WSGIServer(('127.0.0.1', 5000), app)
    http_server.serve_forever()