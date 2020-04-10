import datetime
import os

import cv2
from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from users.serializers import UserSerializer
# 上下班打卡范围时间
from utils.baidu_face_search import baidu_face_search

s_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '7:30', '%Y-%m-%d%H:%M')
s_time1 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '9:00', '%Y-%m-%d%H:%M')
e_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '18:00', '%Y-%m-%d%H:%M')
e_time1 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '23:59', '%Y-%m-%d%H:%M')

# 当前时间
n_time = datetime.datetime.now()


class UserCardView(APIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    # get请求方式
    def get(self, request):
        # 判断当前时间是否在上班打卡时间范围内(1.正常打卡 2.打过卡后又识别了就不能再打卡了)
        if n_time > s_time and n_time < s_time1:
            datas = baidu_face_search()
            if datas["result"] == "OK":
                name = datas["data"]["user_id"]
                User.objects.create(name=name)
                data = {
                    "result": "OK",
                    "message": "上班打卡成功"
                }
                return Response(data)
            else:
                data = {
                    "result": "error",
                    "message": "请重新识别"
                }
                return Response(data)
        # 是否在下班时间打卡范围
        elif n_time > e_time and n_time < e_time1:
            datas = baidu_face_search()
            if datas["result"] == "OK":
                name = datas["data"]["user_id"]
                user_info = User.objects.filter(name=name, start_time__range=[s_time, s_time1])
                if user_info:
                    User.objects.filter(name=name, start_time__range=[s_time, s_time1]).update(
                        end_time=n_time
                    )
                    data = {
                        "result": "OK",
                        "message": "下班打卡成功"
                    }
                    return Response(data)
                else:
                    data = {
                        "result": "error",
                        "message": "上班时间没有打卡哦"
                    }
                    return Response(data)

            else:
                data = {
                    "result": "error",
                    "message": "不是该公司员工"
                }
                return Response(data)
        # 是否早退
        elif n_time < e_time and n_time > s_time1:
            datas = baidu_face_search()
            if datas["result"] == "OK":
                name = datas["data"]["user_id"]
                user_info = User.objects.filter(name=name, start_time__range=[s_time, s_time1])
                if user_info:
                    User.objects.filter(name=name, start_time__range=[s_time, s_time1]).update(
                        end_time=n_time
                    )
                    data = {
                        "result": "OK",
                        "message": "早退打卡",
                        "data": datas
                    }
                    return Response(data)
                else:
                    data = {
                        "result": "error",
                        "message": "上班时间没有打卡哦"
                    }
                    return Response(data)

            else:
                data = {
                    "result": "error",
                    "message": "不是该公司员工"
                }
                return Response(data)


class GetPersonList(APIView):
    # 获取考勤记录（按日，周，月，年，自定义查看）
    def post(self, request):
        # 开始查询时间
        start_time = request.data["start_time"]
        # 结束查询时间
        end_time = request.data["end_time"]
        user_list = []
        user_infos = User.objects.filter(start_time__gte=start_time, end_time__lte=end_time).Orderby("start_time")
        if user_infos:
            for user_info in user_infos:
                user_id = user_info.user_id
                s_time = user_info.start_time
                e_time = user_info.end_time
                user_dict = {
                    "user_id": user_id,
                    "start_time": s_time,
                    "end_time": e_time,
                }
                user_list.append(user_dict)
        data = {
            "result": "OK",
            "data": user_list
        }
        return Response(data=data)


