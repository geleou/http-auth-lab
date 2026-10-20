from http_request import Request, HTTPError

def parse_request(raw_data: bytes) -> Request:
	# Separate headers from body on the first occurence of the separator
	header_bytes, separator, body = raw_data.partition(
		b"\r\n\r\n"
	)

	# Separator cannot be missing
	if not separator:
		raise HTTPError(400, "Missing header terminator")

	# Headers should only follow the said ISO byte format
	# Attempt to retrieve the actual text out the headers bytes
	try:
		header_text = header_bytes.decode("iso-8859-1")
	except UnicodeDecodeError:
		raise HTTPError(400, "Invalid HTTP headers")


	# Split the headers into its different lines
	# The first line should only contain 3 things: method, target and version
	lines = header_text.split("\r\n")
	parts = lines[0].split(" ")

	if len(parts) != 3:
		raise HTTPError(400, "Invalid request line")

	method, target, version = parts

	if version != "HTTP/1.1":
		raise HTTPError(400, "Unsupported HTTP version")

	# Create an empty header dictionary in which the actual content 
	# for the headers will be stored after parsing
	headers = {}

	# Parse lines excluding the first which is already known to
	# contain method, target and version
	for line in lines[1:]:
		# Request headers should only follow the format "Name: Value"
		# Name of header should not be empty and should be unique
		if ":" not in line:
			raise HTTPError(400, "Malformed header")

		# Split at the first occurence of ":"
		name, value = line.split(":", 1)
		name = name.strip().lower()
		value = value.strip()

		if not name:
			raise HTTPError(400, "Empty header name")
		if name in headers:
			raise HTTPError(400, "Duplicate header")

		headers[name] = value

	# Move on to body parsing and check its length,
	# which should be present as a key in the header dict (assume zero if not present)
	try:
		content_length = int(headers.get("content-length", "0"))
	except ValueError:
		raise HTTPError(400, "Invalid Content-Length")

	if content_length < 0:
		raise HTTPError(400, "Negative Content-Length")

	# content-length header should match the actual length of the body string
	if len(body) != content_length:
		raise HTTPError(400, "Body length mismatch")

	# If somehow everything is in order, create a new Request object and return it
	return Request(
		method=method,
		target=target,
		version=version,
		headers=headers,
		body=body
	)

	# parse_request() expects a complete request
	# It doesn't account for the actual socket reading request data in sparse bytes
	# A separate function that reads throught the request data and only then parses
	# the actual data to form the data structure called a Request object


def read_http_request(client_socket):
	buffer = b""

	MAX_HEADER_SIZE = 16 * 1024
	MAX_BODY_SIZE = 1024 * 1024

	# Phase 1:
	# Keep reading chunks of 4096 bytes until header-body separator is stumbled upon
	while b"\r\n\r\n" not in buffer:
		chunk = client_socket.recv(4096)

		if not chunk:
			raise HTTPError(400, "Connection closed during headers")

		# Keep adding the chunks to the buffer
		buffer += chunk

		if (
			b"\r\n\r\n" not in buffer
			and
			len(buffer) > MAX_HEADER_SIZE
		):
			# If you 're still reading through headers and
			# max size is reached then raise error
			raise HTTPError(431, "Headers too large")

	# Split the now complete message at the first occurence of the separator 
	header_bytes, separator, body = buffer.partition(b"\r\n\r\n")

	if len(header_bytes) > MAX_HEADER_SIZE:
		raise HTTPError(431, "Headers too large")

	# Decode header message and then separate each header line
	header_lines = header_bytes.decode("iso-8859-1").split("\r\n")

	content_length_values = []
	transfer_encoding_present = False

	# First line of headers is supposed to contain method, target and version
	for line in header_lines[1:]:
		# Enforce key: value format for headers
		if ":" not in line:
			raise HTTPError(400, "Malformed header")

		name, value = line.split(":", 1)
		name = name.strip().lower()

		if name == "content-length":
			content_length_values.append(value.strip())
		if name == "transfer-encoding":
			transfer_encoding_present = True

	if transfer_encoding_present:
		raise HTTPError(501, "Transfer-Encoding not supported")

	if len(content_length_values) > 1:
		raise HTTPError(400, "Duplicate Content-Length")

	try:
		content_length = int(
			content_length_values[0]
			if content_length_values else "0"
		)
	except ValueError:
		raise HTTPError(400, "Invalid Content-Length")

	# Phase 2:
	# Read the remaining body bytes off the message
	while len(body) < content_length:
		chunk = client_socket.recv(
			min(4096, content_length - len(body))
		)

		if not chunk:
			raise HTTPError(400, "Incomplete request body")

		body += chunk

	# Connect the separetely parsed parts of the message to form
	# a single Request object and pass that to the previous functions
	raw_request = header_bytes + separator + body[:content_length]

	return parse_request(raw_request)