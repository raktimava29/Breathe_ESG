from django.db import models


class Tenant(models.Model):
    """Company / organization boundary for all ESG data."""

    slug = models.SlugField(max_length=64, unique=True)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
