from django.db import models


class Testimonial(models.Model):
    company_name = models.CharField(max_length=120)
    quote_th = models.TextField()
    quote_en = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.company_name


class FAQItem(models.Model):
    question_th = models.CharField(max_length=255)
    question_en = models.CharField(max_length=255, blank=True)
    answer_th = models.TextField()
    answer_en = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "FAQ item"

    def __str__(self):
        return self.question_th


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.created_at:%Y-%m-%d})"
