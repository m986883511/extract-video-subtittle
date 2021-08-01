import cv2


class Value:
    all_time = ''
    now_time = ''


def get_seconds(time_str: str):
    time_list = time_str.strip().split(':')
    time_list = [float(i) for i in time_list]
    seconds = 0
    for i, num in enumerate(time_list[::-1]):
        seconds = seconds + 60 ** i * num
    return seconds


def get_extract_voice_progress(input_str: str)->int:
    if 'Duration:' in input_str:
        Value.all_time = input_str[10:21]
        index = input_str.index('Duration:')
        Value.all_time = input_str[index + 10:index + 21]
    if input_str[:5] == 'size=':
        Value.now_time = input_str[21:32]
        # print(Value.now_time, Value.all_time)
        progress = get_seconds(Value.now_time) / get_seconds(Value.all_time) * 100
        return int(progress)

# def CropImage4File(image):
#     sp = image.shape  # 获取图像形状：返回【行数值，列数值】列表
#     sz1 = sp[0]  # 图像的高度（行 范围）
#     sz2 = sp[1]  # 图像的宽度（列 范围）
#     # sz3 = sp[2]                #像素值由【RGB】三原色组成
#
#     # 你想对文件的操作
#     a = int(sz1 / 2 - 64)  # x start
#     b = int(sz1 / 2 + 64)  # x end
#     c = int(sz2 / 2 - 64)  # y start
#     d = int(sz2 / 2 + 64)  # y end
#     cropImg = image[a:b, c:d]  # 裁剪图像
#     cv2.imwrite(dest, cropImg)  # 写入图像路径
