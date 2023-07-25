from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.db import models



class UserFollows(models.Model):
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following')
    followed_user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followers')

    class Meta:
        # ensures we don't get multiple UserFollows instances
        # for unique user-user_followed pairs
        unique_together = ('user', 'followed_user', )

    def __str__(self):
        return f'{self.user.username} follows {self.followed_user.username}'
