from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            # Try to fetch the user by searching the username or email field
            user = UserModel.objects.filter(email=username).first()
            if not user:
                user = UserModel.objects.filter(username=username).first()
            
            if user and user.check_password(password) and self.user_can_authenticate(user):
                return user
        except UserModel.DoesNotExist:
            return None
