from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm

User = get_user_model()


class CustomerSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].label = "ລະຫັດຜ່ານໃໝ່"
        self.fields["new_password2"].label = "ຢືນຢັນລະຫັດຜ່ານໃໝ່"
        self.fields["new_password1"].help_text = "ຢ່າງໜ້ອຍ 8 ຕົວ · ຢ່າໃຊ້ລະຫັດງ່າຍເກີນໄປ"
        self.fields["new_password2"].help_text = ""
        for name in ("new_password1", "new_password2"):
            self.fields[name].widget.attrs.update({
                "class": "form-control form-control-lg",
                "placeholder": "ລະຫັດຜ່ານໃໝ່" if name.endswith("1") else "ພິມອີກຄັ້ງ",
            })


class CustomerRegistrationForm(forms.Form):
    full_name = forms.CharField(
        label="ຊື່ ແລະ ນາມສະກຸນ",
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control form-control-lg", "placeholder": "ຊື່ ນາມສະກຸນ"}),
    )
    email = forms.EmailField(
        label="ອີເມວ",
        widget=forms.EmailInput(attrs={"class": "form-control form-control-lg", "placeholder": "you@example.com"}),
    )
    phone = forms.CharField(
        label="ເບີໂທ",
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-control form-control-lg", "placeholder": "20xxxxxxxx"}),
    )
    address = forms.CharField(
        label="ທີ່ຢູ່",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control form-control-lg", "placeholder": "ບ້ານ / ເມືອງ / ແຂວງ"}),
    )
    password1 = forms.CharField(
        label="ລະຫັດຜ່ານ",
        widget=forms.PasswordInput(attrs={"class": "form-control form-control-lg", "placeholder": "ຢ່າງໜ້ອຍ 8 ຕົວ"}),
    )
    password2 = forms.CharField(
        label="ຢືນຢັນລະຫັດຜ່ານ",
        widget=forms.PasswordInput(attrs={"class": "form-control form-control-lg", "placeholder": "ພິມລະຫັດຜ່ານອີກຄັ້ງ"}),
    )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(username=email).exists() or User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("ອີເມວນີ້ຖືກໃຊ້ແລ້ວ")
        return email

    def clean_password1(self):
        pw = self.cleaned_data["password1"]
        if len(pw) < 8:
            raise forms.ValidationError("ລະຫັດຜ່ານຕ້ອງຍາວຢ່າງໜ້ອຍ 8 ຕົວ")
        return pw

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "ລະຫັດຜ່ານບໍ່ຕົງກັນ")
        return cleaned


class CustomerProfileEditForm(forms.Form):
    full_name = forms.CharField(
        label="ຊື່ ແລະ ນາມສະກຸນ",
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control form-control-lg"}),
    )
    email = forms.EmailField(
        label="ອີເມວ",
        widget=forms.EmailInput(attrs={"class": "form-control form-control-lg"}),
    )
    phone = forms.CharField(
        label="ເບີໂທ",
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-control form-control-lg"}),
    )
    address = forms.CharField(
        label="ທີ່ຢູ່",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    )
    current_password = forms.CharField(
        label="ລະຫັດຜ່ານປັດຈຸບັນ",
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control form-control-lg", "placeholder": "ໃສ່ຖ້າຢາກປ່ຽນລະຫັດຜ່ານ"}),
    )
    password1 = forms.CharField(
        label="ລະຫັດຜ່ານໃໝ່",
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control form-control-lg", "placeholder": "ປ່ອຍວ່າງ = ບໍ່ປ່ຽນ"}),
    )
    password2 = forms.CharField(
        label="ຢືນຢັນລະຫັດຜ່ານໃໝ່",
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-control form-control-lg"}),
    )

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        qs = User.objects.filter(email__iexact=email)
        if self.user:
            qs = qs.exclude(pk=self.user.pk)
        if qs.exists():
            raise forms.ValidationError("ອີເມວນີ້ຖືກໃຊ້ແລ້ວ")
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        current = cleaned.get("current_password")
        if p1 or p2:
            if len(p1 or "") < 8:
                self.add_error("password1", "ລະຫັດຜ່ານຕ້ອງຍາວຢ່າງໜ້ອຍ 8 ຕົວ")
            if p1 != p2:
                self.add_error("password2", "ລະຫັດຜ່ານບໍ່ຕົງກັນ")
            if self.user and not self.user.check_password(current or ""):
                self.add_error("current_password", "ລະຫັດຜ່ານປັດຈຸບັນບໍ່ຖືກຕ້ອງ")
        return cleaned
