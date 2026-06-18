from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()


class CustomerRegistrationForm(forms.Form):
    full_name = forms.CharField(
        max_length=120,
        label="ຊື່-ນາມສກຸນ",
        widget=forms.TextInput(attrs={"class": "form-control form-control-lg", "placeholder": "ຊື່ເຕັມ"}),
    )
    email = forms.EmailField(
        label="ອີເມວ",
        widget=forms.EmailInput(attrs={"class": "form-control form-control-lg", "placeholder": "you@email.com"}),
    )
    phone = forms.CharField(
        max_length=30,
        label="ເບີໂທ",
        widget=forms.TextInput(attrs={"class": "form-control form-control-lg", "placeholder": "020 XXXXXXXX"}),
    )
    address = forms.CharField(
        required=False,
        label="ທີ່ຢູ່",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "ທີ່ຢູ່ຈັດສົ່ງ (ບໍ່ບັງຄັບ)"}),
    )
    password1 = forms.CharField(
        label="ລະຫັດຜ່ານ",
        widget=forms.PasswordInput(attrs={"class": "form-control form-control-lg"}),
    )
    password2 = forms.CharField(
        label="ຢືນຢັນລະຫັດຜ່ານ",
        widget=forms.PasswordInput(attrs={"class": "form-control form-control-lg"}),
    )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(username=email).exists():
            raise ValidationError("ອີເມວນີ້ຖືກໃຊ້ແລ້ວ — ລອງເຂົ້າສູ່ລະບົບ")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("ລະຫັດຜ່ານບໍ່ກົງກັນ")
        if password1:
            validate_password(password1)
        return password2


class CustomerLoginForm(forms.Form):
    email = forms.EmailField(
        label="ອີເມວ",
        widget=forms.EmailInput(attrs={"class": "form-control form-control-lg", "placeholder": "you@email.com"}),
    )
    password = forms.CharField(
        label="ລະຫັດຜ່ານ",
        widget=forms.PasswordInput(attrs={"class": "form-control form-control-lg"}),
    )
