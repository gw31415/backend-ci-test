from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView, View

from tweets.forms import TweetCreateForm
from tweets.models import Tweet


class HomeView(LoginRequiredMixin, ListView):
    template_name = "tweets/home.html"
    model = Tweet

    def get_queryset(self, **kwargs):
        return Tweet.objects.select_related("user").order_by("-created_at")


class TweetCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = TweetCreateForm()
        return render(request, "tweets/create.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = TweetCreateForm(data=request.POST)
        if form.is_valid():
            content = form.cleaned_data.get("content")
            Tweet.objects.create(user=request.user, content=content)
            return redirect("tweets:home")
        return render(request, "tweets/create.html", {"form": form})


class TweetDetailView(LoginRequiredMixin, DetailView):
    template_name = "tweets/detail.html"
    model = Tweet
    queryset = Tweet.objects.select_related("user")


class TweetDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        tweet = get_object_or_404(
            Tweet,
            pk=kwargs.get("pk"),
        )
        if tweet.user != request.user:
            return HttpResponseForbidden()
        tweet.delete()
        return redirect("tweets:home")
