from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from rest_framework import permissions
from rest_framework_simplejwt.tokens import RefreshToken

from drf_spectacular.utils import extend_schema

from apps.users.models import UserStats
from apps.users.models import BaseUser
from apps.utils.otp import generate_and_store_otp, verify_otp


class LoginView(APIView):

    class InputSerializer(serializers.Serializer):
        mobile = serializers.CharField(max_length=15)

    @extend_schema(
        request=InputSerializer,
    )
    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']
            user, created = BaseUser.objects.get_or_create(mobile=mobile)
            UserStats.objects.get_or_create(user=user)
            otp = generate_and_store_otp(mobile)
            print(otp)
            return Response({"message": "OTP generated", "mobile": mobile}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    class InputSerializer(serializers.Serializer):
        mobile = serializers.CharField(max_length=15)
        otp = serializers.CharField(max_length=6)

    @extend_schema(
        request=InputSerializer,
    )
    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']
            otp = serializer.validated_data['otp']
            if verify_otp(mobile, otp):
                try:
                    user = BaseUser.objects.get(mobile=mobile)
                    # Generate JWT tokens
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        "message": "OTP verified",
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    }, status=status.HTTP_200_OK)
                except BaseUser.DoesNotExist:
                    return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
