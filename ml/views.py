# ml/views.py
import tempfile
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from .utils import predict_banana_ripeness

class PredictRipenessView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request):
        img = request.data.get('image')
        wp  = request.data.get('weights_path')
        mp  = request.data.get('mapping_path')
        if not img or not wp or not mp:
            return Response({'error':'image, weights_path, mapping_path required'}, status=status.HTTP_400_BAD_REQUEST)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        for chunk in img.chunks(): tmp.write(chunk)
        tmp.flush()
        output, b64 = predict_banana_ripeness(tmp.name, wp, mp)
        return Response({'predictions': output, 'image_base64': b64})