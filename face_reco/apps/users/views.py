import datetime
import os

import cv2
from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import AttendCard, UserTable
from users.serializers import UserSerializer
# 上下班打卡范围时间
from utils.baidu_face_multi_search import baidu_face_multi_search
from utils.baidu_face_search import baidu_face_search
from utils.paginations import pagination

s_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '7:30', '%Y-%m-%d%H:%M')
s_time1 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '9:29', '%Y-%m-%d%H:%M')
e_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '18:00', '%Y-%m-%d%H:%M')
e_time1 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '23:59', '%Y-%m-%d%H:%M')

# 当天日期时间
t_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '00:01', '%Y-%m-%d%H:%M')
t_time1 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '23:59', '%Y-%m-%d%H:%M')

# 当前时间
n_time = datetime.datetime.now()


class UserCardView(APIView):
    serializer_class = UserSerializer
    queryset = AttendCard.objects.all()
    # get请求方式
    def get(self, request):
        pass


# 人脸打卡
class FaceCardView(APIView):
    def post(self, request):
        base64 = request.data["base64"]
        data = {}
        datas = baidu_face_multi_search(base64)
        if datas["error_code"] == 0:
            user_infos = datas["result"]["face_list"]
            if user_infos:
                for user_info in user_infos:
                    user_name = user_info["user_list"][0]["user_id"]
                    user_up = AttendCard.objects.filter(userName=user_name,
                                                        attendType="1",
                                                        pushTime__range=[t_time, t_time1]
                                                        )
                    user_down = AttendCard.objects.filter(userName=user_name,
                                                          attendType="2",
                                                          pushTime__range=[t_time, t_time1]
                                                          )
                    # 判断当前时间是否在上班打卡时间范围内(1.正常打卡 2.打过卡后又识别了就不能再打卡了)
                    if n_time > s_time and n_time < s_time1:
                        # 判断当前这个人是否已经上班打过卡
                        if not user_up:
                            AttendCard.objects.create(userName=user_name, attendType="1", attendState="1")
                            data = {
                                "retCode": "0000",
                                "retMsg": user_name + "上班打卡成功"
                            }
                            return Response(data)
                        else:
                            data = {
                                "retCode": "0000",
                                "retMsg": user_name + "上班已经打过卡"
                            }
                            return Response(data)
                            # 是否在下班时间打卡范围
                    # 是否在下班时间打卡范围
                    elif n_time > e_time and n_time < e_time1:
                        if user_up and not user_down:
                            AttendCard.objects.create(userName=user_name, attendState="1", attendType="2")
                            data = {
                                "retCode": "0000",
                                "retMsg": user_name + "下班打卡成功"
                            }
                            return Response(data)
                        elif user_up and user_down:
                            data = {
                                "retCode": "0000",
                                "retMsg": user_name + "下班打卡成功"
                            }
                            return Response(data)
                        else:  # 上班时间没有打卡
                            AttendCard.objects.create(userName=user_name, attendType="1", attendState="2")
                            AttendCard.objects.create(userName=user_name, attendType="2", attendState="1")
                            data = {
                                "retCode": "0000",
                                "retMsg": user_name + "上班时间没有打卡，下班打卡成功"
                            }
                            return Response(data)
                    # 是否迟到
                    elif n_time > s_time1 and n_time < e_time:
                        if user_up and user_down:
                            #  上下班都已经打卡
                            data = {
                                "retCode": "0000",
                                "retMsg": user_name + "已经打过卡",
                            }
                            return Response(data)
                        elif user_up and not user_down:
                            # 上班打卡，下班没打卡
                            AttendCard.objects.create(
                                userName=user_name,
                                attendType="2",
                                attendState="3"
                            )
                            data = {
                                "retCode": "0000",
                                "retMsg": user_name + "早退打卡",
                            }
                            return Response(data)
                        elif not user_up and not user_down:
                            # 上下班都没打卡，算早退
                            AttendCard.objects.create(
                                userName=user_name,
                                attendType="2",
                                attendState="3"
                            )
                            data = {
                                "retCode": "0000",
                                "retMsg": user_name + "早退打卡",
                            }
                            return Response(data)
                        else:  # 上班没打卡
                            data = {
                                "retCode": "0000",
                                "retMsg": user_name + "早退打卡",
                            }
                            return Response(data)
                    else:
                        data = {
                            "retCode": "0000",
                            "retMsg": "不在正常打卡时间范围",
                        }
                        return Response(data)
            else:
                data = {
                    "retCode": 222207,
                    "retMsg": "未找到匹配的用户"
                }

        elif datas["error_code"] == 222207:
            data = {
                "retCode": "222207",
                "retMsg": "未找到匹配的用户"
            }
        else:
            data = {
                "retCode": "0000",
                "retMsg": "添加成功"
            }
        return Response(data=data)


# 获取考勤记录
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
        user_lists = pagination(1, 10, user_list)
        return Response(data=user_lists)

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
        user_lists = pagination(current_page, page_size, user_list)
        data = {
            "result": True,
            "data": user_lists
        }
        return Response(data=data)


# 增加员工
class AddUserView(APIView):
    def post(self, request):
        """增加员工"""
        userName = request.data["userName"]
        userCode = request.data["userCode"]
        sex = request.data["sex"]
        state = request.data["state"]
        UserTable.objects.create(
            userName=userName,
            userCode=userCode,
            sex=sex,
            state=state,
        )
        data = {
            "retCode": "0000",
            "retMsg": "添加成功"
        }
        return Response(data=data)


# 查询员工数据
class GetUserListView(APIView):
    def post(self, request):
        user_list = []
        data = request.data
        currentPage = request.data["page"]
        rows = request.data["rows"]
        userName = request.data["userName"]
        userCode = request.data["userCode"]
        sex = request.data["sex"]
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
        user_infos = UserTable.objects.filter(
            userName__contains=userName,
            userCode=userCode,
            sex=sex,
            insertTime__range=[start_time, end_time]
        ).order_by("insertTime")

        if user_infos:
            for user_info in user_infos:
                user_id = user_info.id
                user_name = user_info.userName
                user_code = user_info.userCode
                sex = user_info.sex
                state = user_info.state
                insertTime = user_info.insertTime
                user_dict = {
                    "id": user_id,
                    "userName": user_name,
                    "userCode": user_code,
                    "sex": sex,
                    "state": state,
                    "insertTime": insertTime,
                }
                user_list.append(user_dict)
        user_info = pagination(currentPage, rows, user_list)

        return Response(data=user_info)

