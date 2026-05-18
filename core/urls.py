from django.urls import path
from .views import *

urlpatterns = [
        path('', index, name='home',),
        path('posts/', all_posts, name='all_posts',),
        path("posts/<int:post_id>", post_details, name="post_details"),
        path('create_posts/',post_creation , name='create_posts',),
       
        path("posts/<int:post_id>/delete/", delete_post, name="delete_post"),
        path("posts/<int:post_id>/edit/", edit_post, name="edit_post"),

     
     
       
       
        

    ]
    
