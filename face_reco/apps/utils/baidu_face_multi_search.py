import requests
from face_reco.apps.utils import get_access_token


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
    # if (access_token == ""):
    #     print("获取access_token失败")
    #     data = {
    #         "error_code": 100,
    #         "message": "无效的access_token参数"
    #     }
    #     return data
    # 请求地址
    request_url = request_url + "?access_token=" + access_token
    # 请求头
    headers = {'content-Type': 'application/json',
               'Connection': 'close'
               }
    # 响应
    response = requests.post(request_url, data=params, headers=headers,verify=False)
    json = response.json()
    return json

# if __name__ == '__main__':
#     baidu_face_multi_search(file_path)

