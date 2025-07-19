from django.urls import path
from . import views
from django.http import JsonResponse

def api_info(request):
    return JsonResponse({
        'message': 'DUTTKB API',
        'available_endpoints': {
            'tkb_download': '/api/tkb_download/ (POST)'
        },
        'usage': {
            'method': 'POST',
            'content_type': 'application/json',
            'body': {
                'data': 'JSON array of course data'
            }
        }
    })

urlpatterns = [
    path('', api_info, name='api_info'),
    path('tkb_download/', views.tkb_download, name='tkb_download'),
]