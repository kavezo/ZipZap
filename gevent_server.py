from gevent.pywsgi import WSGIServer

from multiprocessing import Process, freeze_support
from dnserver import startDNS

if __name__ == '__main__':
    from app import app # only do this in main process because of logging

    freeze_support()
    dnsprocess = Process(target=startDNS)
    dnsprocess.start()
    http_server = WSGIServer(('127.0.0.1', 5000), app)
    app.logger.info("App server started")
    print("App server started")
    http_server.serve_forever()