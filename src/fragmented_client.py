import socket
import time

with socket.create_connection(("127.0.0.1", 8080)) as sock:
    parts = [
        b"POST /test HTTP/1.1\r\n",
        b"Host: localhost\r\n",
        b"Content-Type: application/json\r\n",
        b"Content-Length: 17\r\n",
        b"\r\n",
        b'{"hello":',
        b'"world"}'
    ]

    for part in parts:
        print("Sending:", repr(part))
        sock.sendall(part)
        time.sleep(0.2)

    response = bytearray()

    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        response.extend(chunk)

    print("\nResponse:")
    print(response.decode("utf-8"))
