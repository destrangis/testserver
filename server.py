# Sample SSL Server loading certificates based on hostname using SNI_callback
import socket
import ssl
from pprint import pformat

hosts = {
    "badabec": "badabec.pem",
    "pantagruel": "pantagruel.pem",
    }


class Server:
    def __init__(self, address, port, hosts):
        self.address = address
        self.port = port
        self.host_contexts = {}

        self.defcontext = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
        self.defcontext.sni_callback = self.name_callback
        self.load_certificates(hosts)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind( (self.address, self.port) )
        print("Listening on {}:{}".format(self.address, self.port))
        self.socket.listen(5)


    def load_certificates(self, hosts):
        for hostname, hostcertfile in hosts.items():
            ctx = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH)
            ctx.load_cert_chain(hostcertfile)
            self.host_contexts[hostname] = ctx


    def name_callback(self, socket, hostname, ctx):
        print("SNI for {}".format(hostname))
        if hostname:
            ctx = self.host_contexts.get(hostname)
            if ctx:
                socket.context = ctx
        return None


    def serve(self):
        while True:
            newsock, fromaddr = self.socket.accept()
            stream = self.defcontext.wrap_socket(newsock, server_side=True)
            try:
                self.handle_connection(stream)
            finally:
                stream.shutdown(socket.SHUT_RDWR)
                stream.close()


    def handle_connection(self, stream):
        chunksize = 1024
        data = b""
        while True:
            chunk = stream.recv(chunksize)
            data += chunk
            if len(chunk) < chunksize:
                break

        print("RECEIVED: {}".format(data))
        response = b"HTTP/1.1 200 OK\r\nServer: pepito\r\nContent-length: 10\r\nContent-type: text/plain\r\nConnection: close\r\n\r\nAll fine\r\n"
        stream.send(response)

if __name__ == "__main__":
    srv = Server("0.0.0.0", 8080, hosts)
    srv.serve()
