from .models import CustomUser
from rest_framework.authentication import BaseAuthentication
from rest_framework.authentication import get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
import jwt


class UserTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        """
        The `authenticate` function takes a request object, decodes the authorization token, verifies its
        validity, and returns the corresponding user and role if authentication is successful.

        :param request: The `request` parameter is an object that represents the HTTP request being made to
        the server. It contains information about the request, such as the headers, body, and other
        metadata. In this code snippet, the `request` parameter is used to extract the authorization header,
        which contains the token used
        :return: The authenticate function returns two values: 'admin' and 'de_value["role"]'.
        """
        try:
            print("User inside the authenticate")
            token = get_authorization_header(request).decode("utf-8").split()
            if len(token) == 2:
                de_value = jwt.decode(token[1], "user_key", algorithms=["HS256"])
                admin = CustomUser.objects.filter(id=de_value["id"])
                print(de_value)
                if admin.exists():
                    return admin, de_value["role"]
                else:
                    raise AuthenticationFailed("Token authentication failed.")
            else:
                raise AuthenticationFailed("Token authentication failed.")
        except (jwt.ExpiredSignatureError, jwt.InvalidSignatureError):
            raise AuthenticationFailed("Token authentication failed.")
        except Exception:
            raise AuthenticationFailed("Token authentication failed.")
        
class AdminTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        """
        The `authenticate` function takes a request object, decodes the authorization token, verifies its
        validity, and returns the corresponding user and role if authentication is successful.

        :param request: The `request` parameter is an object that represents the HTTP request being made to
        the server. It contains information about the request, such as the headers, body, and other
        metadata. In this code snippet, the `request` parameter is used to extract the authorization header,
        which contains the token used
        :return: The authenticate function returns two values: 'admin' and 'de_value["role"]'.
        """
        try:
            print("User inside the authenticate")
            token = get_authorization_header(request).decode("utf-8").split()
            if len(token) == 2:
                de_value = jwt.decode(token[1], "admin_key", algorithms=["HS256"])
                admin = CustomUser.objects.filter(id=de_value["id"])
                print(de_value)
                if admin.exists():
                    return admin, de_value["role"]
                else:
                    raise AuthenticationFailed("Token authentication failed.")
            else:
                raise AuthenticationFailed("Token authentication failed.")
        except (jwt.ExpiredSignatureError, jwt.InvalidSignatureError):
            raise AuthenticationFailed("Token authentication failed.")
        except Exception:
            raise AuthenticationFailed("Token authentication failed.")