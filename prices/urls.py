from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PriceViewSet

router = DefaultRouter()
router.register(r'prices', PriceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]