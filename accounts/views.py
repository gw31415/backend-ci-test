from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, View, DetailView

from .forms import LoginForm, SignUpForm

User = get_user_model()


class SignUpView(CreateView):
    template_name = "accounts/signup.html"
    form_class = SignUpForm
    success_url = reverse_lazy("tweets:home")

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


class LoginView(LoginView):
    form_class = LoginForm
    template_name = "accounts/login.html"


class LogoutView(LoginRequiredMixin, LogoutView):
    template_name = "welcome/index.html"

class UserProfileView(LoginRequiredMixin, DetailView):
    def get(self, request, *args, **kwargs):
        requested_user = get_object_or_404(User, username=kwargs.get("username"))
        requested_username = requested_user.get_username()
#        user_tweets = Tweet.objects.filter(user=requested_user)
#        follower_count = FriendShip.objects.filter(followee=requested_user).count()
#        followee_count = FriendShip.objects.filter(follower=requested_user).count()
        context = {
                #            "follower_count": follower_count,
                #            "followee_count": followee_count,
                #            "user_tweets": user_tweets,
            "requested_username": requested_username,
        }
        return render(request, "accounts/profile.html", context)
#class UserProfileView(TemplateView):
#    def get_username(self, **kwargs):
#        username = super().get_username(**kwargs)
#        return username
#    username = get_username()
#
#    template_name = "accounts/profile.html"
