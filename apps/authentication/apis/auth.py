from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from rest_framework import permissions
from rest_framework_simplejwt.tokens import RefreshToken

from drf_spectacular.utils import extend_schema

from apps.users.models import UserStats
from apps.users.models import BaseUser
from apps.utils.otp import generate_and_store_otp, verify_otp, limit_otp


class LoginView(APIView):

    class LoginInputSerializer(serializers.Serializer):
        mobile = serializers.CharField(max_length=13)

        def validate_mobile(self, value):
            if not value.startswith('+98'):
                raise serializers.ValidationError("Mobile number must start with '+98'.")
            if len(value) != 13:
                raise serializers.ValidationError("Mobile number must be exactly 13 characters long.")
            return value

    @extend_schema(
        request=LoginInputSerializer,
    )
    def post(self, request):
        serializer = self.LoginInputSerializer(data=request.data)
        if serializer.is_valid():
            mobile = serializer.validated_data['mobile']
            user, created = BaseUser.objects.get_or_create(mobile=mobile)
            UserStats.objects.get_or_create(user=user)
            if limit_otp(mobile):
                return Response({"message": "Existing OTP still valid", "mobile": mobile}, status=status.HTTP_200_OK)

            generate_and_store_otp(mobile)
            return Response({"message": "OTP generated", "mobile": mobile}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    class VerifyOTPInputSerializer(serializers.Serializer):
        mobile = serializers.CharField(max_length=13)
        otp = serializers.CharField(max_length=6)

        def validate_mobile(self, value):
            if not value.startswith('+98'):
                raise serializers.ValidationError("Mobile number must start with '+98'.")
            if len(value) != 13:
                raise serializers.ValidationError("Mobile number must be exactly 13 characters long.")
            return value


    @extend_schema(
        request=VerifyOTPInputSerializer,
    )
    def post(self, request):
        serializer = self.VerifyOTPInputSerializer(data=request.data)
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
