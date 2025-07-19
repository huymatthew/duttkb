from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .generator import generator
import json
import io
import os

@csrf_exempt
@require_http_methods(["GET", "POST"])
def tkb_download(request):
    try:
        # Get data from request
        if request.method == 'GET':
            data = request.GET.get('data', None)
        else:  # POST
            if request.content_type == 'application/json':
                try:
                    body = json.loads(request.body.decode('utf-8'))
                    data = body.get('data', None)
                except json.JSONDecodeError:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Invalid JSON in request body'
                    }, status=400)
            else:
                data = request.POST.get('data', None)
        
        if not data:
            return JsonResponse({
                'status': 'error',
                'message': 'No data provided'
            }, status=400)
        
        # Parse JSON data if it's a string
        if isinstance(data, str):
            try:
                json_data = json.loads(data)
            except json.JSONDecodeError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid JSON data'
                }, status=400)
        else:
            json_data = data
        
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
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error generating image: {str(e)}'
        }, status=500)