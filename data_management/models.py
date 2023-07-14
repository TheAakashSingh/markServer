from django.db import models

from user_management.models import UserProfile


# Create your models here.
class DataTable(models.Model):
    class Meta:
            db_table = 'data_table'
            verbose_name_plural = 'Data Table'
    row_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    address = models.CharField(max_length=255, null=True)
    mobile_no = models.BigIntegerField(null=True)
    email_id = models.EmailField(null=True)
    city = models.CharField(max_length=255, null=True)
    pincode = models.BigIntegerField(null=True)
    order_item = models.CharField(max_length=255, null=True)
    order_restaurant = models.CharField(max_length=255, null=True)
    created_by = models.CharField(max_length=255, null=True)
    updated_by = models.CharField(max_length=255, null=True)
    created_date = models.DateTimeField(null=True)
    updated_date = models.DateTimeField(null=True)
    date_of_birth = models.DateField(null=True)
    def __str__(self):
        return self.email_id