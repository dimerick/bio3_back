from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import CustomUser, Profile, University, Degree, FieldsOfStudy, Project, Community, ProjectImage
from .serializers import CustomUserSerializer, ProfileSerializer, UniversitySerializer, DegreeSerializer, ProjectSerializer, CommunitySerializer, ProjectImageSerializer
from django.http import Http404
import googlemaps
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.tokens import default_token_generator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.utils import timezone
from django.db import connection
from django.http import JsonResponse
from django.conf import settings
from rest_framework.permissions import BasePermission

# Create your views here.

class IsOwnerOrReadOnly(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `created_by_id`.
        print(request.user)
        return obj.created_by_id == request.user.id

class HelloBio3science(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]


    def get(self, request):
        content = {"message": "Alersnet Rocking"}
        return Response(content)

class Place(APIView):
    #permission_classes = [permissions.IsAuthenticated]


    def get(self, request, input_search):

        gmaps = googlemaps.Client(key=settings.GOOGLE_KEY)

        #input_search = request.get['input_search']

        #result = gmaps.find_place(input_search, 'textquery', ['business_status', 'formatted_address', 'geometry', 'icon', 'name', 'photos', 'place_id', 'plus_code', 'types'])

        result = gmaps.places_autocomplete_query(input_search, 3)

        return Response(result)

class AccountList(APIView):

    def get(self, request, format=None):

        email = request.GET.get('email', None)
        if(email):
            objs = CustomUser.objects.filter(email=email)
        else:
            objs = CustomUser.objects.all()
            
        serializer = CustomUserSerializer(objs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            if user:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class AccountDetail(APIView):    

    def get_object(self, pk):
        try:
            return CustomUser.objects.get(id=pk)
        except CustomUser.DoesNotExist:
            raise Http404
    
    def get(self, request, pk=None, format=None):

        
        obj = self.get_object(pk)
        
        serializer = CustomUserSerializer(obj)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        obj = self.get_object(pk)
        serializer = CustomUserSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        obj = self.get_object(pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# class AccountByEmail(APIView):
        
#     def get(self, request, email, format=None):
#         user = get_object_by_email(email)
#         serializer = CustomUserSerializer(user)
#         return Response(serializer.data)

class ProfileList(APIView):

    def get(self, request, format=None):
        objs = Profile.objects.all()
        serializer = ProfileSerializer(objs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProfileSerializer(data=request.data)
        
        if serializer.is_valid():
            obj = serializer.save()
            if obj:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UniversityList(APIView):

    def get(self, request, format=None):

        name = request.GET.get('name', None)
        exclude_id = request.GET.get('exclude_id', None)
        if(name):
            objs = University.objects.filter(name__icontains=name)
        elif(exclude_id):
            objs = University.objects.exclude(id=exclude_id)
        else:
            objs = University.objects.all()

        serializer = UniversitySerializer(objs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UniversitySerializer(data=request.data)
        
        if serializer.is_valid():
            obj = serializer.save()
            if obj:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UniversityDetail(APIView):    

    def get_object(self, pk):
        try:
            return University.objects.get(id=pk)
        except University.DoesNotExist:
            raise Http404

    
    def get(self, request, pk, format=None):
        obj = self.get_object(pk)
        serializer = UniversitySerializer(obj)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        obj = self.get_object(pk)

        # created_by = request.GET.get('created_by', None)
        # if(created_by):
        #     obj.created_by = CustomUser.objects.get(id=created_by)
        #     obj.save()
        #     serializer = UniversitySerializer(data=obj)
        #     if serializer.is_valid():
        #         return Response(serializer.data)

        serializer = UniversitySerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        obj = self.get_object(pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class DegreeList(APIView):

    def get(self, request, format=None):
        degrees = Degree.objects.all()
        serializer = DegreeSerializer(degrees, many=True)
        return Response(serializer.data)

class FieldsOfStudyList(APIView):

    def get(self, request, format=None):
        items = FieldsOfStudy.objects.all()
        serializer = DegreeSerializer(items, many=True)
        return Response(serializer.data)

class GenerateTokenResetPassword(APIView):

    def get_object(self, email):
        try:
            return CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise Http404

    def get(self, request):
        email = request.GET.get('email', None)
        obj = self.get_object(email)
        token = default_token_generator.make_token(obj)
        print(token)



class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        user.last_login = timezone.now()
        user.save()
        # ...

        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class ProjectList(APIView):

    def get(self, request, format=None):

        name = request.GET.get('name', None)
        user = request.GET.get('user', None)
        if(user):
            objs = Project.objects.filter(created_by_id=user, is_active=True).order_by('-created_at')
        if(name):
            objs = Project.objects.filter(name__icontains=name, is_active=True).order_by('-created_at')
        else:
            objs = Project.objects.all().filter(is_active=True).order_by('-created_at')

        serializer = ProjectSerializer(objs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        
        if serializer.is_valid():
            obj = serializer.save()
            if obj:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProjectDetail(APIView):    

    # serializer_class = ProjectSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_object(self, pk):
        try:
            obj = Project.objects.get(id=pk, is_active=True)
            self.check_object_permissions(self.request, obj)
            return obj
        except Project.DoesNotExist:
            raise Http404

    
    def get(self, request, pk, format=None):
        obj = self.get_object(pk)
        serializer = ProjectSerializer(obj)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        obj = self.get_object(pk)
        serializer = ProjectSerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        obj = self.get_object(pk)
        obj.is_active = False
        obj.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk, format=None):
        obj = self.get_object(pk)
        serializer = ProjectSerializer(obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProjectImageList(APIView):

    def get(self, request, format=None):

        project = request.GET.get('project', None)
        if(project):
            objs = ProjectImage.objects.filter(project=project)
        else:
            objs = ProjectImage.objects.all()

        serializer = ProjectImageSerializer(objs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProjectImageSerializer(data=request.data)
        
        if serializer.is_valid():
            obj = serializer.save()
            if obj:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommunityList(APIView):

    def get(self, request, format=None):
        objs = Community.objects.all()
        serializer = CommunitySerializer(objs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CommunitySerializer(data=request.data)
        
        if serializer.is_valid():
            obj = serializer.save()
            if obj:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommunityDetail(APIView):    

    def get_object(self, pk):
        try:
            return Community.objects.get(id=pk)
        except Community.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        obj = self.get_object(pk)
        serializer = CommunitySerializer(obj)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        obj = self.get_object(pk)
        serializer = CommunitySerializer(obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        obj = self.get_object(pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

def dictfetchall(cursor):
        "Return all rows from a cursor as a dict"
        columns = [col[0] for col in cursor.description]
        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

class ProjectNetworkList(APIView):
    
    def get(self, request, format=None):
        with connection.cursor() as cursor:
            cursor.execute("select project.id, project.name, project.description, project.created_at, uni.name as universidad, ST_X(uni.location) as long, ST_Y(uni.location) as lat, ST_AsText(ST_Transform(uni.location, 4326)) as uni_location, user2.id as user_id, user2.name as user_name, user2.last_name as user_last_name from bio3_project project inner join bio3_university uni on project.main_university_id = uni.id inner join bio3_customuser user2 on project.created_by_id = user2.id where project.is_active = true;")
            projects = dictfetchall(cursor)
            for i in range(0, len(projects)):
                cursor.execute("select ST_X(uni.location) as long, ST_Y(uni.location) as lat, ST_X(uni_assoc.location) as long_assoc, ST_Y(uni_assoc.location) as lat_assoc from bio3_project project inner join bio3_university uni on project.main_university_id = uni.id inner join bio3_project_universities pu on project.id = pu.project_id inner join bio3_university uni_assoc on pu.university_id = uni_assoc.id where project.id = %s;", [projects[i]['id']])
                projects[i]['universities_network'] = dictfetchall(cursor)

                cursor.execute("select ST_X(uni.location) as long, ST_Y(uni.location) as lat, ST_X(community_assoc.location) as long_assoc, ST_Y(community_assoc.location) as lat_assoc from bio3_project project inner join bio3_university uni on project.main_university_id = uni.id inner join bio3_project_communities pc on project.id = pc.project_id inner join bio3_community community_assoc on pc.community_id = community_assoc.id where project.id = %s;", [projects[i]['id']])
                projects[i]['communities_network'] = dictfetchall(cursor)

                cursor.execute("select id, concat(%s, image) as url from bio3_projectimage where project_id = %s;", [settings.MEDIA_URL, projects[i]['id']])
                projects[i]['images'] = dictfetchall(cursor)

            return JsonResponse(projects, safe=False)

class NodesNetworkList(APIView):
    def get(self, request, format=None):
        nodes = dict()
        with connection.cursor() as cursor:
            cursor.execute("select uni.id, min(uni.name) as name, min(uni.long) as long, min(uni.lat) as lat, 10+exp(sum(uni.points)*0.001) as points from (select min(uni.id) as id, min(uni.name) as name, min(ST_X(uni.location)) as long, min(ST_Y(uni.location)) as lat, count(uni.id)*1 as points from bio3_project project inner join bio3_university uni on project.main_university_id = uni.id where project.is_active = true group by uni.id union all select min(uni.id) as id, min(uni.name) as name, min(ST_X(uni.location)) as long, min(ST_Y(uni.location)) as lat, count(uni.id)*0.5 as points from bio3_project project inner join bio3_project_universities pu on project.id = pu.project_id inner join bio3_university uni on pu.university_id = uni.id where project.is_active = true group by university_id) as uni group by uni.id;")
            nodes['universities'] = dictfetchall(cursor)
        
        with connection.cursor() as cursor2:
            cursor2.execute("select pc.community_id as id, min(community.name) as name, min(ST_X(community.location)) as long, min(ST_Y(community.location)) as lat, 10+exp((count(pc.community_id) * 0.5)*0.001) as points from bio3_project_communities pc inner join bio3_project project on pc.project_id = project.id inner join bio3_community community on pc.community_id = community.id where project.is_active = true group by pc.community_id;")
            nodes['communities'] = dictfetchall(cursor2)
        return JsonResponse(nodes, safe=False)