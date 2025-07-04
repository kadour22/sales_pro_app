import csv
import io

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status , permissions , generics

from .models import SalesFile , SalesRecord , Profile
from .serializers import (
     RegistrationSerializer , SalesRecordSerializer ,
     SalesFileSerializer , SalesFileListSerializer ,
     ProfileSerializer
)
from django.template.loader import render_to_string
from weasyprint import HTML
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.urls import reverse
from django.conf import settings
from django.db.models.functions import TruncWeek , TruncDay ,TruncYear ,TruncMonth
from django.http import HttpResponse


class RegistrationView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User created successfully", "user_id": user.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UploadCSVFile(APIView) :
    permission_classes = [permissions.IsAuthenticated]
    def post(self , request) :
        csv_file = request.FILES.get('file')
        user     = self.request.user
        if not csv_file :
            return Response(
                {
                    'error' : 'No File Provided'
                }, status = status.HTTP_400_BAD_REQUEST
            )
        sales_file = SalesFile.objects.create(
            user=user,
            file_name=csv_file.name
        )

        decoded_file = csv_file.read().decode('utf-8')
        io_string    = io.StringIO(decoded_file)
        reader       = csv.DictReader(io_string)
        print(reader)
        for row in reader:
            try:
                SalesRecord.objects.create(
                    sales_file=sales_file,
                    date    = row['Date'],
                    product = row['Product'],
                    revenue = row['Revenue'],
                    region  = row['Region']
                )
            except Exception as e:
                print('خطأ في السطر:', row, e)

        return Response({'message': 'File uploaded successfully!'}, status=status.HTTP_201_CREATED)

class MyUploadedFileList(APIView) :
    def get(self , request) :
        user = self.request.user
        print(user)
        sales_files = SalesFile.objects.filter(user=user)
        serializer = SalesFileListSerializer(sales_files , many = True)

        for file in serializer.data :
            file_id = file["id"]
            file['dashboard_url'] = request.build_absolute_uri(
                reverse('files-chart-view' , args=[file_id])
            )

        return Response(serializer.data)
    
class SalesStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, file_id):
        sales_file = SalesFile.objects.get(id=file_id)
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        print("Start:", start_date, "End:", end_date)
        records = SalesRecord.objects.filter(sales_file=sales_file)
        # Open-ended date filtering
        if start_date:
            records = records.filter(date__gte=start_date)
        if end_date:
            records = records.filter(date__lte=end_date)
            print("Filtered records count:", records.count())
        try:
            records = records.select_related('sales_file')
            total_revenue = records.aggregate(Sum('revenue'))['revenue__sum'] or 0
            top_product = records.values('product') \
                .annotate(total=Sum('revenue')) \
                .order_by('-total') \
                .first()

            revenue_by_region = records.values('region') \
                .annotate(total=Sum('revenue')) \
                .order_by('-total')

            revenue_by_month = records.annotate(month=models.functions.TruncMonth('date')) \
                .values('month') \
                .annotate(total=Sum('revenue')) \
                .order_by('month')

            revenue_by_week = records.annotate(week=TruncWeek('date'))\
            .values('week')\
            .annotate(total=Sum('revenue'))

            revenue_by_day = records.annotate(day=TruncDay('date'))\
            .values('day')\
            .annotate(total=Sum('revenue'))

            revenue_by_year = records.annotate(year=TruncYear('date'))\
            .values('year')\
            .annotate(total=Sum('revenue'))

            return Response({
                'total_revenue'    : total_revenue,
                'top_product'      : top_product,
                'revenue_by_region': revenue_by_region,
                'revenue_by_month': revenue_by_month,
                'revenue_by_week':revenue_by_week,
                'revenue_by_day':revenue_by_day,
                'revenue_by_year': revenue_by_year
            })
        except Exception as e:
            print("Error in SalesStatsView:", e)
            return Response(
                {"Error Message": "Failed To Analyse Data"}, status=status.HTTP_204_NO_CONTENT
            )

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = Profile.objects.filter(user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

class DownloadReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, file_id):
        sales_file = SalesFile.objects.get(id=file_id)
        records = SalesRecord.objects.filter(sales_file=sales_file)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=\"report_{file_id}.csv\"'
        writer = csv.writer(response)
        writer.writerow(['Date', 'Product', 'Revenue', 'Region'])
        for record in records:
            writer.writerow([record.date, record.product, record.revenue, record.region])
        return response
    


class SalesReportPDFView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, file_id):
        sales_file = SalesFile.objects.get(id=file_id)
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        records = SalesRecord.objects.filter(sales_file=sales_file)
        if start_date:
            records = records.filter(date__gte=start_date)
        if end_date:
            records = records.filter(date__lte=end_date)

        total_revenue = records.aggregate(Sum('revenue'))['revenue__sum'] or 0
        top_product = records.values('product') \
            .annotate(total=Sum('revenue')) \
            .order_by('-total') \
            .first()
        revenue_by_region = records.values('region').annotate(total=Sum('revenue'))
        revenue_by_month  = records.annotate(month=TruncMonth('date')).values('month').annotate(total=Sum('revenue'))
        revenue_by_week   = records.annotate(week=TruncWeek('date')).values('week').annotate(total=Sum('revenue'))
        revenue_by_day    = records.annotate(day=TruncDay('date')).values('day').annotate(total=Sum('revenue'))
        revenue_by_year   = records.annotate(year=TruncYear('date')).values('year').annotate(total=Sum('revenue'))

        html_string = render_to_string("sales_report.html", {
            'total_revenue'    : total_revenue,
            'top_product'      : top_product,
            'revenue_by_region': revenue_by_region,
            'revenue_by_month' : revenue_by_month,
            'revenue_by_week'  : revenue_by_week,
            'revenue_by_day'   : revenue_by_day,
            'revenue_by_year'  : revenue_by_year,
        })

        html     = HTML(string=html_string)
        pdf_file = html.write_pdf()

        response = HttpResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = f"attachment; filename='sales_report_{file_id}.pdf'"
        return response
