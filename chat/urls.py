# urls.py

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
    path("", views.index, name="index"),
    path("api/auth/check/", check_auth, name="auth_check"),
    path("api/gemini_chat/", views.ask_gemini_chat, name="ask_gemini_chat"),


    # path("api/groq_chat/", views.ask_groq_chat, name="ask_groq_chat"),
    # path("api/models/", views.get_models, name="get_models"),
]
