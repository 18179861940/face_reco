import base64
from io import BytesIO
import cv2
from PIL import Image


def generate():
    # 调用人脸识别分类器
    faceCascade = cv2.CascadeClassifier(r'open\data\haarcascade_frontalface_alt2.xml')
    # 开启摄像头
    # cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    cam_url = 'rtsp://admin:fff12345@192.168.0.242:554/Streaming/Channels/201'   #小头无云台
    cap = cv2.VideoCapture(cam_url)  # 调用IP摄像头
    ok = True
    n=0
    while ok and cap.isOpened():
        # 读取摄像头中的图像，ok为是否读取成功的判断参数
        # img是每一帧的图像，是个三维矩阵
        ok, frame = cap.read()
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))  # 将每一帧转为Image
        output_buffer = BytesIO()  # 创建一个BytesIO
        img.save(output_buffer, format='JPEG')  # 写入output_buffer
        byte_data = output_buffer.getvalue()  # 在内存中读取
        base64_data = base64.b64encode(byte_data)  # 转为BASE64
        n = n + 1
        if n > 10:
            break
        # 等待1毫秒看是否有按键输入
        k = cv2.waitKey(1)
        yield base64_data + b'\\r\\n'

    # 释放摄像头并销毁所有窗口
    cap.release()
    cv2.destroyAllWindows()


def frame2base64(frame):
    img = Image.fromarray(frame) #将每一帧转为Image
    output_buffer = BytesIO() #创建一个BytesIO
    img.save(output_buffer, format='JPEG') #写入output_buffer
    byte_data = output_buffer.getvalue() #在内存中读取
    base64_data = base64.b64encode(byte_data) #转为BASE64
    # print("ba", base64_data)
    return base64_data #转码成功 返回base64编码

