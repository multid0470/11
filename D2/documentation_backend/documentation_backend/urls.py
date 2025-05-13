#from django.contrib import admin
#from django.urls import path
#from django.conf import settings
#from django.conf.urls.static import static
#from .views import CodeUploadView, get_documentation

#urlpatterns = [
#    path('admin/', admin.site.urls),
#    path('api/upload/', CodeUploadView.as_view()),
#    path('api/documentation/', get_documentation),
#] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import CodeUploadView, get_documentation

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/upload/', CodeUploadView.as_view()),
    path('api/documentation/', get_documentation),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)






