#!/usr/bin/env python3

import logging
import socket
import sys
from time import sleep
import xmlrpc.client

from zeroconf import ServiceBrowser, ServiceStateChange, Zeroconf


def on_service_state_change(zeroconf, service_type, name, state_change):
    print("Service %s of type %s state changed: %s" % (name, service_type, state_change))

    if state_change is ServiceStateChange.Added:
        info = zeroconf.get_service_info(service_type, name)
        # connect to the server
        if info:
            addrstr = "http://{}:{}/".format(socket.inet_ntoa(info.address), info.port)
            print("attempting to connect to xmlprc at {}".format(addrstr))
            a = xmlrpc.client.ServerProxy(addrstr)
            print("calling a method on it")
            ans = a.bogus()
            print('dont calling')
            print(a.bogus())
            print(a.read_albums())
            print("done")


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) > 1:
        assert sys.argv[1:] == ['--debug']
        logging.getLogger('zeroconf').setLevel(logging.DEBUG)

    zeroconf = Zeroconf()
    print("\nBrowsing services, press Ctrl-C to exit...\n")
    browser = ServiceBrowser(zeroconf, "_http._tcp.local.", handlers=[on_service_state_change])

    try:
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        zeroconf.close()
