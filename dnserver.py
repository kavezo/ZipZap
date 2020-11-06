# Copyright (c) Twisted Matrix Laboratories.

from twisted.internet import reactor, defer
from twisted.names import client, dns, error, server
import socket

# https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
# trying three of the methods above, two of them are backup
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    s.connect(("8.8.8.8", 8022))
    myip = s.getsockname()[0]
    s.close()
except:
    myip = socket.gethostbyname(socket.gethostname())
    if myip == '127.0.0.1':
        myip = socket.gethostbyname(socket.getfqdn())

class DynamicResolver(object):
    """
    A resolver which calculates the answers to certain queries based on the
    query type and name.
    """

    def _dynamicResponseRequired(self, query):
        """
        Check the query to determine if a dynamic response is required.
        """
        domain_includes = ['magica-us.com', 'app.adjust.com', 'treasuredata.com', 'smbeat', 'snaa.services']
        should_redirect = False
        for domain in domain_includes:
            if domain in query.name.name.decode('ascii'):
                should_redirect = True

        return should_redirect


    def _doDynamicResponse(self, query):
        """
        Calculate the response to a query.
        """
        answer = dns.RRHeader(
            name=query.name.name,
            payload=dns.Record_A(address=myip.encode('ascii')))
        answers = [answer]
        authority = []
        additional = []
        return answers, authority, additional


    def query(self, query, timeout=None):
        """
        Check if the query should be answered dynamically, otherwise dispatch to
        the fallback resolver.
        """
        if self._dynamicResponseRequired(query):
            return defer.succeed(self._doDynamicResponse(query))
        else:
            return defer.fail(error.DomainError())

def startDNS():
    """
    Run the server.
    """
    factory = server.DNSServerFactory(
        clients=[DynamicResolver(), client.Resolver(resolv='resolv.conf')]
    )

    protocol = dns.DNSDatagramProtocol(controller=factory)

    reactor.listenUDP(53, protocol)
    reactor.listenTCP(53, factory)

    print(f"DNS server started at {myip}")
    reactor.run()