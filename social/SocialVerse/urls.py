from django.urls import path
from django.conf import settings

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("create_post", views.create_post, name="create_post"),
    path("liked_posts", views.liked_posts, name="liked_posts"),
    path("<int:post_id>/comment", views.comment, name="comment"),
    path("<int:post_id>/like", views.like, name="like"),
    path("<int:post_id>/unlike", views.unlike, name="unlike"),
    path("created", views.created, name="created"),
    path("<int:listing_id>/delete", views.delete_post, name="delete"),
    path("my_profile", views.my_profile, name="my_profile"),
    path("user_profile/<str:username>", views.user_profile, name="user_profile"),
    path("search_results/<str:query>", views.search_results, name="search_results"),
    path('follow/<str:username>', views.follow, name='follow'),
    path('unfollow/<str:username>', views.unfollow, name='unfollow')
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)