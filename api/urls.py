from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView , TokenRefreshView

urlpatterns = [
    path('upload/' , views.UploadCSVFile.as_view(), name='upload-csv'),
    path('stats/<int:file_id>/', views.SalesStatsView.as_view(), name='files-chart-view'),
    path('myfiles/' , views.MyUploadedFileList.as_view() , name='files'),
    path('profile/' , views.UserProfileView.as_view() , name='profile-user'),
    path('download-report/pdf/<int:file_id>/' , views.SalesReportPDFView.as_view() , name='download-report'),


    path('token/' , TokenObtainPairView.as_view(), name='token'),
    path('refresh/' , TokenRefreshView.as_view(), name='refresh'),
    path('register/' , views.RegistrationView.as_view(), name='refresh'),
]