from rest_framework import serializers
from .models import SalesFile , SalesRecord , Profile
from django.contrib.auth.models import User

class RegistrationSerializer(serializers.ModelSerializer):

    class Meta:
       model = User
       fields = ('username', 'email', 'password', 'first_name', 'last_name')

    def validate(self, data):
       if data['password'] == None:
            raise serializers.ValidationError({"password": "Empty password.. chose a strong password"})
       if len(data['password']) < 8:
            raise serializers.ValidationError({"password": "Password must be at least 8 characters long"})
       return data

    def create(self, validated_data):
       password = validated_data.pop('password')
       user = User.objects.create_user(**validated_data, password=password)
       return user

class SalesRecordSerializer(serializers.ModelSerializer) :
    class Meta :
        model =  SalesRecord
        fields= "__all__"

class SalesFileSerializer(serializers.ModelSerializer) :
    records = SalesRecordSerializer(many=True , read_only = True)
    class Meta : 
        model = SalesFile
        fields= "__all__"
        
class SalesFileListSerializer(serializers.ModelSerializer) :
    records = SalesRecordSerializer(many=True , read_only = True)
    class Meta : 
        model = SalesFile
        fields= "__all__"

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    files = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['username', 'email', 'first_name', 'last_name', 'image', 'files']

    def get_files(self, obj):
        user = obj.user
        sales_files = SalesFile.objects.filter(user=user)
        return SalesFileSerializer(sales_files, many=True).data