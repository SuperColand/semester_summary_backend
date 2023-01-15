from django.urls import path, re_path
from .views import *

urlpatterns = [
    path('all_in_one/', all_in_one),
    path('say/', say),
    # 这是一个样例，指定路由名为url_name，对应处理函数为当前app内views.py中的api_name
]