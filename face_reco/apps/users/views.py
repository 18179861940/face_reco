import datetime
from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import AttendCard, UserTable
from users.serializers import UserSerializer

from utils.baidu_face_multi_search import baidu_face_multi_search
from utils.paginations import pagination
from utils.time_difference import minNums, houNums

# 上班打卡时间范围
s_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '7:30', '%Y-%m-%d%H:%M')
s_time1 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '9:29', '%Y-%m-%d%H:%M')
# 上下班打卡分界时间
m_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '12:30', '%Y-%m-%d%H:%M')
# 下班打卡时间范围
e_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '15:00', '%Y-%m-%d%H:%M')
e_time1 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '23:59', '%Y-%m-%d%H:%M')

# 当天日期时间
t_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '00:01', '%Y-%m-%d%H:%M')
t_time1 = datetime.datetime.strptime(str(datetime.datetime.now().date()) + '23:59', '%Y-%m-%d%H:%M')

# 当前时间
n_time = datetime.datetime.now()


# 人脸打卡
class FaceCardView(APIView):
    def post(self, request):
        base64 = request.data["base64"]
        try:
            datas = baidu_face_multi_search(base64)
            clock_list = []
            if datas["error_code"] == 0:
                user_infos = datas["result"]["face_list"]
                if user_infos:
                    for user_info in user_infos:

                        user_list = user_info["user_list"]
                        if user_list == []:
                            pass
                        else:
                            user_name = user_info["user_list"][0]["user_id"]
                            user_up = AttendCard.objects.filter(userName=user_name,
                                                                attendType="1",
                                                                pushTime__range=[t_time, t_time1]
                                                                ).first()
                            user_down = AttendCard.objects.filter(userName=user_name,
                                                                  attendType="2",
                                                                  pushTime__range=[t_time, t_time1]
                                                                  ).first()
                            # 判断当前时间是否在上班打卡时间范围内(1.正常打卡 2.打过卡后又识别了就不能再打卡了)
                            if n_time > s_time and n_time < s_time1:
                                # 判断当前这个人是否已经上班打过卡
                                if not user_up:
                                    AttendCard.objects.create(userName=user_name, attendType="1", attendState="1")
                                    clockData = {
                                        "userName": user_name,
                                        "pushTime": n_time,
                                        "attendType": "1",
                                        "attendState": "1"
                                    }
                                    clock_list.append(clockData)
                                else:   # 上班已经打过卡
                                    clockData = {
                                        "userName": user_name,
                                        "pushTime": user_up.pushTime,
                                        "attendType": "1",
                                        "attendState": "1"
                                    }
                                    clock_list.append(clockData)
                                    # 是否在下班时间打卡范围
                            # 是否在下班时间打卡范围
                            elif n_time > e_time and n_time < e_time1:
                                if user_up and not user_down:
                                    AttendCard.objects.create(userName=user_name, attendType="2", attendState="1")
                                    clockData = {
                                        "userName": user_name,
                                        "pushTime": n_time,
                                        "attendType": "2",
                                        "attendState": "1"
                                    }
                                    clock_list.append(clockData)
                                elif user_up and user_down:
                                    if user_down.attendState == "1":   # 下班正常打过卡
                                        # 判断打卡时间有没有超过两分钟
                                        minute = minNums(user_down.pushTime, n_time)
                                        if minute > 2:
                                            AttendCard.objects.filter(userName=user_name,
                                                                      attendType="2",
                                                                      attendState="1",
                                                                      pushTime__range=[t_time, t_time1]
                                                                      ).update(
                                                pushTime=n_time,
                                            )
                                            clockData = {
                                                "userName": user_name,
                                                "pushTime": n_time,
                                                "attendType": "2",
                                                "attendState": "1"
                                            }
                                            clock_list.append(clockData)
                                        else:
                                            clockData = {
                                                "userName": user_name,
                                                "pushTime": user_down.pushTime,
                                                "attendType": "2",
                                                "attendState": "1"
                                            }
                                            clock_list.append(clockData)
                                    elif user_down.attendState == "3":  # 下班早退打卡
                                        AttendCard.objects.filter(userName=user_name,
                                                                  attendType="2",
                                                                  attendState="3",
                                                                  pushTime__range=[t_time, t_time1]
                                                                  ).update(
                                            pushTime=n_time,
                                            attendState="1"
                                        )
                                        clockData = {
                                            "userName": user_name,
                                            "pushTime": n_time,
                                            "attendType": "2",
                                            "attendState": "1",

                                        }
                                        clock_list.append(clockData)
                                else:  # 上班时间没有打卡，上班时间缺卡
                                    AttendCard.objects.create(userName=user_name, attendType="1", attendState="4", pushTime=s_time1)
                                    AttendCard.objects.create(userName=user_name, attendType="2", attendState="1")
                                    clockData = {
                                        "userName": user_name,
                                        "pushTime": n_time,
                                        "attendType": "2",
                                        "attendState": "1"
                                    }
                                    clock_list.append(clockData)
                            # 迟到打卡范围
                            elif n_time > s_time1 and n_time < m_time:
                                # 如果上班打过卡，则不再打卡
                                if user_up:
                                    clockData = {
                                        "userName": user_name,
                                        "pushTime": user_up.pushTime,
                                        "attendType": "1",
                                        "attendState": user_up.attendState
                                    }
                                    clock_list.append(clockData)
                                else:
                                    AttendCard.objects.create(
                                        userName=user_name,
                                        attendType="1",
                                        attendState="2"
                                    )
                                    clockData = {
                                        "userName": user_name,
                                        "pushTime": n_time,
                                        "attendType": "1",
                                        "attendState": "2"
                                    }
                                    clock_list.append(clockData)
                            # 早退打卡范围
                            elif n_time > m_time and n_time < e_time:
                                # 上班没有打卡，则上班打卡缺卡
                                if user_up:
                                    AttendCard.objects.create(
                                        userName=user_name,
                                        attendType="2",
                                        attendState="3"
                                    )
                                    clockData = {
                                        "userName": user_name,
                                        "pushTime": n_time,
                                        "attendType": "2",
                                        "attendState": "3"
                                    }
                                    clock_list.append(clockData)
                                else:  # 上班没有打卡，则上班打卡缺卡,下班还早退
                                    AttendCard.objects.create(
                                        userName=user_name,
                                        attendType="1",
                                        attendState="4"
                                    )
                                    AttendCard.objects.create(
                                        userName=user_name,
                                        attendType="2",
                                        attendState="3"
                                    )
                                    clockData = {
                                        "userName": user_name,
                                        "pushTime": n_time,
                                        "attendType": "2",
                                        "attendState": "3"
                                    }
                                    clock_list.append(clockData)
                            else:
                                clock_list = {
                                    "success": False,
                                    "message": "打卡失败"
                                }
                else:
                    clock_list = {
                        "success": False,
                        "message": "打卡失败"
                    }
            else:
                clock_list = {
                    "success": False,
                    "message": "打卡失败"
                }
        except:
            clock_list = {
                "success": False,
                "message": "打卡失败"
            }

        return Response(data=clock_list)


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
        try:
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
        except:
            user_lists = {
                "success": False,
                "message": "查询失败"
            }
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
            name = ''
        if "attendType" in data.keys():
            attendType = request.data["attendType"]
        else:
            attendType = '1'
        if "attendState" in data.keys():
            attendState = request.data["attendState"]
        else:
            attendState = '1'
        try:
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
                        "id": user_id,
                        "userName": user_name,
                        "userCode": user_code,
                        "pushTime": push_time,
                        "attendState": attend_state,
                    }
                    user_list.append(user_dict)
            user_lists = pagination(current_page, page_size, user_list)
        except:
            user_lists = {
                "success": False,
                "message": "查询失败"
            }
        return Response(data=user_lists)


# 增加员工
class AddUserView(APIView):
    def post(self, request):
        """增加员工"""
        userName = request.data["userName"]
        userCode = request.data["userCode"]
        sex = request.data["sex"]
        if "state" in request.data.keys():
            state = request.data["state"]
        else:
            state = "1"
        try:
            UserTable.objects.create(
                userName=userName,
                userCode=userCode,
                sex=sex,
                state=state,
            )
            data = {
                "success": True,
                "message": "保存成功"
            }
        except:
            data = {
                "success": False,
                "message": "添加失败"
            }

        return Response(data=data)


# 查询员工数据
class GetUserListView(APIView):
    def post(self, request):
        user_list = []
        data = request.data
        currentPage = request.data["page"]
        rows = request.data["rows"]
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
        if 'userName' in data.keys():
            userName = request.data["userName"]
        else:
            userName = ''
        if 'userCode' in data.keys():
            userCode = request.data["userCode"]
        else:
            userCode = ''
        if 'sex' in data.keys():
            sex = request.data["sex"]
        else:
            sex = '1'
        try:
            user_infos = UserTable.objects.filter(
                userName__contains=userName,
                userCode__contains=userCode,
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
                        "insertTime": insertTime,
                        "state": state,
                    }
                    user_list.append(user_dict)
            user_info = pagination(currentPage, rows, user_list)
        except:
            user_info = {
                "success": False,
                "message": "查询失败"
            }
        return Response(data=user_info)

