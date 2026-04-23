from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from projects.models import Project
from .models import TestExecution
from .serializers import TestExecutionSerializer
from .services import run_execution


class ExecutionAllureAssetView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, pk, asset_path='index.html'):
        execution = TestExecution.objects.get(pk=pk)
        allure_html_path = execution.summary.get('allure_html_path', '') if execution.summary else ''
        if not allure_html_path:
            raise Http404('Allure report not available')
        report_root = (Path(settings.BASE_DIR) / allure_html_path).parent
        target = report_root / asset_path
        if not target.exists() or not target.is_file():
            raise Http404('Allure asset not found')
        return FileResponse(open(target, 'rb'))


class TestExecutionViewSet(viewsets.ModelViewSet):
    queryset = TestExecution.objects.select_related('project').all()
    serializer_class = TestExecutionSerializer

    @action(detail=True, methods=['get'], url_path='html')
    def html_report(self, request, pk=None):
        execution = self.get_object()
        if not execution.report_path:
            raise Http404('Report file not found')
        report_path = Path(settings.BASE_DIR) / execution.report_path
        if not report_path.exists():
            raise Http404('Report file not found')
        return HttpResponse(report_path.read_text(encoding='utf-8', errors='ignore'), content_type='text/html')

    @action(detail=True, methods=['get'], url_path='allure')
    def allure_report(self, request, pk=None):
        execution = self.get_object()
        allure_html_path = execution.summary.get('allure_html_path', '') if execution.summary else ''
        if not allure_html_path:
            note = execution.summary.get('allure_note', 'Allure report not available') if execution.summary else 'Allure report not available'
            return Response({'detail': note}, status=status.HTTP_404_NOT_FOUND)
        report_path = Path(settings.BASE_DIR) / allure_html_path
        if not report_path.exists():
            raise Http404('Allure report file not found')
        return HttpResponse(report_path.read_text(encoding='utf-8', errors='ignore'), content_type='text/html')

    @action(detail=False, methods=['post'], url_path='run')
    def run_execution(self, request):
        project_id = request.data.get('project')
        trigger_user = request.data.get('trigger_user', 'web-user')
        if not project_id:
            return Response({'detail': 'project is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return Response({'detail': 'project not found'}, status=status.HTTP_404_NOT_FOUND)

        execution = TestExecution.objects.create(
            project=project,
            trigger_user=trigger_user,
            status='PENDING',
            summary={},
        )
        execution = run_execution(execution)
        return Response(TestExecutionSerializer(execution).data, status=status.HTTP_201_CREATED)
