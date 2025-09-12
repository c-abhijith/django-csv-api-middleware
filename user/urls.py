from .views import UserViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'upload-csv', UserViewSet, basename='user')
urlpatterns = router.urls