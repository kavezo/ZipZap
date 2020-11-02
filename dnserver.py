import socket
import dns
from dns import resolver
from queue import Queue
from threading import Thread

class DNSQuery:
  def __init__(self, data):
    self.data=data
    self.dominio=b''

    tipo = (data[2] >> 3) & 15   # Opcode bits
    if tipo == 0:                     # Standard query
      ini=12
      lon=data[ini]
      while lon != 0:
        self.dominio+=data[ini+1:ini+lon+1]+b'.'
        ini+=lon+1
        lon=data[ini]

  def respuesta(self, ip):
    packet=b''
    if self.dominio:
      packet+=self.data[:2] + b"\x81\x80"
      packet+=self.data[4:6] + self.data[4:6] + b'\x00\x00\x00\x00'   # Questions and Answers Counts
      packet+=self.data[12:]                                         # Original Domain Name Question
      packet+=b'\xc0\x0c'                                             # Pointer to domain name
      packet+=b'\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04'             # Response type, ttl and resource data length -> 4 bytes
      packet+=bytes([int(x) for x in ip.split('.')]) # 4bytes of IP
    return packet

q = Queue()
def getDNS(udps):
  try:
    while True:
      data, addr = q.get()
      p=DNSQuery(data)
      if p.dominio and not 'magica-us.com' in p.dominio.decode('ascii'):
        domain = p.dominio.decode('ascii')
        # just extract the first IP
        for ipval in resolver.resolve(domain if not domain.endswith('.') else domain[:-1], 'A'):
          ip = ipval.to_text()
          break
      else:
          ip = myip
      udps.sendto(p.respuesta(ip), addr)
  except Exception as e:
    print(e)
  finally:
    q.task_done()
    

if __name__ == '__main__':
  myip = socket.gethostbyname(socket.gethostname())

  udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  udps.bind(('',53))

  try:
    for i in range(10):
        t = Thread(target=getDNS, args=(udps,))
        t.daemon = True
        t.start()
    while True:
      answer = udps.recvfrom(1024)
      q.put(answer)
  except KeyboardInterrupt:
    print('Shutting down...')
    q.join()
    udps.close()