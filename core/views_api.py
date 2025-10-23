from rest_framework import viewsets, permissions
from .models import Post, SiteConfiguration
from .serializers import PostSerializer, SiteConfigSerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class SiteConfigViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SiteConfiguration.objects.all()
    serializer_class = SiteConfigSerializer
    permission_classes = [permissions.AllowAny]
