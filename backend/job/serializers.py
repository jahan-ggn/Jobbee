from rest_framework import serializers
from .models import CandidatesApplied, Job


class JobSerilaizer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = "__all__"

class CandidatesAppliedSerializer(serializers.ModelSerializer):
    job = JobSerilaizer()
    class Meta:
        model = CandidatesApplied
        fields = ('user', 'resume', 'appliedAt', 'job')