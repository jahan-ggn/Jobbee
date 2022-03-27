from dataclasses import fields
from pyexpat import model
from rest_framework import serializers
from .models import Job


class JobSerilaizer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = "__all__"
