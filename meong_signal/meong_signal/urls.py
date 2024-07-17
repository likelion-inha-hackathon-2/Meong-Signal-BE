from django.contrib import admin
from django.urls import path, include, re_path

from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from django.conf import settings
from django.conf.urls.static import static

# schema_view = get_schema_view(
#     openapi.Info(
#         title="meong-signal",
#         default_version='1.1.1',
#         description="감자탕후루 api 문서",
#         terms_of_service="https://www.google.com/policies/terms/"
#     ),
#     public=True,
#     permission_classes=(AllowAny,),
# )

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),

    # Swagger url
    # re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    # re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]


# urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) -> swagger관련 설정
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)