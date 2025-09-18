from django.urls import path
from . import views
urlpatterns = [
    path('signup', views.signup, name='accounts.signup'),
    path('login/', views.login, name='accounts.login'),
    path('logout/', views.logout_view, name='accounts.logout'),
    path('orders/', views.orders, name='accounts.orders'),
    path('settings/security/', views.security_settings, name='accounts.security'),
    path('forgot/', views.forgot_password_username, name='accounts.forgot_username'),
    path('forgot/answer/', views.forgot_password_answer, name='accounts.forgot_answer'),
]