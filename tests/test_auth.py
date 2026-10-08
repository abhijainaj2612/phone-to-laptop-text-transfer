from relay_server.auth import RateLimiter, issue_phone_token, verify_phone_token

def test_signed_phone_token():
    token = issue_phone_token("device-1", "x" * 40)
    assert verify_phone_token(token, "x" * 40) == "device-1"
    assert verify_phone_token(token, "y" * 40) is None

def test_rate_limiter():
    limiter = RateLimiter(2)
    assert limiter.allowed("a") and limiter.allowed("a") and not limiter.allowed("a")
