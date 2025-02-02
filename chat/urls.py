from django.urls import path
from . import views  # Import the views from the current app

urlpatterns = [
    # Route for the homepage which renders your chat interface
    path("", views.index, name="index"),
    # Route to fetch available models (could be used to populate a model selection dropdown)
    path("api/models/", views.get_models, name="get_models"),
    # Route to handle chat requests with streaming responses
    path("api/ask_chat/", views.ask_chat, name="ask_chat"),
]
