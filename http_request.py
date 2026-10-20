import json
from urllib.parse import urlsplit, parse_qs

# HTTPError extends the built-in Exception class
class HTTPError(Exception):
	# Constructor initializes the status code and the ajdunct message
	def __init__(self, status_code, message):
		self.status_code = status_code
		self.message = message
		# The constructor of the superclass Exception is initialized using the same message
		super().__init__(message)

# Class representation of an HTTP request
class Request:
	def __init__(self, method, target, version, headers, body):
		self.method = method
		self.target = target
		self.version = version
		self.headers = headers
		self.body = body

		# Split the target and fetch path and query parameters
		parsed_url = urlsplit(target)
		self.path = parsed_url.path
		self.query_params = parse_qs(parsed_url.query)

	# Attempt to return JSON representation of said request
	# Use the HTTPError class to initialize and report problems 
	def json(self):
		try:
			return json.loads(self.body)
		except (ValueError, UnicodeDecodeError):
			raise HTTPError(400, "Invalid JSON body")

	def __repr__(self):
		return (
			f"Request(method={self.method!r}, "
			f"path={self.path!r}, "
			f"version={self.version!r})"
		)

