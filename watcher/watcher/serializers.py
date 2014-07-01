from rest_framework import serializers
from watcher.models import Website

class WebsiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Website
        fields = ('id', 'created', 'url', 'status')
