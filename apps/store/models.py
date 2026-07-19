from django.db import models
from django.conf import settings


class Employee(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employee_profile",
        verbose_name="Email / Password (auth_user)",
        help_text="ບົດ: Email, Password — Django ເກັບໃນ auth_user (hash)",
    )
    emp_name = models.CharField("Emp_Name", max_length=100)
    emp_last = models.CharField("Emp_Last", max_length=100)
    emp_address = models.TextField("Emp_Address")
    emp_gender = models.CharField("Emp_Gender", max_length=10)
    emp_tel = models.CharField("Emp_Tel", max_length=20)

    class Meta:
        verbose_name = "ພະນັກງານ (Employee)"
        verbose_name_plural = "ພະນັກງານ (Employee)"

    def __str__(self):
        return f"{self.emp_name} {self.emp_last}"


class Customer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_profile",
        null=True,
        blank=True,
        verbose_name="Email / Password (auth_user)",
        help_text="ບົດ: Email, Password — Django ເກັບໃນ auth_user (hash)",
    )
    cus_name = models.CharField("Cus_Name", max_length=100)
    cus_last = models.CharField("Cus_Last", max_length=100)
    address = models.TextField("Address")
    gender = models.CharField("Gender", max_length=10)
    cus_tel = models.CharField("Cus_Tel", max_length=20)

    class Meta:
        verbose_name = "ລູກຄ້າ (Customer)"
        verbose_name_plural = "ລູກຄ້າ (Customer)"

    def __str__(self):
        return f"{self.cus_name} {self.cus_last}"
