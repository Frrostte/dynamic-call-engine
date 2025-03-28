from django.db import models
from django.conf import settings

class Campaign(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    company_details = models.TextField()
    product_service = models.TextField()
    marketing_keywords = models.TextField()
    starting_pitch = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    chatbot_interactions = models.IntegerField(default=0)
    conversion_rate = models.FloatField(default=0.0)
    average_interaction_duration = models.DurationField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    def __str__(self):
        return self.name

class Contact(models.Model):
    campaign = models.ForeignKey(Campaign, related_name='contacts', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, blank=True)
    location = models.CharField(max_length=100, blank=True)
    call_status = models.CharField(max_length=20, default='pending')
    call_recording_url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.name} - {self.phone_number}"