from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse, Http404
from django.conf import settings
from .generator import generator
import json
import io
import os

@api_view(['GET', 'POST'])
def tkb_download(request):
    try:
        # Get data from request
        if request.method == 'GET':
            data = request.GET.get('data', None)
        else:  # POST
            data = request.data.get('data', None)
        
        if not data:
            return Response({
                'status': 'error',
                'message': 'No data provided'
            }, status=400)
        
        # Parse JSON data if it's a string
        if isinstance(data, str):
            try:
                json_data = json.loads(data)
            except json.JSONDecodeError:
                return Response({
                    'status': 'error',
                    'message': 'Invalid JSON data'
                }, status=400)
        else:
            json_data = data
        
        # Change working directory to assets folder for generator
        current_dir = os.getcwd()
        assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
        
        try:
            os.chdir(assets_dir)
            
            # Generate image using generator function
            image = generator(json_data)
            
            # Convert image to bytes
            img_buffer = io.BytesIO()
            image.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            # Return image as HTTP response
            response = HttpResponse(img_buffer.getvalue(), content_type='image/png')
            response['Content-Disposition'] = 'attachment; filename="tkb_schedule.png"'
            return response
            
        finally:
            # Always restore original directory
            os.chdir(current_dir)
            
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error generating image: {str(e)}'
        }, status=500)