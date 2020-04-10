from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^register_face/$', views.UserCardView.as_view()),  # 识别人像
    url(r'^get_list/$', views.GetPersonList.as_view()),  # 获取考勤记录
]