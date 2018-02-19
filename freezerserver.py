#! /usr/bin/env python3
import random
import socket
import time
import xmlrpc.server

from zeroconf import ServiceInfo, Zeroconf

from freezer import FreezerInstance
from freezerdb import FreezerDB


def getmyip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ans = s.getsockname()[0]
    print("looks like my IP is {}".format(ans))
    s.close()
    return ans


class FreezerServer(object):
    def __init__(self):
        self.port = 8080

    def register_zeroconf(self):
        desc = {}
        self.info = ServiceInfo("_http._tcp.local.",
                                "freezer._http._tcp.local.",
                                socket.inet_aton(getmyip()), self.port, 0, 0,
                                desc, "somehost.local.")
        self.zc = Zeroconf()
        print("calling register_service")
        self.zc.register_service(self.info)

    def serve_forever(self):
        self.register_zeroconf()
        addr = ("0.0.0.0", self.port)
        server = xmlrpc.server.SimpleXMLRPCServer(addr)
        print("serving on", addr)
        frzr = FreezerInstance()
        db = FreezerDB()
        server.register_function(db.read_all, "read_all")
        server.register_function(db.read_albums, "read_albums")
        server.register_function(frzr.zip_album)
        server.register_function(frzr.search, name="search")
        server.serve_forever()
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            print("\nUnregistering...")
            self.close()

    def close(self):
        self.zc.unregister_service(self.info)
        self.zc.close()


if __name__ == "__main__":
    s = FreezerServer()
    s.serve_forever()
