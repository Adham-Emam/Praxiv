from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.cache import cache


class OpaqueJWTAuthentication(JWTAuthentication):
    """
    Accept opaque tokens instead of raw JWTs.
    Resolves the opaque token from cache to the real JWT, then validates it.
    """

    def get_raw_token(self, header):
        raw_token = super().get_raw_token(header)
        if raw_token is None:
            return None

        # Ensure string (header might give bytes)
        if isinstance(raw_token, bytes):
            raw_token = raw_token.decode("utf-8")

        # Resolve opaque to real JWT
        resolved = cache.get(raw_token)
        if resolved:
            return resolved

        print(f"Token {raw_token} not found in cache")
        print(resolved)

        return raw_token
