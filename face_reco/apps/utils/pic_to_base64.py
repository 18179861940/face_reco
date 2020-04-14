import base64
import os

# 存放照片的绝对地址（需要自己改变）
# target_path = 'C:\\Users\\MyPC\\PycharmProjects\\face_attendance\\face_attendance\\photoSet'


# 图片转码成为base64 百度要求
def picToBase64(file_path):
    with open(file_path, 'rb') as f:
        img = base64.b64encode(f.read()).decode('utf-8')
        return img


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
        pa = target_path + "\\" + dirs[n-2]
        return pa
getPicPath('C:\\Users\\MyPC\\Downloads')