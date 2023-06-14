from django.urls import path

from . import views

urlpatterns = [
        path("", views.index, name="index"),
        path("NewPage", views.NewPage, name="NewPage"),
        path("RandomPage", views.RandomPage, name="RandomPage"),
        path("edit/<str:entry>", views.edit, name="edit"),
        path("wiki/<str:entry>", views.entry, name="entry"),

    ]