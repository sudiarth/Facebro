from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'app_facebro'

urlpatterns = [
    path('', views.index, name='index'),
    path('user/<int:user_id>/timeline', views.timeline, name='timeline'),
    path('settings', views.setting, name='setting'),
    path('user/<int:user_id>/post', views.post_create, name='post_create'),
    path('post/<int:post_id>/delete', views.post_delete, name='post_delete'),
    path('user/<int:user_id>/following', views.following, name='following'),
    path('user/<str:email>/follow', views.follow, name='follow'),
    path('user/<str:user_id>/unfollow', views.unfollow, name='unfollow'),
    path('user/<int:user_id>/follower', views.follower, name='follower'),
    path('user/<int:user_id>/photos', views.photo, name='photo'),
    path('photo/create', views.photo_create, name='photo_create'),
    path('photo/<int:photo_id>/delete', views.photo_delete, name='photo_delete'),
    path('search', views.search, name='search'),
    path('results/<str:query>', views.results, name='results'),
    path('comment/<int:post_id>/post', views.comment_post, name='comment_post'),
    path('comment/<int:comment_id>/delete', views.comment_delete, name='comment_delete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)