from .passwords import hash_password, verify_password


# For now let user authentication be static
# We can transition to an SQLite database later on
USERS = {}


def create_user(username: str, password:str):
	if username in USERS:
		raise ValueError("User already exists")

	# Store the record only after hashing the password
	password_record = hash_password(password)
	USERS[username] = {
		"username": username,
		"password_record": password_record,
		"role": "user"
	}


def authenticate_user(username: str, password: str):
	user = USERS.get(username)

	if user is None:
		return None
	if not verify_password(
		password,
		user["password_record"]
	):
		return None

	return user