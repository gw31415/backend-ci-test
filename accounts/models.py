from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(max_length=254)
    following = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="follower",
    )


# class FriendShip(models.Model):
#     pass
