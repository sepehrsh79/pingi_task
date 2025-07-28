from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework import permissions

from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter
from apps.users.models import BaseUser, UserStats
from apps.users.selectors import get_or_create_user_stats, get_user_with_mobile, get_stats_with_user


class NowView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    class NowOutPutSerializer(serializers.Serializer):
        now = serializers.DateTimeField()

    @extend_schema(
        responses=NowOutPutSerializer,
    )
    def get(self, request):
        try:
            stats, _ = get_or_create_user_stats(user_id=request.user.id)
        except BaseUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        stats.open_count += 1
        stats.save()
        # Return current time
        data = {"now": timezone.now()}
        serializer = self.NowOutPutSerializer(data)
        return Response(serializer.data)


class StatsView(APIView):
    #TODO : This api should allow for admins to check user stats
    permission_classes = [permissions.AllowAny]

    class StatsOutPutSerializer(serializers.ModelSerializer):
        user = serializers.CharField(source='user.mobile')

        class Meta:
            model = UserStats
            fields = ['user', 'open_count']

    @extend_schema(
        parameters=[
                OpenApiParameter(name='user',
                                 description="User mobile number, must start with '+98' and be exactly 13 characters long (e.g., '+989123456789').",
                                 type=str,
                                 required=True
                                 ),
            ],
        responses=StatsOutPutSerializer
    )
    def get(self, request):
        user_mobile = request.query_params.get('user')
        if not user_mobile:
            return Response({"error": "Mobile number required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = get_user_with_mobile(mobile=user_mobile)
            stats = get_stats_with_user(user=user)
            serializer = self.StatsOutPutSerializer(stats)
            return Response(serializer.data)
        except BaseUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except UserStats.DoesNotExist:
            return Response({"user": user_mobile, "open_count": 0})
