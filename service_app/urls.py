from django.urls import path
from . import views

urlpatterns = [
    path("", views.login_page, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("start/", views.start_page, name="start"),
    path("home/", views.home_page, name="home"),
    path("about/", views.about_page, name="about"),
    path("contact/", views.contact_page, name="contact"),
    path("register/", views.register_page, name="register"),
    path("service/", views.service_page, name="service"),
    path("messages/", views.message_page, name="message"),
    path("analysis/", views.analysis_page, name="analysis"),
    path("history/", views.history_page, name="history"),
    path("admin-page/", views.admin_page, name="admin_page"),
]