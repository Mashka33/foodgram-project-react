# from .serializers import (FollowSerializer, FollowedSerializer,
#                           CustomPasswordRetypeSerializer)
# from rest_framework import mixins, permissions, status, views, viewsets, filters
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from api.pagination import CustomPagination
# from rest_framework.generics import ListAPIView
#
#
# class FollowedViewSet(mixins.CreateModelMixin,
#                       mixins.ListModelMixin,
#                       viewsets.GenericViewSet):
#     serializer_class = FollowedSerializer
#     permission_classes = [IsAuthenticated]
#     filter_backends = [filters.SearchFilter]
#     search_fields = ('following__username', 'user__username',)
#
#     def get_queryset(self):
#         return self.request.user.follower.all()
#
#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)
#
#
# class FollowView(ListAPIView):
#     serializer_class = FollowSerializer
#     pagination_class = CustomPagination
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         user = self.request.user
#         return user.follower.all()
#
#
# class SetPasswordRetypeView(views.APIView):
#     permission_classes = [permissions.IsAuthenticated]
#
#     def post(self, request):
#         serializer = CustomPasswordRetypeSerializer(
#             data=request.data,
#             context={
#                 'request': request,
#                 'format': self.format_kwarg,
#                 'view': self
#             }
#         )
#         if serializer.is_valid():
#             self.request.user.set_password(serializer.data['new_password'])
#             self.request.user.save()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
