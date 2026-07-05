from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "display_name", "email", "staff_badge", "active_badge")
    list_filter = ("is_staff", "is_active")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)
    list_per_page = 25

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("ຂໍ້ມູນພະນັກງານ"),
            {
                "fields": ("first_name", "last_name", "email"),
                "description": _("ຊື່ຈະສະແດງໃນ Staff portal ແລະ POS."),
            },
        ),
        (
            _("ສິດການເຂົ້າ"),
            {
                "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
                "description": _(
                    "✓ Staff status = ເຂົ້າ /staff/ ໄດ້ (ອໍເດີ, ສลິບ, ສິນຄ້າ, POS). "
                    "Superuser = ເຂົ້າ Admin ເຕັມ. ພະນັກກະເກັດປົກກະຕິໃຊ້ແຕ່ Staff status."
                ),
            },
        ),
        (_("ວັນທີ"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2"),
                "description": _(
                    "ສ້າງບັນຊີພະນັກງານ: ຕິກ Staff status ໃນຂັ້ນຕອນຖັດໄປ "
                    "(ຫຼືໃຊ້ຄຳສັ່ງ create_staff)."
                ),
            },
        ),
        (
            _("ຂໍ້ມູນ"),
            {"fields": ("first_name", "last_name", "email", "is_staff", "is_active")},
        ),
    )

    @admin.display(description=_("ຊື່"))
    def display_name(self, obj):
        return obj.get_full_name() or "—"

    @admin.display(description=_("Staff"))
    def staff_badge(self, obj):
        if obj.is_superuser:
            return format_html('<span class="pa-badge pa-badge--admin">Admin</span>')
        if obj.is_staff:
            return format_html('<span class="pa-badge pa-badge--staff">Staff</span>')
        return format_html('<span class="pa-badge pa-badge--muted">—</span>')

    @admin.display(description=_("ໃຊ້ງານ"))
    def active_badge(self, obj):
        if obj.is_active:
            return format_html('<span class="pa-badge pa-badge--ok">✓</span>')
        return format_html('<span class="pa-badge pa-badge--no">✗</span>')

    @admin.action(description=_("ເປີດ Staff status (ເຂົ້າ /staff/)"))
    def make_staff(self, request, queryset):
        updated = queryset.update(is_staff=True, is_active=True)
        self.message_user(request, _("ອັບເດດ %(n)s ບັນຊີ") % {"n": updated})

    @admin.action(description=_("ປິດ Staff status"))
    def remove_staff(self, request, queryset):
        updated = queryset.exclude(is_superuser=True).update(is_staff=False)
        self.message_user(request, _("ອັບເດດ %(n)s ບັນຊີ") % {"n": updated})

    actions = ["make_staff", "remove_staff"]
