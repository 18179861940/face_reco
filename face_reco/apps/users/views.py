import datetime
import os

import cv2
from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import AttendCard
from users.serializers import UserSerializer
# 上下班打卡范围时间
from utils.baidu_face_search import baidu_face_search
from utils.paginations import pagination

s_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '7:30', '%Y-%m-%d%H:%M')
s_time1 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '18:29', '%Y-%m-%d%H:%M')
e_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '19:00', '%Y-%m-%d%H:%M')
e_time1 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '23:59', '%Y-%m-%d%H:%M')

# 当前时间
n_time = datetime.datetime.now()


class UserCardView(APIView):
    serializer_class = UserSerializer
    queryset = AttendCard.objects.all()
    # get请求方式
    def get(self, request):
        # 判断当前时间是否在上班打卡时间范围内(1.正常打卡 2.打过卡后又识别了就不能再打卡了)
        if n_time > s_time and n_time < s_time1:
            datas = baidu_face_search()
            if datas["result"] is True:
                name = datas["data"]["user_id"]
                # 判断当前这个人是否已经上班打过卡
                user_info = AttendCard.objects.filter(userName=name, attendType="1", pushTime__range=[s_time, s_time1])
                if not user_info:
                    AttendCard.objects.create(userName=name)
                    data = {
                        "result": True,
                        "message": name + "上班打卡成功"
                    }
                    return Response(data)
                else:
                    data = {
                        "result": True,
                        "message": name + "上班已经打过卡"
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
                user_info = AttendCard.objects.filter(userName=name, pushTime__range=[s_time, s_time1])
                if user_info:
                    AttendCard.objects.create(userName=name, attendType="2")
                    data = {
                        "result": True,
                        "message":  name + "下班打卡成功"
                    }
                    return Response(data)
                else:
                    data = {
                        "result": False,
                        "message": name + "上班时间没有打卡,请联系管理员"
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
                user_info = AttendCard.objects.filter(userName=name, pushTime__range=[s_time, s_time1])
                if user_info:
                    AttendCard.objects.create(userName=name, attendType="2", attendState="3")
                    data = {
                        "result": True,
                        "message": name + "早退打卡",
                    }
                    return Response(data)
                else:
                    data = {
                        "result": False,
                        "message": name + "上班时间没有打卡,请联系管理员"
                    }
                    return Response(data)

            else:
                data = {
                    "result": False,
                    "message": "没有找到匹配的人物"
                }
                return Response(data)
        # 是否迟到
        elif n_time > s_time1 and n_time < e_time:
            datas = baidu_face_search()
            if datas["result"] is True:
                name = datas["data"]["user_id"]
                user_info = AttendCard.objects.filter(userName=name, attendType="1", pushTime__range=[s_time, s_time1])
                if user_info:
                    data = {
                        "result": True,
                        "message": name + "上班已经打过卡",
                    }
                    return Response(data)
                else:
                    AttendCard.objects.create(userName=name, attendType="1", attendState="2")
                    data = {
                        "result": True,
                        "message": name + "迟到打卡"
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
    queryset = AttendCard.objects.all()
    def get(self,request):
        """
        获取所有考勤记录
        """
        start_time = '2020-01-01'
        end_time = datetime.datetime.now()
        user_list = []
        user_infos = AttendCard.objects.filter(is_delete=False, attendType="1", pushTime__range=[start_time, end_time]).order_by("-pushTime")
        print(user_infos)
        if user_infos:
            for user_info in user_infos:
                user_id = user_info.id
                user_name = user_info.userName
                user_code = user_info.userCode
                user_type = user_info.attendType
                push_time = user_info.pushTime
                attend_state = user_info.attendState
                user_dict = {
                    "id": user_id,
                    "userName": user_name,
                    "userCode": user_code,
                    "attendType": user_type,
                    "attendState": attend_state,
                    "pushTime": push_time,
                }
                user_list.append(user_dict)
        user_lists = pagination(1, 2, user_list)
        data = {
            "result": True,
            "data": user_lists
        }
        return Response(data=data)

    # 获取考勤记录
    def post(self, request):
        """
         # 获取考勤记录（按日期或姓名,自定义查看）
        :param request:
        :return:
        """
        data = request.data
        user_list = []
        current_page = request.data['page']  # 当前页
        page_size = request.data['rows']  # 一页数据多少条
        # 1.是否有时间查询
        if 'startDate' in data.keys():
            # 开始查询时间
            start_time = request.data["startDate"]
        else:
            import datetime
            start_time = '2020-01-01'
        if 'endDate' in data.keys():
            # 结束查询时间
            end_time = request.data["endDate"]
        else:
            import datetime
            end_time = datetime.datetime.now()
        if "userName" in data.keys():
            name = request.data["userName"]
        else:
            name = None
        if "attendType" in data.keys():
            attendType = request.data["attendType"]
        else:
            attendType = '1'
        if "attendState" in data.keys():
            attendState = request.data["attendState"]
        else:
            attendState = '1'
        user_infos = AttendCard.objects.filter(is_delete=False,
                                               userName__contains=name,
                                               pushTime__range=[start_time, end_time],
                                               attendType=attendType,
                                               attendState=attendState
                                               ).order_by("-pushTime")
        if user_infos:
            for user_info in user_infos:
                user_id = user_info.id
                user_name = user_info.userName
                user_code = user_info.userCode
                push_time = user_info.pushTime
                attend_state = user_info.attendState
                user_dict = {
                    "user_id": user_id,
                    "user_name": user_name,
                    "user_code": user_code,
                    "push_time": push_time,
                    "attend_state": attend_state,
                }
                user_list.append(user_dict)
        user_lists = pagination(current_page,page_size,user_list)
        data = {
            "result": True,
            "data": user_lists
        }
        return Response(data=data)


# 修改打卡记录（暂时谁都可以修改，没有管理员，但是只能修改打卡时间）
class UpdateCardList(APIView):
    serializer_class = UserSerializer
    queryset = AttendCard.objects.all()

    def post(self,request):
        # 获取要修改的用户id（唯一）
        user_id = request.data["user_id"]
        start_time = request.data["start_time"]
        # 结束时间
        end_time = request.data["end_time"]
        user_info = AttendCard.objects.filter(id=user_id)
        if not user_info:
            return Response({"result": False, "message": "没有找到该用户的信息"})
        else:
            AttendCard.objects.filter(id=user_id).update(pushTime=start_time, pushEndTime=end_time)
            return Response({"result": True, "message": "修改成功"})


class DeleteCardRecord(APIView):
    serializer_class = UserSerializer
    queryset = AttendCard.objects.all()
    def post(self,request):
        # 获取要修改的用户id（唯一）
        user_id = request.data["user_id"]
        user_info = AttendCard.objects.filter(id=user_id)
        if not user_info:
            return Response({"result": False, "message": "没有找到该用户的信息"})
        else:
            AttendCard.objects.filter(id=user_id).update(is_delete=True)
            return Response({"result": True, "message": "删除成功"})


