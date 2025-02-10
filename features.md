1. Implement caching for chat history:

```python
pythonCopyfrom django.core.cache import cache

def get_chat_history(user_id):
    cache_key = f'chat_history_{user_id}'
    history = cache.get(cache_key)
    if history is None:
        history = Chat.objects.filter(user_id=user_id).order_by('-created_at')
        cache.set(cache_key, history, timeout=300)  # 5 minutes cache
    return history
```


2. Implement asynchronous image processing:

```python
pythonCopyfrom celery import shared_task

@shared_task
def process_image_async(image_id):
    image = MessageImage.objects.get(id=image_id)
    webp_image = convert_image_to_webp(image.image)
    image.image = webp_image
    image.save()
```