import socket
import time
import xmlrpc.server

from zeroconf import ServiceInfo, Zeroconf

from freezer import FreezerInstance
from freezerdb import FreezerDB


class FreezerServer(object):

    def __init__(self):
        pass

    def register_zeroconf(self):
        desc = {} 
        self.info = ServiceInfo("_http._tcp.local.",
                        "freezer._http._tcp.local.",
                        socket.inet_aton("127.0.0.1"), 8000, 0, 0,
                        desc, "somehost.local.")
        self.zc = Zeroconf()
        self.zc.register_service(self.info)

    def serve_forever(self):
        self.register_zeroconf()
        addr = ("0.0.0.0", 8000)
        server = xmlrpc.server.SimpleXMLRPCServer(addr)
        print("serving on", addr)
        frzr = FreezerInstance()
        db = FreezerDB()
        server.register_function(db.index_generator, "read_all")
        server.register_function(frzr.zip_album)
        server.register_function(frzr.search, name="search")
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            print("Unregistering...")
            self.close()

    def close(self):
        self.zc.unregister_service(self.info)
        self.zc.close()

