from django.urls import path

from travelproject.users.apis import UserAddApi

app_name = "users"

urlpatterns = [
    path("create/", UserAddApi.as_view(), name="user_create")
    # path("register", RegisterView.as_view(), name="register"),
    # path("confirm", ConfirmEmailView.as_view(), name="confirm"),
    # path("login", LoginView.as_view(), name="login"),
    # path("logout", LogoutView.as_view(), name="logout"),
    # path("<int:id>", user_details, name="users_detail_view"),
    # path("me", logged_user, name="logged_user"),
    # path("change_photo", change_profile_picture, name="change_photo"),
    # path("", users_list, name="users_list"),
    # path("forgot_password", ForgotPasswordView.as_view(), name="forgot_password"),
    # path("change_password", ChangePasswordView.as_view(), name="change_password"),
]
