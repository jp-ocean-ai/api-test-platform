from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter

from apis.views import ApiDefinitionViewSet
from core.views import MockLoginAPIView
from environments.views import EnvironmentViewSet
from executions.views import ExecutionAllureAssetView, TestExecutionViewSet
from projects.views import ProjectViewSet
from reports.views import TestReportViewSet
from testcases.views import TestCaseViewSet

schema_view = get_schema_view(
    openapi.Info(
        title='API Test Platform API',
        default_version='v1',
        description='Backend API for the API Test Platform',
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

router = DefaultRouter()
router.register('projects', ProjectViewSet)
router.register('environments', EnvironmentViewSet)
router.register('apis', ApiDefinitionViewSet)
router.register('testcases', TestCaseViewSet)
router.register('executions', TestExecutionViewSet)
router.register('reports', TestReportViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/mock/login/', MockLoginAPIView.as_view()),
    path('api/executions/<int:pk>/allure/<path:asset_path>', ExecutionAllureAssetView.as_view()),
    path('api/executions/<int:pk>/allure/', ExecutionAllureAssetView.as_view(), {'asset_path': 'index.html'}),
    path('api/', include(router.urls)),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
