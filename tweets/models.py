from django.db import models

from accounts.models import User


class Tweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tweets")
    content = models.TextField(max_length=140)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    liked_by = models.ManyToManyField(
        User,
        related_name="liking",
    )

    def __str__(self):
        return f"{self.user.username} : {self.content}"

    class Meta:
        verbose_name_plural = "ツイート"
