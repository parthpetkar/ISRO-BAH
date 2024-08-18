from django.contrib import admin
from django.urls import path, include
from chat.views import save_chat_to_cache, save_cache_to_db, fetch_chat_from_db, list_chats, save_chat

"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/

Examples:
    Function views:
        1. Add an import:  from my_app import views
        2. Add a URL to urlpatterns:  path('', views.home, name='home')
    Class-based views:
        1. Add an import:  from other_app.views import Home
        2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
    Including another URLconf:
        1. Import the include() function: from django.urls import include, path
        2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))

"""

urlpatterns = [
    path('admin/', admin.site.urls),
    # List all chats
    path('list_chats/', list_chats, name='list_chats'),
    # Save a chat to the cache
    path('save_chat/', save_chat, name='save_chat'),
    # Save a chat to the cache and then to the database
    path('save_chat_to_cache/', save_chat_to_cache, name='save_chat_to_cache'),
    # Save a chat from the cache to the database
    path('save_cache_to_db/', save_cache_to_db, name='save_cache_to_db'),
    # Fetch a chat from the database by its ID
    path('fetch_chat_from_db/<int:chat_id>/', fetch_chat_from_db, name='fetch_chat_from_db'),
]