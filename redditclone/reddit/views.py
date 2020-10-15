from django.shortcuts import render
from rest_framework import generics, permissions, mixins
from rest_framework.exceptions import ValidationError, status
from rest_framework.response import Response
from .models import Post, Vote
from .serializers import Postserializers, Voteserializers

# Create your views here.


class Postlist(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = Postserializers
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(poster = self.request.user)

class Postview(generics.RetrieveDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = Postserializers
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def delete(self, request, *args, **kwargs):
        post = Post.objects.filter(pk = kwargs['pk'], poster= self.request.user)
        if post.exists():
            return self.destroy(self, *args, **kwargs)
        else:
            raise ValidationError("This post does not belongs to you. ")


         

class Votecreate(generics.CreateAPIView, mixins.DestroyModelMixin):
    serializer_class = Voteserializers
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        post = Post.objects.get(pk = self.kwargs['pk'])
        return Vote.objects.filter(voter = user, post = post)

    def perform_create(self, serializer):
        if self.get_queryset().exists():
            raise ValidationError("You have already voted ")
        serializer.save(voter = self.request.user, post = Post.objects.get(pk = self.kwargs['pk']))

    def delete(self, request, *args, **kwargs):
        if self.get_queryset().exists():
            self.get_queryset().delete()
            return Response(status = status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError("You have already deleted this upvote ")


