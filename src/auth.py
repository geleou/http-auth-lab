from .http_request import HTTPError
from .tokens import validate_token
from .users import USERS

from functools import wraps


def extract_bearer_token(request):
	# Retrieve the header related to authorization 
	authorization = request.headers.get(
		"authorization", ""
	)
	scheme, separator, token = authorization.partition(" ")

	# Force bearer token format
	if (
		not separator
		or scheme.lower() != "bearer"
		or not token
		or any(char.isspace() for char in token)
	):
		raise HTTPError(401, "Invalid or missing bearer token")

	return token

	def require_user(request):
		token = extract_bearer_token(request)
		username = validate_token(token)
		if username is None:
			raise HTTPError(401, "Invalid or expired token")

		user = USERS.get(username)
		if user is None:
			raise HTTPError(401, "User not found")

		return user

	def require_admin(request):
		user = require_user(request)
		if user["role"] != "admin":
			raise HTTPError(403, "Unauthorized")

		return user

def authenticated(handler):
	@wraps(handler)
	def wrapper(request, *args, **kwargs):
		user = require_user(request)
		request.user = user

		return handler(request, *args, **kwargs)

	return wrapper

def requires_role(role):
	def decorator(handler):
		@wraps(handler)
		def wrapper(request, *args, **kwargs):
			user = require_user(request)

			if user["role"] != role:
				raise HTTPError(403, "Unauthorized")

			request.user = user

			return handler(request, *args, **kwargs)

		return wrapper

	return decorator

def authorize(roles=None, owner_params=None):
	allowed_roles = (
		frozenset(roles) 
		if roles is not None 
		else None
	)

	def decorator(handler):
		@wraps(handler)
		def wrapper(request, *args, **kwargs):
			user = require_user(request)

			if (
				allowed_roles is not None
				and user["role"] not in allowed_roles
			):
				raise HTTPError(403, "Unauthorized")

			if owner_params is not None:
				resource_owner = request.path_params.get(
					owner_params
				)
				if resource_owner != user["username"]:
					raise HTTPError(403,"Unauthorize")

			request.user = user

			return handler(request, *args, **kwargs)

		return wrapper

	return decorator