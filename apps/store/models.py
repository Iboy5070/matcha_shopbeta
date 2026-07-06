from django.db import models
from django.conf import settings


class Employee(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="employee_profile")
    emp_name = models.CharField(max_length=100)
    emp_last = models.CharField(max_length=100)
    emp_address = models.TextField()
    emp_gender = models.CharField(max_length=10)
    emp_tel = models.CharField(max_length=20)

    class Meta:
        verbose_name = "ພະນັກງານ (Employee)"
        verbose_name_plural = "ພະນັກງານ (Employees)"

    def __str__(self):
        return f"{self.emp_name} {self.emp_last}"


class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="customer_profile", null=True, blank=True)
    cus_name = models.CharField(max_length=100)
    cus_last = models.CharField(max_length=100)
    address = models.TextField()
    gender = models.CharField(max_length=10)
    cus_tel = models.CharField(max_length=20)

    class Meta:
        verbose_name = "ລູກຄ້າ (Customer)"
        verbose_name_plural = "ລູກຄ້າ (Customers)"

    def __str__(self):
        return f"{self.cus_name} {self.cus_last}"
