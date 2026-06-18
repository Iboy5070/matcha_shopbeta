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
    question_lo = models.CharField("ຄຳຖາມ (ລາວ)", max_length=255, blank=True)
    answer_lo = models.TextField("ຄຳຕອບ (ລາວ)", blank=True)
    question_th = models.CharField("ຄຳຖາມ (ไทย)", max_length=255)
    question_en = models.CharField("Question (EN)", max_length=255, blank=True)
    answer_th = models.TextField("ຄຳຕອບ (ไทย)")
    answer_en = models.TextField("Answer (EN)", blank=True)
    sort_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "FAQ item"

    def __str__(self):
        return self.question_lo or self.question_th

    def question_for(self, lang):
        if lang == "en" and self.question_en:
            return self.question_en
        if lang == "th":
            return self.question_th
        if lang == "lo" and self.question_lo:
            return self.question_lo
        return self.question_lo or self.question_th or self.question_en

    def answer_for(self, lang):
        if lang == "en" and self.answer_en:
            return self.answer_en
        if lang == "th":
            return self.answer_th
        if lang == "lo" and self.answer_lo:
            return self.answer_lo
        return self.answer_lo or self.answer_th or self.answer_en


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
