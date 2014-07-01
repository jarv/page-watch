from django.db import models
from model_utils import Choices

class Website(models.Model):
    STATUS = Choices('initialized', 'processing', 'processed')
    created = models.DateTimeField(auto_now_add=True)
    url = models.URLField()
    status = models.CharField(max_length=32, choices=STATUS, default=STATUS.initialized)

    class Meta:
        ordering = ('created',)
