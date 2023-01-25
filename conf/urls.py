from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from library import views as library_views
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token

from . import settings

router = routers.DefaultRouter()
router.register(r"author", library_views.AuthorView, "author")
router.register(r"publisher", library_views.PublisherView, "publisher")
router.register(r"book", library_views.BookView, "book")
router.register(r"category", library_views.CategoryView, "category")
router.register(r"user", library_views.UserView, "user")
router.register(r"favorite", library_views.FavoriteView, "favorite")

urlpatterns = (
    [
        path("admin/", admin.site.urls),
        path("api/", include(router.urls)),
        path("register/", library_views.RegisterView.as_view({"post": "create"})),
        path("login/", obtain_jwt_token),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)
