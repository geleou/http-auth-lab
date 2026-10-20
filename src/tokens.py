import hashlib, secrets, time

TOKEN_LIFETIME = 300 # seconds = 5 minutes

# This is where active sessions will be stored
SESSIONS = {}


def hash_token(token: str) -> str:
	return hashlib.sha256(
		token.encode("ascii")
	).hexdigest()

def create_token(username: str) -> str:
	token = secrets.token_urlsafe(32)
	token_digest = hash_token(token)

	SESSIONS[token_digest] = {
		"username": username,
		"expires_at": time.time() + TOKEN_LIFETIME
	}

	return token

def validate_token(token: str):
	token_digest = hash_token(token)
	session = SESSIONS.get(token_digest)

	if session is None:
		return None

	if time.time() >= session["expires_at"]:
		del SESSIONS[token_digest]
		return None

	return session["username"]

def revoke_token(token: str):
	token_digest = hash_token(token)

	# If the token exists pop it and return True otherwise return False
	return SESSIONS.pop(token_digest, None) is not None