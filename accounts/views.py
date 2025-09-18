from django.shortcuts import render
from django.contrib.auth import login as auth_login, authenticate
from .forms import CustomUserCreationForm, CustomErrorList
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

from .forms import SecurityQAForm, ForgotUsernameForm, SecurityAnswerResetForm
from .models import SecurityQA
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
@login_required
def logout_view(request):
    logout(request)
    return redirect('home.index')
def login(request):
    template_data = {}
    template_data['title'] = 'Login'
    if request.method == 'GET':
        return render(request, 'accounts/login.html',
            {'template_data': template_data})
    elif request.method == 'POST':
        user = authenticate(
            request,
            username = request.POST['username'],
            password = request.POST['password']
        )
        if user is None:
            template_data['error'] = 'The username or password is incorrect.'
            return render(request, 'accounts/login.html',
                {'template_data': template_data})
        else:
            auth_login(request, user)
            return redirect('home.index')
def signup(request):
    template_data = {}
    template_data['title'] = 'Sign Up'
    if request.method == 'GET':
        template_data['form'] = CustomUserCreationForm()
        return render(request, 'accounts/signup.html',
            {'template_data': template_data})
    elif request.method == 'POST':
        form = CustomUserCreationForm(request.POST, error_class=CustomErrorList)
        if form.is_valid():
            form.save()
            return redirect('accounts.login')
        else:
            template_data['form'] = form
            return render(request, 'accounts/signup.html',
                {'template_data': template_data})

@login_required
def orders(request):
    template_data = {}
    template_data['title'] = 'Orders'
    template_data['orders'] = request.user.order_set.all()
    return render(request, 'accounts/orders.html',
        {'template_data': template_data})

@login_required
def security_settings(request):
    template_data = {'title': 'Security Settings'}
    if request.method == 'POST':
        form = SecurityQAForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your security phrase was saved.")
            return redirect('accounts.security')
    else:
        form = SecurityQAForm(user=request.user)
    template_data['form'] = form
    return render(request, 'accounts/security_settings.html', {'template_data': template_data})


def forgot_password_username(request):
    # Step 1: enter username
    template_data = {'title': 'Forgot Password'}
    if request.method == 'POST':
        form = ForgotUsernameForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                user = User.objects.get(username=username)
                # Ensure they have a SecurityQA set
                user.security_qa
            except (User.DoesNotExist, SecurityQA.DoesNotExist):
                messages.error(request, "Account not found or no security phrase set.")
                return render(request, 'accounts/forgot_username.html', {'template_data': template_data, 'form': form})
            # Store user id in session for next step
            request.session['pw_reset_user_id'] = user.id
            return redirect('accounts.forgot_answer')
    else:
        form = ForgotUsernameForm()
    template_data['form'] = form
    return render(request, 'accounts/forgot_username.html', {'template_data': template_data})


def forgot_password_answer(request):
    # Step 2: show question; verify answer; set new password
    user_id = request.session.get('pw_reset_user_id')
    if not user_id:
        return redirect('accounts.forgot_username')

    user = get_object_or_404(User, id=user_id)
    try:
        qa = user.security_qa
    except SecurityQA.DoesNotExist:
        messages.error(request, "No security phrase set for this account.")
        return redirect('accounts.forgot_username')

    template_data = {'title': 'Verify Security Phrase', 'question': qa.question}

    if request.method == 'POST':
        form = SecurityAnswerResetForm(request.POST)
        if form.is_valid():
            if not qa.check_answer(form.cleaned_data['answer']):
                messages.error(request, "Incorrect answer.")
                return render(request, 'accounts/forgot_answer.html', {'template_data': template_data, 'form': form})
            # Reset password
            user.set_password(form.cleaned_data['new_password1'])
            user.save()
            # Clear the session marker
            request.session.pop('pw_reset_user_id', None)
            messages.success(request, "Password reset successful. Please log in.")
            return redirect('accounts.login')
    else:
        form = SecurityAnswerResetForm()

    return render(request, 'accounts/forgot_answer.html', {'template_data': template_data, 'form': form})