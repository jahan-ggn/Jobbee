from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Avg, Min, Count, Max
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist


from .serializers import CandidatesAppliedSerializer, JobSerilaizer
from .models import CandidatesApplied, Job
from .filters import JobsFilter

from django.shortcuts import get_object_or_404

# Create your views here.
@api_view(["GET"])
def getAllJobs(request):
    filterset = JobsFilter(request.GET, queryset=Job.objects.all().order_by("id"))
    count = filterset.qs.count()
    resPerPage = 3
    paginator = PageNumberPagination()
    paginator.page_size = resPerPage
    queryset = paginator.paginate_queryset(filterset.qs, request)

    serializer = JobSerilaizer(queryset, many=True)
    return Response({"count": count, "resPerPage": resPerPage, "jobs": serializer.data})


@api_view(["GET"])
def getJob(request, pk):
    job = get_object_or_404(Job, id=pk)
    serializer = JobSerilaizer(job, many=False)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def newJob(request):
    request.data["user"] = request.user
    data = request.data
    job = Job.objects.create(**data)
    serializer = JobSerilaizer(job, many=False)
    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def updateJob(request, pk):
    job = get_object_or_404(Job, id=pk)
    if job.user != request.user:
        return Response(
            {"message": "You cannot update this job"}, status=status.HTTP_403_FORBIDDEN
        )
    job.title = request.data["title"]
    job.description = request.data["description"]
    job.email = request.data["email"]
    job.address = request.data["address"]
    job.jobType = request.data["jobType"]
    job.industry = request.data["industry"]
    job.education = request.data["education"]
    job.experience = request.data["experience"]
    job.salary = request.data["salary"]
    job.positions = request.data["positions"]
    job.company = request.data["company"]

    job.save()

    serializer = JobSerilaizer(job, many=False)
    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def deleteJob(request, pk):
    job = get_object_or_404(Job, id=pk)
    if job.user != request.user:
        return Response(
            {"message": "You cannot update this job"}, status=status.HTTP_403_FORBIDDEN
        )
    job.delete()
    return Response({"message": "Job is deleted"}, status=status.HTTP_200_OK)


@api_view(["GET"])
def getTopicStats(request, topic):
    args = {"title__icontains": topic}
    jobs = Job.objects.filter(**args)

    if len(jobs) == 0:
        return Response({"message": "No stats found for {topic}".format(topic=topic)})

    stats = jobs.aggregate(
        total_jobs=Count("title"),
        avg_positions=Avg("positions"),
        avg_salary=Avg("salary"),
        min_salary=Min("salary"),
        max_salary=Max("salary"),
    )

    return Response(stats)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def applyToJob(request, pk):
    user = request.user
    job = get_object_or_404(Job, id=pk)
    try:
        resume = user.userprofile.resume
    except ObjectDoesNotExist:
        return Response(
            {"error": "Please upload your resume first"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if job.last_date < timezone.now():
        return Response(
            {"error": "You cannot apply to this job. Date is over"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    alreadyApplied = job.candidatesapplied_set.filter(user=user).exists()
    if alreadyApplied:
        return Response(
            {"error": "You have already applied to this job."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    jobApplied = CandidatesApplied.objects.create(
        job=job, user=user, resume=resume
    )
    return Response({"applied": True, "job_id": jobApplied.id}, status=status.HTTP_200_OK)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getCurrentUserAppliedJobs(request):
    args = { 'user_id': request.user.id}
    jobs = CandidatesApplied.objects.filter(**args)
    serialzer = CandidatesAppliedSerializer(jobs, many=True)
    return Response(serialzer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def isAppliedToJob(request, pk):
    user = request.user
    job = get_object_or_404(Job, id=pk)
    applied = job.candidatesapplied_set.filter(user=user).exists()
    return Response(applied)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def getCurrentUserJos(request):
    args = { 'user': request.user.id }
    jobs = Job.objects.filter(**args)
    serializer = JobSerilaizer(jobs, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getCandidatesApplied(request, pk):

    user = request.user
    job = get_object_or_404(Job, id=pk)

    if job.user != user:
        return Response({ 'error': 'You can not acces this job' }, status=status.HTTP_403_FORBIDDEN)

    candidates = job.candidatesapplied_set.all()

    serializer = CandidatesAppliedSerializer(candidates, many=True)

    return Response(serializer.data)