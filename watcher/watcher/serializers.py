from rest_framework import serializers

class WebsiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Website
        fields = ('id', 'created', 'url', 'status')
