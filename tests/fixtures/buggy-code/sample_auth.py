"""Sample fixture for Analyzer & Verifier benchmark."""

def authenticate(username, password):
    # SECURITY BUG: Plaintext comparison, no rate limiting, SQL injection potential
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    return query
