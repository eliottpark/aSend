from django.urls import path
from .views import EntryListView, CategoryDetailView, EntryCreateView, CategoryCreateView, EntryDetailView
from . import views
from django.urls import path, include

from django.conf import settings
from django.shortcuts import render, redirect
 
from django.conf.urls.static import static


urlpatterns = [
    path('', EntryListView.as_view(), name='homepage'),
    path('category/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('entry/new/', EntryCreateView.as_view(), name='entry-create'),
    path('category/new/', CategoryCreateView.as_view(), name='category-create'),
    path('entry/<int:pk>/', EntryDetailView.as_view(), name='entry-detail'),
    path('updateRank/<cat_id>/', views.updater, name='update')
]

#app/model_viewtype.html