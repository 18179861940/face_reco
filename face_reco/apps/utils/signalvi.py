import base64
from io import BytesIO
import cv2
from PIL import Image
# from utils.baidu_face_multi_search import baidu_face_multi_search


def generate():
    # 调用人脸识别分类器
    faceCascade = cv2.CascadeClassifier(r'open\data\haarcascade_frontalface_alt2.xml')
    # 开启摄像头
    # cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    cam_url = 'rtsp://admin:fff12345@192.168.0.242:554/Streaming/Channels/201'   #小头无云台
    # cam_url = 'rtsp://admin:fff12345@192.168.0.53:554/11'  # 大头有云台
    # 用以下模板调用其他摄像头，仅限海康
    # cam_url='rtsp://admin: 密码  @ IP :554/Streaming/Channels/201'
    cap = cv2.VideoCapture(cam_url)  # 调用IP摄像头
    fource = cv2.VideoWriter_fourcc(*'avc1')
    out = cv2.VideoWriter("", fource, 25.0, (1920, 1080))
    print("********", cap.isOpened())
    ok = True
    # 设置人脸边框颜色为绿色
    color = (0, 225, 0)
    while ok and cap.isOpened():
        # 读取摄像头中的图像，ok为是否读取成功的判断参数
        # img是每一帧的图像，是个三维矩阵
        ok, img = cap.read()
        # 转换成灰度图像
        # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 人脸检测
        # 1.2为图片缩放比例，minNeighbors为需要至少检测多少次才能确定目标
        # faces = faceCascade.detectMultiScale(
        #     gray,
        #     scaleFactor=1.2,
        #     minNeighbors=5,
        #     minSize=(32, 32)
        # )
        # if len(faces) > 0:  # 大于0则检测到人脸
        #     # if n < 5:
        #     for face in faces:  # 单独框出每一张人脸
        #         x, y, w, h = face  # 获取框的左上的坐标，框的长宽
        #         # 画出矩形框
        #         cv2.rectangle(img, (x - 10, y - 10), (x + w - 10, y + h - 10), color, 2)
        #         image = img[y - 10: y + h + 10, x - 10: x + w + 10]
        #         base64_res = frame2base64(img)
        #         source = baidu_face_multi_search(base64_res)
        #         card_list = []
        #         try:
        #             face_list = source['result']['face_list']
        #             print(face_list)
        #             for face in face_list:
        #                 user_list = face["user_list"]
        #                 for user in user_list:
        #                     group_id = user["group_id"]
        #                     user_id = user["user_id"]
        #                     user_info = user["user_info"]
        #                     score = user["score"]
        #                     card_dict = {
        #                         "group_id": group_id,
        #                         "user_id": user_id,
        #                         "user_info": user_info,
        #                         "score": score,
        #                     }
        #                     card_list.append(card_dict)
        #             for i in range(0, len(card_list)):
        #                 name = card_list[i]["user_id"]
        #                     # name_list.append(name)
        #         except Exception as e:
        #             print(e)
        #         font = cv2.FONT_HERSHEY_SIMPLEX  # 字体
        #         cv2.putText(img,
        #                     '',
        #                     # 'checked people face',
        #                     (x + 10, y + 10),   # 坐标
        #                     font,  # 字体
        #                     1,   # 字号
        #                     (0, 0, 205),  # 颜色
        #                     4  # 字的线宽
        #                     )
        # else:
        #     cv2.putText(img, '', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 4)
        # 显示图像
        cv2.imshow('video', img)
        # 等待1毫秒看是否有按键输入
        k = cv2.waitKey(1)


    # 释放摄像头并销毁所有窗口
    cap.release()
    out.release()
    cv2.destroyAllWindows()

def frame2base64(frame):
    img = Image.fromarray(frame) #将每一帧转为Image
    output_buffer = BytesIO() #创建一个BytesIO
    img.save(output_buffer, format='JPEG') #写入output_buffer
    byte_data = output_buffer.getvalue() #在内存中读取
    base64_data = base64.b64encode(byte_data) #转为BASE64
    # print("ba", base64_data)
    return base64_data #转码成功 返回base64编码

generate()
