import requests
from face_reco.apps.utils import get_access_token
from face_reco.apps.utils.pic_to_base64 import picToBase64, getPicPath

# target_path = 'D:\\PycharmProjects\\face_attendance\\face_attendance\\photoSet'
# file_path = getPicPath(target_path)   # 调用图片接口获取最后一个数据


# 调用百度API完成M:N人脸搜索
# def baidu_face_multi_search(file_path):
def baidu_face_multi_search(base64):
    card_list = []
    request_url = "https://aip.baidubce.com/rest/2.0/face/v3/multi-search"
    params = {
        # "image": picToBase64(file_path),
        "image": base64,
        "image_type": "BASE64",  # 图片类型
        "group_id_list": "people",  # 这是要检索的图片库
        "max_face_num": 3,  # 最多处理人脸的数量
        "match_threshold": 70,  # score低于此阈值用户的信息将不会被返回
    }
    access_token = get_access_token.getAccessToken()
    if (access_token == ""):
        print("获取access_token失败")
        data = {
            "error_code": 100,
            "message": "无效的access_token参数"
        }
        return data
    # 请求地址
    request_url = request_url + "?access_token=" + access_token
    # 请求头
    headers = {'content-Type': 'application/json'}
    # 响应
    response = requests.post(request_url, data=params, headers=headers)
    json = response.json()
    error_code = json['error_code']
    if (error_code != 0):
        print("==未识别图像==")
        data = {
            "error_code": 222207,
            "message": "未找到匹配的用户"
        }
        return data
    # 人脸列表
    face_list = json['result']['face_list']
    for face in face_list:
        user_list = face["user_list"]
        for user in user_list:
            group_id = user["group_id"]
            user_id = user["user_id"]
            user_info = user["user_info"]
            score = user["score"]
            card_dict = {
                "group_id": group_id,
                "user_id": user_id,
                "user_info": user_info,
                "score": score,
            }
            if score > 70:
                card_list.append(card_dict)
                # print(user_id + "识别成功")
    # print(card_list)
    return json

# if __name__ == '__main__':
#     baidu_face_multi_search(file_path)

