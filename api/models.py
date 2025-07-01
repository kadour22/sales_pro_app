from django.db import models
from django.contrib.auth.models import User


class SalesFile(models.Model) :
    user = models.ForeignKey(User , on_delete=models.CASCADE , related_name="sales_files")
    file_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)


    def __str__(self) :
        return self.file_name
    
class SalesRecord(models.Model) :
    sales_file = models.ForeignKey(SalesFile , on_delete=models.CASCADE , related_name="records")
    date    = models.DateField()
    product = models.CharField(max_length=255)
    revenue = models.DecimalField(max_digits=10, decimal_places=2)
    region  = models.CharField(max_length=100)

    
    def __str__(self):
        return f'{self.product} - {self.revenue} DT'

class Profile(models.Model) :
    user  = models.OneToOneField(User , on_delete=models.CASCADE)
    image = models.ImageField(upload_to="profile" , null=True)
    
    def __str__(self) :
        return f"{self.user}"