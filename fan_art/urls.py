from django.urls import path

from . import views

urlpatterns = [
    path('', views.fan_art_gallery, name='fan_art_gallery'),
    path('user_gallery', views.user_gallery, name='user_gallery'),
    path('add_art', views.add_art, name='add_art'),
    path('edit_art/<art_id>', views.edit_art, name='edit_art'),
    path('delete_art/<art_id>', views.delete_art, name='delete_art'),
]