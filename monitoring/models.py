from django.db import models
from django.conf import settings
from trees.models import Tree


class FollowUp(models.Model):
    FOLLOWUP_TYPE = [
        ('1_month', '1 Month'),
        ('6_month', '6 Months'),
        ('1_year', '1 Year'),
    ]
    tree = models.ForeignKey(Tree, on_delete=models.CASCADE)
    scheduled_date = models.DateField()
    type = models.CharField(max_length=32, choices=FOLLOWUP_TYPE)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"FollowUp {self.type} for {self.tree.tree_id}"


class MonitoringReport(models.Model):
    HEALTH_STATUS = [
        ('healthy', 'Healthy'),
        ('at_risk', 'At Risk'),
        ('failed', 'Failed'),
    ]
    site = models.ForeignKey('beneficiaries.PlantingSite', null=True, blank=True, on_delete=models.SET_NULL)
    tree = models.ForeignKey(Tree, null=True, blank=True, on_delete=models.SET_NULL)
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    date = models.DateField(auto_now_add=True)
    total_planted = models.PositiveIntegerField(default=0)
    surviving = models.PositiveIntegerField(default=0)
    growth_notes = models.TextField(blank=True)
    health_status = models.CharField(max_length=16, choices=HEALTH_STATUS, default='healthy')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    weather = models.JSONField(null=True, blank=True)
    soil_type = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # optional link to media app (many-to-many)
    media = models.ManyToManyField('media_app.Media', blank=True)

    class Meta:
        ordering = ['-date', '-created_at']

    @property
    def survival_rate(self):
        if not self.total_planted:
            return None
        return round((self.surviving / self.total_planted) * 100, 2)

    def __str__(self):
        label = self.site.name if self.site else (self.tree.tree_id if self.tree else 'Report')
        return f"MonitoringReport {label} @ {self.date}"
