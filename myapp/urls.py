from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views  # Adjust this import based on your project structure

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # Add this line to handle the root URL
    path('upload/', views.upload_image, name='upload_image'), 
    path('search/', views.input_word, name='input_word'), 
    path('camera/', views.camera_view, name='camera_view'), 
    path('capture/', views.capture_image, name='capture_image'), # URL for the upload view
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
