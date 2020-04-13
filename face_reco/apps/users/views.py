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
s_time1 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '9:29', '%Y-%m-%d%H:%M')
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
            if datas["result"] is True:
                name = datas["data"]["user_id"]
                # 判断当前这个人是否已经上班打过卡
                user_info = User.objects.filter(name=name, start_time__range=[s_time, s_time1])
                if not user_info:
                    User.objects.create(name=name)
                    data = {
                        "result": True,
                        "message": "上班打卡成功"
                    }
                    return Response(data)
                else:
                    data = {
                        "result": True,
                        "message": "上班打卡成功"
                    }
                    return Response(data)
            else:
                data = {
                    "result": False,
                    "message": "没有找到匹配的人物"
                }
                return Response(data)
        # 是否在下班时间打卡范围
        elif n_time > e_time and n_time < e_time1:
            datas = baidu_face_search()
            if datas["result"] is True:
                name = datas["data"]["user_id"]
                user_info = User.objects.filter(name=name, start_time__range=[s_time, s_time1])
                if user_info:
                    User.objects.filter(name=name, start_time__range=[s_time, s_time1]).update(
                        end_time=n_time
                    )
                    data = {
                        "result": True,
                        "message": "下班打卡成功"
                    }
                    return Response(data)
                else:
                    data = {
                        "result": False,
                        "message": "上班时间没有打卡,请联系管理员"
                    }
                    return Response(data)

            else:
                data = {
                    "result": False,
                    "message": "没有找到匹配的人物"
                }
                return Response(data)
        # 是否早退
        elif n_time < e_time and n_time > s_time1:
            datas = baidu_face_search()
            if datas["result"] is True:
                name = datas["data"]["user_id"]
                user_info = User.objects.filter(name=name, start_time__range=[s_time, s_time1])
                if user_info:
                    User.objects.filter(name=name, start_time__range=[s_time, s_time1]).update(
                        end_time=n_time
                    )
                    data = {
                        "result": True,
                        "message": "早退打卡",
                    }
                    return Response(data)
                else:
                    data = {
                        "result": False,
                        "message": "上班时间没有打卡,请联系管理员"
                    }
                    return Response(data)

            else:
                data = {
                    "result": False,
                    "message": "没有找到匹配的人物"
                }
                return Response(data)


class GetPersonList(APIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    def get(self,request):
        """
        获取所有考勤记录
        """
        start_time = '2020-01-01'
        end_time = datetime.datetime.now()
        user_list = []
        user_infos = User.objects.filter(is_delete=False, start_time__range=[start_time, end_time]).order_by("-start_time")
        print(user_infos)
        if user_infos:
            for user_info in user_infos:
                user_id = user_info.id
                user_name = user_info.name
                s_time = user_info.start_time
                e_time = user_info.end_time
                user_dict = {
                    "user_id": user_id,
                    "user_name": user_name,
                    "start_time": s_time,
                    "end_time": e_time,
                }
                user_list.append(user_dict)
        data = {
            "result": True,
            "data": user_list
        }
        return Response(data=data)

    # 获取考勤记录（按日，周，月，年，自定义查看）
    def post(self, request):
        """
         # 获取考勤记录（按日期或姓名,自定义查看）
        :param request:
        :return:
        """
        data = request.data
        user_list = []
        # 1.是否有时间查询
        if 'start_time' in data.keys() and 'end_time' in data.keys():
            # 开始查询时间
            start_time = request.data["start_time"]
            # 结束查询时间
            end_time = request.data["end_time"]
            if start_time == '' and end_time != '':
                import datetime
                time_end = datetime.date(*map(int, end_time.split('-')))
                end_time = str(time_end + datetime.timedelta(days=1))
                start_time = '2020-01-01'
            elif start_time == '' and end_time == '':
                import datetime
                start_time = '2020-01-01'
                end_time = datetime.datetime.now()
            elif start_time != '' and end_time == '':
                import datetime
                end_time = datetime.datetime.now()
            if "user_name" in data.keys():
                name = request.data["user_name"]
                user_infos = User.objects.filter(is_delete=False, name__contains=name, start_time__range=[start_time, end_time]).order_by(
                    "-start_time")
            else:
                user_infos = User.objects.filter(is_delete=False, start_time__range=[start_time, end_time]).order_by("-start_time")

        else:
            user_infos = User.objects.filter(is_delete=False).order_by("-start_time")
        if user_infos:
            for user_info in user_infos:
                user_id = user_info.id
                user_name = user_info.name
                s_time = user_info.start_time
                e_time = user_info.end_time
                user_dict = {
                    "user_id": user_id,
                    "user_name": user_name,
                    "start_time": s_time,
                    "end_time": e_time,
                }
                user_list.append(user_dict)
        data = {
            "result": True,
            "data": user_list
        }
        return Response(data=data)


# 修改打卡记录（暂时谁都可以修改，没有管理员，但是只能修改打卡时间）
class UpdateCardList(APIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    def post(self,request):
        # 获取要修改的用户id（唯一）
        user_id = request.data["user_id"]
        start_time = request.data["start_time"]
        # 结束时间
        end_time = request.data["end_time"]
        user_info = User.objects.filter(id=user_id)
        if not user_info:
            return Response({"result": False, "message": "没有找到该用户的信息"})
        else:
            User.objects.filter(id=user_id).update(start_time=start_time, end_time=end_time)
            return Response({"result": True, "message": "修改成功"})



