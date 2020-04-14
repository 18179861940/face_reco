from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^register_face/$', views.UserCardView.as_view()),  # 识别人像
    url(r'^get_list/$', views.GetPersonList.as_view()),  # 获取考勤记录
    url(r'^modify_card/$', views.UpdateCardList.as_view()),  # 修改考勤记录
    url(r'^delete_card/$', views.DeleteCardRecord.as_view()),  # 删除考勤记录
]