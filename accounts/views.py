from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Exists, OuterRef
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, RedirectView

from tweets.models import Tweet

from .forms import SignUpForm

User = get_user_model()


class SignUpView(CreateView):
    template_name = "accounts/signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password1"]
        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            login(self.request, user)
            return response
        else:
            return redirect("welcome:top")


class LoginView(auth_views.LoginView):
    template_name = "accounts/login.html"


class LogoutView(LoginRequiredMixin, auth_views.LogoutView):
    pass


class UserProfileView(LoginRequiredMixin, ListView):
    template_name = "accounts/profile.html"
    model = Tweet
    queryset = Tweet.objects.select_related("user")

    def get_queryset(self, **kwargs):
        username = self.kwargs.get("username")
        user = get_object_or_404(User, username=username)  # Userオブジェクトを取得
        queryset = (
            self.queryset.filter(user=user)  # Userオブジェクトでフィルター
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
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs["username"])
        context["username"] = user.username
        context["followings_count"] = user.following.count()
        context["followers_count"] = User.objects.filter(
            following=user,
        ).count()
        context["is_following"] = self.request.user.following.filter(
            username=user.username,
        ).exists()
        return context


# コピペ元amaさん
class FollowingListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "accounts/following.html"

    # デフォルトでは単にモデルのオブジェクトを並べるだけ
    def get_queryset(self, **kwargs):
        user = get_object_or_404(
            User.objects.prefetch_related("following"),
            username=self.kwargs.get("username"),
        )
        return user.following.all()

    def get_context_deta(self, **kwargs):
        context = super().get_context_deta(**kwargs)
        context["username"] = self.kwargs["username"]
        return context


class FollowerListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "accounts/follower.html"

    def get_queryset(self, **kwargs):
        user = get_object_or_404(
            User.objects.prefetch_related("follower"),
            username=self.kwargs.get("username"),
        )
        return user.follower.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["username"] = self.kwargs["username"]
        return context


class FollowView(LoginRequiredMixin, RedirectView):
    url = reverse_lazy("tweets:home")
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        if self.kwargs["username"] == request.user.username:
            return HttpResponseBadRequest("自分自身をフォローすることはできません。")
        target_user = get_object_or_404(User, username=self.kwargs["username"])
        request.user.following.add(target_user)
        return super().post(request, *args, **kwargs)


class UnFollowView(LoginRequiredMixin, RedirectView):
    url = reverse_lazy("tweets:home")
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        if self.kwargs["username"] == request.user.username:
            return HttpResponseBadRequest("自分自身にリクエストできません。")
        target_user = get_object_or_404(User, username=self.kwargs["username"])
        request.user.following.remove(target_user)
        return super().post(request, *args, **kwargs)
