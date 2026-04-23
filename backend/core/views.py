from rest_framework.response import Response
from rest_framework.views import APIView


class MockLoginAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if username == 'demo' and password == 'demo':
            return Response({'code': 200, 'message': 'login success'})
        return Response({'code': 401, 'message': 'invalid credentials'}, status=401)
