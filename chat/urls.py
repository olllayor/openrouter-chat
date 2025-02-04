from django.urls import path
from . import views
from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def check_auth(request):
    if request.user.is_authenticated:
        return JsonResponse({"authenticated": True})
    return JsonResponse({"authenticated": False}, status=401)


urlpatterns = [
    path('', views.index, name='index'),
    path('api/ask_chat/', views.ask_chat, name='ask_chat'),
    path('api/models/', views.get_models, name='get_models'),
    path('api/auth/check/', check_auth, name='auth_check'),

]
