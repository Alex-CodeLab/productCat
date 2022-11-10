from django.db import models
from django_mysql.models import DynamicField, Model

class Product(Model):
    name = models.CharField(max_length=30)
    attrs = DynamicField(spec={
            "size": str,
        })
    brandname = models.CharField(max_length=30)



