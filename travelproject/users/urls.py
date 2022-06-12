from django.urls import path
from travelproject.users.apis import (
    UserAddApi,
    UserChangePasswordApi,
    UserDeleteApi,
    UserDetailApi,
    UserListApi,
    UserMeApi,
    UserUpdateApi,
)

app_name = "users"

urlpatterns = [
    path("create/", UserAddApi.as_view(), name="user_create"),
    path("me/", UserMeApi.as_view(), name="user_me"),
    path("<int:user_id>/", UserDetailApi.as_view(), name="user_detail"),
    path("list/", UserListApi.as_view(), name="user_list"),
    path("delete/", UserDeleteApi.as_view(), name="user_delete"),
    path("update/", UserUpdateApi.as_view(), name="user_update"),
    path("password/", UserChangePasswordApi.as_view(), name="user_change_passord"),
]
