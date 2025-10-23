from django.db import models

class Beneficiary(models.Model):
    BENEFICIARY_TYPE = [
        ('school', 'School'),
        ('church', 'Church'),
        ('community', 'Community Group'),
    ]
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=50, choices=BENEFICIARY_TYPE)
    contact_person = models.CharField(max_length=100, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name


class PlantingSite(models.Model):
    """A physical planting site that can belong to a beneficiary (e.g., school compound)."""
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE, related_name='sites')
    name = models.CharField(max_length=200, blank=True)
    address = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name or self.beneficiary.name}"
