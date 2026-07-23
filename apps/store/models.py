from django.db import models
from django.conf import settings


class Employee(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employee_profile",
        verbose_name="ບັນຊີເຂົ້າລະບົບ",
        help_text="ເຊື່ອມກັບ User (ອີເມວ/ຊື່ຜູ້ໃຊ້ + ລະຫັດ) — ສຳລັບ login ພະນັກງານ",
    )
    emp_name = models.CharField("ຊື່", max_length=100)
    emp_last = models.CharField("ນາມສະກຸນ", max_length=100)
    emp_address = models.TextField("ທີ່ຢູ່")
    emp_gender = models.CharField("ເພດ", max_length=10, help_text="ຕົວຢ່າງ: ຊາຍ / ຍິງ")
    emp_tel = models.CharField("ເບີໂທ", max_length=20, help_text="ເບີຕິດຕໍ່ພະນັກງານ")

    class Meta:
        verbose_name = "ພະນັກງານ"
        verbose_name_plural = "ພະນັກງານ"

    def __str__(self):
        return f"{self.emp_name} {self.emp_last}"


class Customer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_profile",
        null=True,
        blank=True,
        verbose_name="ບັນຊີເຂົ້າລະບົບ",
        help_text="ຖ້າລູກຄ້າລົງທະບຽນເວັບ — ເຊື່ອມກັບ User. ລູກຄ້າ POS ອາດປ່ອຍວ່າງໄດ້",
    )
    cus_name = models.CharField("ຊື່", max_length=100)
    cus_last = models.CharField("ນາມສະກຸນ", max_length=100)
    address = models.TextField("ທີ່ຢູ່ / ທີ່ຈັດສົ່ງ", help_text="ໃຊ້ສຳລັບສົ່ງສິນຄ້າ")
    gender = models.CharField("ເພດ", max_length=10, blank=True)
    cus_tel = models.CharField("ເບີໂທ", max_length=20, help_text="ເບີຕິດຕໍ່ລູກຄ້າ (ສຳຄັນ)")

    class Meta:
        verbose_name = "ລູກຄ້າ"
        verbose_name_plural = "ລູກຄ້າ"

    def __str__(self):
        return f"{self.cus_name} {self.cus_last}"
