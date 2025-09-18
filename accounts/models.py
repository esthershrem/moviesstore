from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password

class SecurityQA(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='security_qa')
    question = models.CharField(max_length=255)
    answer_hash = models.CharField(max_length=128)
    updated_at = models.DateTimeField(auto_now=True)

    def set_answer(self, raw_answer: str):
        self.answer_hash = make_password(raw_answer)

    def check_answer(self, raw_answer: str) -> bool:
        return check_password(raw_answer, self.answer_hash)

    def __str__(self):
        return f"SecurityQA for {self.user.username}"
