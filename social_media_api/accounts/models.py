from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    
    Adds social media specific fields:
    - bio: A text field for user biography
    - profile_picture: Image field for user's profile picture
    - followers: ManyToMany self-referential field for following relationships
    """
    bio = models.TextField(
        blank=True,
        null=True,
        help_text="User's biography or about section"
    )
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        help_text="User's profile picture"
    )
    followers = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='following',
        blank=True,
        help_text="Users who follow this user"
    )

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        db_table = 'accounts_user'

    def __str__(self):
        return f"{self.username} ({self.get_full_name()})" if self.get_full_name() else self.username

    def follower_count(self):
        """Returns the number of followers."""
        return self.followers.count()

    def following_count(self):
        """Returns the number of users this user is following."""
        return self.following.count()

    def is_following(self, user):
        """Check if this user follows another user."""
        return self.following.filter(pk=user.pk).exists()

    def follow(self, user):
        """Follow another user."""
        if not self.is_following(user) and self != user:
            self.following.add(user)

    def unfollow(self, user):
        """Unfollow another user."""
        if self.is_following(user):
            self.following.remove(user)