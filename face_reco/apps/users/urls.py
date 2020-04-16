from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^register_face/$', views.UserCardView.as_view()),  # 识别人像
    url(r'^reco_face/$', views.FaceCardView.as_view()),  # 识别人像
    url(r'^get_card_list/$', views.GetPersonList.as_view()),  # 获取考勤记录
    url(r'^add_user/$', views.AddUserView.as_view()),  # 增加员工
    url(r'^get_user_list/$', views.GetUserListView.as_view()),  # 查询员工数据
]