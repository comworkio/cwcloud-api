from fastapi.security import APIKeyHeader

user_token_header = APIKeyHeader(name="X-User-Token", auto_error=False, scheme_name="User Token", description="User Token")
auth_token_header = APIKeyHeader(name="X-Auth-Token", auto_error=False, scheme_name="Auth Token", description="Auth Token")
