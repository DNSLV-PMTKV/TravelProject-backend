from django.shortcuts import get_object_or_404

from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from travelproject.users.models import User
from travelproject.users.services import (
    user_change_password,
    user_create,
    user_delete,
    user_list,
    user_update,
)


class UserAddApi(APIView):
    class InputSerializer(serializers.Serializer):
        first_name = serializers.CharField()
        last_name = serializers.CharField()
        email = serializers.EmailField()
        password = serializers.CharField()
        re_password = serializers.CharField()

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        email = serializers.CharField()
        first_name = serializers.CharField()
        last_name = serializers.CharField()

    def post(self, request, *args, **kwargs):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        created_user = user_create(
            email=serializer.get("email"),
            first_name=serializer.get("first_name"),
            last_name=serializer.get("last_name"),
            password=serializer.get("password"),
            re_password=serializer.get("re_password"),
        )

        return Response(self.OutputSerializer(created_user).data)


class UserMeApi(APIView):
    permission_classes = [IsAuthenticated]

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        email = serializers.CharField()
        first_name = serializers.CharField()
        last_name = serializers.CharField()

    def get(self, request, *args, **kwargs):
        return Response(
            self.OutputSerializer(request.user, context={"request": request}).data
        )


class UserDetailApi(APIView):
    permission_classes = [IsAuthenticated]

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        email = serializers.CharField()
        first_name = serializers.CharField()
        last_name = serializers.CharField()

    def get(self, request, user_id: int, *args, **kwargs):
        user = get_object_or_404(User, id=user_id)
        return Response(self.OutputSerializer(user).data)


class UserListApi(APIView):
    permission_classes = [IsAuthenticated]

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        email = serializers.CharField()
        first_name = serializers.CharField()
        last_name = serializers.CharField()

    def get(self, request, *args, **kwargs):
        users = user_list()
        return Response(self.OutputSerializer(users, many=True).data)


class UserUpdateApi(APIView):
    permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        email = serializers.CharField()
        first_name = serializers.CharField()
        last_name = serializers.CharField()

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        email = serializers.CharField()
        first_name = serializers.CharField()
        last_name = serializers.CharField()

    def put(self, request, *args, **kwargs):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = user_update(user=request.user, data=serializer.validated_data)
        return Response(data=self.OutputSerializer(user).data)


class UserDeleteApi(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user_delete(user=request.user)
        return Response(status=status.HTTP_200_OK)


class UserChangePasswordApi(APIView):
    permission_classes = [IsAuthenticated]

    class InputSerializer(serializers.Serializer):
        old_password = serializers.CharField()
        new_password = serializers.CharField()
        re_password = serializers.EmailField()

    def post(self, request, *args, **kwargs):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_change_password(
            user=request.user,
            old_password=serializer.validated_data["old_password"],
            new_password=serializer.validated_data["new_password"],
            re_password=serializer.validated_data["re_password"],
        )

        return Response(status=status.HTTP_200_OK)
