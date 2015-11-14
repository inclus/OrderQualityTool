from django.db import models
from custom_user.models import AbstractEmailUser
from locations.models import Location

class DashboardUser(AbstractEmailUser):
    location = models.ForeignKey(Location, null=True, blank=True)
