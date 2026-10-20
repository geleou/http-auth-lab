class MiniAPI:
	# Initialize the dict in which all the valid routes will be stored
	def __init__(self):
		self.routes = {}

	def route(self, method, path):
		# Routing should mainly handle decorators
		# Remember, when decorating, you substitute a function
		# for another, by first calling the decorator
		def decorator(handler):
			key = (method.upper(), path)

			# Routes should be unique
			if key in self.routes:
				raise ValueError(
					f"Route already registered: {key}"
				)
			self.routes[key] = handler
			return handler

		return decorator

	# After determining method and path exist, handle the request
	# by calling the handler function
	def dispatch(self, request):
		key = (request.method, request.path)
		handler = self.routes.get(key)

		if handler is None:
			return 404, {"error": "Route not found"}

		result = handler(request)

		return 200, result