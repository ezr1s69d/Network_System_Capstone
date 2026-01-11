import socket
from .utils import parser


class HTTPClient:
    def __init__(self) -> None:
        self.connection_pool = {}
    
    def get(self, url, headers=None, stream=False):
        result = parser.parse_url(url)
        if result is None:
            return None
        scheme  = result[0]
        address = result[1]
        resource = result[2]

        # TODO: Generate the string in HTTP/1.1 format, excluding the body, based on the dictionary "headers".
        # headers_str = ?
        # E.g., headers_str = "header1: 1\r\nheader2: 2\r\n"
        headers_str = ""
        
        
        # TODO: Format the string in HTTP/1.1 format, excluding the body and encode the string to bytes.
        # request = ?
        # E.g., request = b"GET / HTTP/1.1\r\nheader1: 1\r\nheader2: 2\r\n\r\n"
        request = b"GET " + resource.encode() + b" HTTP/1.1" + b"\r\n" + headers_str.encode() + b"\r\n"
        
        return self.__send_request(address, request, stream)
    
    def post(self, url, headers=None, body=None, stream=False):
        result = parser.parse_url(url)
        if result is None:
            return None
        scheme = result[0]
        address = result[1]
        resource = result[2]

        # TODO: Generate the string in HTTP/1.1 format, excluding the body, based on the dictionary "headers".
        # headers_str = ?
        # E.g., headers_str = "header1: 1\r\nheader2: 2\r\n"
        headers_str = "content-type: " + headers['Content-Type'] + "\r\n" + "content-length: " + str(headers['Content-Length']) + "\r\n"
        
        
        # TODO: Format the string in HTTP/1.1 format, excluding the body and encode the string to bytes.
        # request = ?
        # E.g., request = b"GET / HTTP/1.1\r\nheader1: 1\r\nheader2: 2\r\n\r\n"
        request = b"POST " + resource.encode() + b" HTTP/1.1" + b"\r\n" + headers_str.encode() + b"\r\n"
        
        
        if body:
            # TODO: Append the bytes with body.
            # request = ?
            # E.g., request = b"GET / HTTP/1.1\r\nheader1: 1\r\nheader2: 2\r\n\r\nthis is body"
            request += body
            
        return self.__send_request(address, request, stream)
    
    def __send_request(self, address, request, stream):
        # Get connection in pool
        client_socket = None
        connection = {}
        # TODO: Retrieve the client_socket if it is in the connection_pool.
        # Hint: Use f"{address[0]}:{address[1]}" as the key of connection_pool
        if f"{address[0]}:{address[1]}" in self.connection_pool:
            client_socket = self.connection_pool[f"{address[0]}:{address[1]}"]['socket']
        else:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(5)
            try:
                client_socket.connect(address)
                connection['socket'] = client_socket
                self.connection_pool[f"{address[0]}:{address[1]}"] = connection
            except:
                client_socket.close()
        
        # TODO: If the client_socket is not found in the connection_pool, create a new socket, connect it to the server using the given address, and add it to the connection_pool.
        # Hint: Use f"{address[0]}:{address[1]}" as the key of connection_pool
        # Hint: Call client_socket.settimeout(5) to set a timeout of 5 seconds.
        
        
        # Check connection
        counter = 0
        while True:
            # Send request
            try:
                client_socket.sendall(request)
                break
            except:
                client_socket.close()
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.settimeout(5)
                connection['socket'] = client_socket
                try:
                    client_socket.connect(address)
                except:
                    pass
                if counter == 3:
                    return None
            counter += 1
        

        # Receive the server's response
        response = parser.parse_response(client_socket, stream)

        return response
    