import requests
from face_reco.apps.utils import get_access_token
from face_reco.apps.utils.pic_to_base64 import picToBase64, getPicPath
"""
将保存在本地的图片与百度数据库里面存放的图片做对比
每新增打开一次摄像头就调用一次
"""
target_path = 'C:\\Users\\MyPC\\PycharmProjects\\face_attendance\\face_attendance\\photoSet'
file_path = getPicPath(target_path)   # 调用图片接口获取最后一个数据


# 调用百度API完成1:N人脸搜索
# def baidu_face_search(file_path):
def baidu_face_search():
    request_url = "https://aip.baidubce.com/rest/2.0/face/v3/search"
    params = {
            "image": picToBase64(file_path),
            "image_type": "BASE64",
            "group_id_list": "people"
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
    score = json['result']['user_list'][0]['score']
    user_id = json['result']['user_list'][0]['user_id']
    group_id = json['result']['user_list'][0]['group_id']
    if int(score) < 80:
        print('没有找到匹配的人物')
        return 'error'
    else:
        print('在%s用户组找到用户%s,匹配度为%s' % (group_id, user_id, score))
        print('%s打卡成功' % user_id)
        data = {
            "result": "OK",
            "data": {
                "score": score,
                "user_id": user_id,
                "group_id": group_id
            }

        }
        return data


if __name__ == '__main__':
    baidu_face_search(file_path)
