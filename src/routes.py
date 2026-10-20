from .mini_api import MiniAPI
from .auth import authorize
from .users import authenticate_user, create_user, USERS
from .tokens import create_token, TOKEN_LIFETIME
from .http_request import HTTPError


app = MiniAPI()
create_user("alice", "correct-horse-battery")


@app.route("GET", "/public")
def public(request):
	return {
		"message": "This is a public landing page endpoint"
	}


@app.route("POST", "/login")
def login(request):
	data = request.json()

	if not isinstance(data, dict):
		raise HTTPError(400, "Expected JSON object")

	username = data.get("username")
	password = data.get("password")

	user = authenticate_user(username, password)

	if user is None:
		raise HTTPError(401, "Invalid credentials")

	token = create_token(user["username"])

	return {
		"access_token": token,
		"token_type": "bearer",
		"expires_in": TOKEN_LIFETIME
	}


@app.route("GET", "/private")
@authorize()
def private(request):
	return {
		"message": "Private endpoint placeholder"
	}


@app.route("GET", "/admin")
@authorize(roles={"admin"})
def admin(request):
	return {
		"message": "Administrative information",
		"username": request.user["username"]
	}


@app.route("GET", "/users/{username}/profile")
@authorize(owner_params="username")
def profile(request):
	return {
		"username": request.user["username"]
	}


@app.route("GET", "/me")
@authorize()
def my_profile(request):
	return {
		"username": request.user["username"],
		"role": request.user["role"]
	}


@app.route("POST", "/register")
def register(request):
	data = request.json()

	if not isinstance(data, dict):
		raise HTTPError(400, "Expected JSON object")

	username = data.get("username")
	password = data.get("password")

	if not isinstance(username, str):
		raise HTTPError(400, "Username must be a string")
	if not isinstance(password, str):
		raise HTTPError(400, "Password must be a string")

	username = username.strip()

	if not (3 <= len(username) <= 50):
		raise HTTPError(
			400,
			"Username must be between 3 and 50 characters long"
		)
	if (
		not username.isascii() 
		or not all(
			char.isalnum() or char == "_"
			for char in username
		)
	):
		raise HTTPError(
			400,
			"Username may contain only ASCII letters, digits and underscores"
		)
	if not (12 <= len(password) <= 128):
		raise HTTPError(
			400,
			"Password must be between 12 and 128 characters"
		)

	try:
		create_user(username, password)
	except ValueError:
		raise HTTPError(409, "Username already exists")

	return {
		"message": "User registered successfully",
		"username": username
	}