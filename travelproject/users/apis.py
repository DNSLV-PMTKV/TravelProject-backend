from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from travelproject.users.services import user_create


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
