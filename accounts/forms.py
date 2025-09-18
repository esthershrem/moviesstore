# accounts/forms.py
from django.contrib.auth.forms import UserCreationForm
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe
from django import forms
from django.contrib.auth.models import User
from .models import SecurityQA


class CustomErrorList(ErrorList):
    def __str__(self):
        if not self:
            return ''
        return mark_safe(''.join([
            f'<div class="alert alert-danger" role="alert">{e}</div>'
            for e in self
        ]))


class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        # IMPORTANT: keep this on one line
        super().__init__(*args, **kwargs)
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update({'class': 'form-control'})

class SecurityQAForm(forms.Form):
    question = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'class': 'form-control'}))
    answer = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        # Pre-fill question if it exists
        try:
            qa = self.user.security_qa
            self.fields['question'].initial = qa.question
        except SecurityQA.DoesNotExist:
            pass

    def save(self):
        question = self.cleaned_data['question']
        answer = self.cleaned_data['answer']
        qa, _created = SecurityQA.objects.get_or_create(user=self.user)
        qa.question = question
        qa.set_answer(answer)  # hashes
        qa.save()
        return qa


class ForgotUsernameForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))


class SecurityAnswerResetForm(forms.Form):
    # Shown after username step
    answer = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password1 = forms.CharField(label="New password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(label="Confirm new password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        data = super().clean()
        p1 = data.get('new_password1')
        p2 = data.get('new_password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return data