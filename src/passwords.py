import hashlib
import hmac
import secrets

SALT_SIZE = 16
KEY_SIZE = 32

# Educational baseline; tune to your environment.
SCRYPT_N = 2**14
SCRYPT_R = 8
SCRYPT_P = 1


def hash_password(password: str) -> dict:
	salt = secrets.token_bytes(SALT_SIZE)

	password_hash = hashlib.scrypt(
		password.encode("utf-8"),
		salt=salt,
		n=SCRYPT_N,
		r=SCRYPT_R,
		p=SCRYPT_P,
		dklen=KEY_SIZE
	)

	return {
		"salt": salt.hex(),
		"hash": password_hash.hex()
	}

def verify_password(password: str, record: dict) -> bool:
    salt = bytes.fromhex(record["salt"])
    expected_hash = bytes.fromhex(record["hash"])

    candidate_hash = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=SCRYPT_N,
        r=SCRYPT_R,
        p=SCRYPT_P,
        dklen=KEY_SIZE,
    )

    return hmac.compare_digest(
        candidate_hash,
        expected_hash
    )