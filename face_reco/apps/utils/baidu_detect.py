import requests

from utils import get_access_token
from utils.pic_to_base64 import picToBase64, getPicPath

target_path = 'C:\\Users\\MyPC\\PycharmProjects\\face_attendance\\face_attendance\\photoSet'
file_path = getPicPath(target_path)   # 调用图片接口获取最后一个数据

def baidu_detect():
    request_url = "https://aip.baidubce.com/rest/2.0/face/v3/detect"
    params = {
        "image": picToBase64(file_path),
        "image_type": "BASE64",
        "max_face_num": 1,
    }

    access_token = get_access_token.getAccessToken()
    if (access_token == ""):
        print("获取access_token失败")
        return
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
        return
    print(json)
    if json["error_code"] == 0:
        result = json["result"]
        left = result["face_list"][0]["location"]["left"]
        top = result["face_list"][0]["location"]["top"]
        width = result["face_list"][0]["location"]["width"]
        height = result["face_list"][0]["location"]["height"]
        rotation = result["face_list"][0]["location"]["rotation"]
        data = left, top, width, height, rotation
        print("666",data)
        return data
