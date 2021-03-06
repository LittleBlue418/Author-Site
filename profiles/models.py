from django_countries.fields import CountryField
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    A User Profile model for storing the default delivery
    information for the user
    """
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile'
    )
    default_phone_number = models.CharField(
        max_length=20, null=True, blank=True, verbose_name='Phone Number'
    )
    default_street_address1 = models.CharField(
        max_length=80, null=True, blank=True, verbose_name='Street Address 1'
    )
    default_street_address2 = models.CharField(
        max_length=80, null=True, blank=True, verbose_name='Street Address 2'
    )
    default_town_or_city = models.CharField(
        max_length=40, null=True, blank=True, verbose_name='Town or City'
    )
    default_county = models.CharField(
        max_length=80, null=True, blank=True, verbose_name='County or State'
    )
    default_postcode = models.CharField(
        max_length=20, null=True, blank=True, verbose_name='Post Code'
    )
    default_country = CountryField(
        blank_label='Country ', null=True, blank=True, verbose_name='Country'
    )

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, raw, **kwargs):
    """
    Create or update the user profile based on changes from the User model
    """
    # For db migrations
    if raw:
        return
    if created:
        UserProfile.objects.create(user=instance)

    instance.profile.save()
