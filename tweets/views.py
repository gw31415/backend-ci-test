from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Exists, OuterRef
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView, View

from tweets.forms import TweetCreateForm
from tweets.models import Tweet


class HomeView(LoginRequiredMixin, ListView):
    template_name = "tweets/home.html"
    model = Tweet

    def get_queryset(self, **kwargs):
        return (
            Tweet.objects.select_related("user")
            .prefetch_related("liked_by")
            .order_by("-created_at")
            .annotate(
                like_counts=Count("liked_by"),
                is_liked=Exists(
                    Tweet.objects.filter(
                        pk=OuterRef("pk"),
                        liked_by=self.request.user,
                    ),
                ),
            )
        )


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["like_counts"] = self.object.liked_by.count()
        context["is_liked"] = self.object.liked_by.filter(
            pk=self.request.user.pk,
        ).exists()
        return context


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


class LikeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        tweet = get_object_or_404(Tweet, pk=self.kwargs["pk"])
        tweet.liked_by.add(request.user)
        previous_url = request.META.get("HTTP_REFERER")
        if previous_url is None:
            return HttpResponse("ok")
        return redirect(previous_url)


class UnlikeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        tweet = get_object_or_404(Tweet, pk=self.kwargs["pk"])
        tweet.liked_by.remove(request.user)
        previous_url = request.META.get("HTTP_REFERER")
        if previous_url is None:
            return HttpResponse("ok")
        return redirect(previous_url)
