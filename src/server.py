import json, socket
from http_parser import read_http_request
from http_request import HTTPError
from routes import app
from users import create_user


HOST = "127.0.0.1"
PORT = 8080


server_socket = socket.socket(
	socket.AF_INET,
	socket.SOCK_STREAM
)

server_socket.setsockopt(
	socket.SOL_SOCKET,
	socket.SO_REUSEADDR,
	1
)

server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f"Server listening on {HOST}:{PORT}")


# Wait indefinitely until a client connects
while True:
	# Fetch client details from the accept method of the socket
    client_socket, client_address = server_socket.accept()

    # Prevent a client from blocking us forever
    client_socket.settimeout(5)

    try:
    	# Read HTTP messages broken up into 4096-byte chunks
        request = read_http_request(client_socket)

        print("\n--- Parsed HTTP Request ---")
        print("Method:", request.method)
        print("Path:", request.path)
        print("Version:", request.version)
        print("Headers:", request.headers)
        print("Query params:", request.query_params)
        print("Body:", request.body)

        if request.headers.get("content-type", "").startswith(
            "application/json"
        ):
            print("JSON:", request.json())

        # status = 200
        # payload = {
        #     "method": request.method,
        #     "path": request.path,
        #     "query_params": request.query_params
        # }

        status, payload = app.dispatch(request)

    except HTTPError as exc:
        status = exc.status_code
        payload = {"error": exc.message}

    except TimeoutError:
        status = 408
        payload = {"error": "Request timeout"}

    except Exception as exc:
        print("Internal server error:", repr(exc))
        status = 500
        payload = {"error": "Internal server error"}

    body = json.dumps(payload).encode("utf-8")

    reason_phrases = {
        200: "OK",
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        408: "Request Timeout",
        409: "Conflict",
        413: "Content Too Large",
        431: "Request Header Fields Too Large",
        500: "Internal Server Error",
        501: "Not Implemented",
    }
    reason = reason_phrases.get(status, "Error")

    response = (
        f"HTTP/1.1 {status} {reason}\r\n"
        "Content-Type: application/json\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode("ascii") + body

    try:
        client_socket.sendall(response)
    except OSError:
        pass

    client_socket.close()

