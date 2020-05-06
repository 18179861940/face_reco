import time
import multiprocessing as mp
import cv2
import numpy as np
import asyncio
import websockets

frame = None
faceCascade = cv2.CascadeClassifier(r'open\data\haarcascade_frontalface_alt2.xml')


def websocket_process(img_dict):
    # 服务器端主逻辑
    async def main_logic(websocket, path):
        await recv_msg(websocket, img_dict)
    start_server = websockets.serve(main_logic, '0.0.0.0', 5679)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()


# 接收客户端的消息并处理
async def recv_msg(websocket, img_dict):
    recv_text = await websocket.recv()
    if recv_text == 'begin':
        while True:
            frame = img_dict['img']
            if isinstance(frame, np.ndarray):
                enconde_data = cv2.imencode('.png', frame)[1]
                enconde_str = enconde_data.tostring()
                try:
                    await websocket.send(enconde_str)
                except Exception as e:
                    print(e)
                    return True


def image_put(q, user, pwd, ip):
    rtsp_url = 'rtsp://{0}:{1}@{2}:554/Streaming/Channels/201'.format(user, pwd, ip)
    cap = cv2.VideoCapture(rtsp_url)
    while True:
        ret, frame = cap.read()
        if ret:
            frame = cv2.resize(frame, (800, 600))
            faces = faceCascade.detectMultiScale(
                frame,
                scaleFactor=1.2,
                minNeighbors=5,
                minSize=(40, 40)
            )
            if len(faces) > 0:  # 大于0则检测到人脸
                for face in faces:  # 单独框出每一张人脸
                    x, y, w, h = face  # 获取框的左上的坐标，框的长宽
                    # 画出矩形框
                    cv2.rectangle(frame, (x - 10, y - 10), (x + w - 10, y + h - 10), (0, 255, 0), 2)
            q.put(frame)  # 将图片放入队列
            q.get() if q.qsize() > 1 else time.sleep(0.01)    # 移除队列中的旧图


def image_get(q, img_dict):
    while True:
        frame = q.get()
        if isinstance(frame, np.ndarray):
            img_dict['img'] = frame


def run_single_camera(user_name, user_pwd, camera_ip):
    mp.set_start_method(method='spawn')  # init
    queue = mp.Queue(maxsize=3)
    m = mp.Manager()
    img_dict = m.dict()
    Processes = [mp.Process(target=image_put, args=(queue, user_name, user_pwd, camera_ip)),
                 mp.Process(target=image_get, args=(queue, img_dict)),
                 mp.Process(target=websocket_process, args=(img_dict,))]

    [process.start() for process in Processes]
    [process.join() for process in Processes]


def run():
    run_single_camera('admin', 'fff12345', '192.168.0.242')


if __name__ == '__main__':
    run()