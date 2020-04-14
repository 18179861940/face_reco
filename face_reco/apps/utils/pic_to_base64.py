import base64
import os

# 存放照片的绝对地址（需要自己改变）
# target_path = 'C:\\Users\\MyPC\\PycharmProjects\\face_attendance\\face_attendance\\photoSet'


# 图片转码成为base64 百度要求
def picToBase64(file_path):
    with open(file_path, 'rb') as f:
        img = base64.b64encode(f.read()).decode('utf-8')
        return img

import time
# 格式化时间戳为本地的时间
nowtime = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
print(nowtime)
# 遍历获取图片路径
def getPicPath(target_path):
    # 返回指定路径的文件夹名称
    dir_list = []
    dirs = os.listdir(target_path)
    # for dir in dirs:
    #     pa = target_path + "\\" + dir
    #     dir_list.append(pa)
    # print(dir_list)
    # return dir_list
    n = int(len(dirs))
    if len(dirs):
        # 拼接字符串(根据情况修改)
        # pa = target_path + "\\" + str(int(nowtime)) + ".jpg"
        pa = target_path + "\\" + dirs[n-1]
        print(pa)
        return pa
getPicPath('C:\\Users\\MyPC\\Downloads')