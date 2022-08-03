from django.urls import path
from . import views
from .feeds import LatestPostsFeed

# App name for current application

app_name = 'blog'

# url patterns for blogs

urlpatterns = [
    # Post views
    path('', views.post_list, name='post_list'),
    path('search/', views.post_search, name='post_search'),
    # path('', views.PostListView.as_view(), name='post_list'),
    path('<int:post_id>/share/', views.post_share, name='post_share'),
    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name='post_detail'),
    # Path for feeds / RSS readers
    path('feed/', LatestPostsFeed(), name='post_feed'),
]
