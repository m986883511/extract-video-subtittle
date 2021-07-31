import base64
import cv2
import os
import logging
import subprocess
import numpy as np
from flask import request, Flask, jsonify
from pydub import AudioSegment
from pydub.silence import detect_nonsilent

import config
from backend.tools.infer import utility
from backend.tools.infer.predict_system import TextSystem

app = Flask(__name__)
TextRecogniser = None
current_dir = os.path.dirname(__file__)
extract_time_point_save = {}
temp_path = os.path.join(current_dir, 'temp')
if not os.path.exists(temp_path):
    os.makedirs(temp_path)


# 加载文本检测+识别模型
def load_text_recogniser_model():
    # 获取参数对象
    args = utility.parse_args()
    # 是否使用GPU加速
    args.use_gpu = config.USE_GPU
    if config.USE_GPU:
        # 设置文本检测模型路径
        args.det_model_dir = config.DET_MODEL_PATH
        # 设置文本识别模型路径
        args.rec_model_dir = config.REC_MODEL_PATH
    else:
        # 加载快速模型
        args.det_model_dir = config.DET_MODEL_FAST_PATH
        # 加载快速模型
        # args.rec_model_dir = config.REC_MODEL_FAST_PATH
        args.rec_model_dir = config.REC_MODEL_PATH
    # 设置字典路径
    args.rec_char_dict_path = config.DICT_PATH
    logging.error('args={}'.format(args))
    return TextSystem(args)


def base64_to_image(base64_code):
    # base64解码
    img_data = base64.b64decode(base64_code)
    # 转换为np数组
    img_array = np.fromstring(img_data, np.uint8)
    # 转换成opencv可用格式
    img = cv2.imdecode(img_array, cv2.COLOR_RGB2BGR)
    return img


def get_coordinates(dt_box):
    """
    从返回的检测框中获取坐标
    :param dt_box 检测框返回结果
    :return list 坐标点列表
    """
    coordinate_list = list()
    if isinstance(dt_box, list):
        for i in dt_box:
            i = list(i)
            (x1, y1) = int(i[0][0]), int(i[0][1])
            (x2, y2) = int(i[1][0]), int(i[1][1])
            (x3, y3) = int(i[2][0]), int(i[2][1])
            (x4, y4) = int(i[3][0]), int(i[3][1])
            xmin = max(x1, x4)
            xmax = min(x2, x3)
            ymin = max(y1, y2)
            ymax = min(y3, y4)
            coordinate_list.append((xmin, xmax, ymin, ymax))
    return coordinate_list


@app.route("/text_recognition", methods=['POST'])
def text_recognition():
    if not callable(TextRecogniser):
        return jsonify({'result': 'please load model first'})
    img = base64.b64decode(str(request.form['image']))
    image_data = np.fromstring(img, np.uint8)
    img = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
    dt_box, rec_res = TextRecogniser(img)
    coordinates = get_coordinates(dt_box)
    text_res = [(res[0], res[1]) for res in rec_res]
    result = [(coordinate, content[0]) for content, coordinate in zip(text_res, coordinates)]
    print(result)
    return jsonify(result)


@app.route("/", methods=['GET'])
def index():
    api = {
        '/': 'get方法，返回支持的api说明',
        '/load_model': "get方法，加载文字识别模型，返回值为{'result': 'load model success'}",
        '/text_recognition': "post方法，"
    }
    return jsonify(api)


@app.route("/extract_voice", methods=['POST'])
def extract_voice():
    print('start /extract_voice')
    name = request.values.get('save_name')
    output_vocals_path = os.path.join(current_dir, 'temp', ''.join(name.split('.')[:-1]), 'vocals.wav')
    success_result = {'file': os.path.abspath(output_vocals_path)}
    if os.path.isfile(output_vocals_path):
        return jsonify(success_result)
    sound_path = os.path.join(temp_path, name)
    content = request.files.get('save_data').read()
    with open(sound_path, 'wb') as f:
        f.write(content)
    cmd = 'spleeter separate -d 1800 -p spleeter:2stems -o {} {}'.format(temp_path, sound_path)
    print(cmd)
    try:
        subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
    except subprocess.CalledProcessError as e:
        err = 'execute {} failed, code={}, stderr={}'.format(cmd, e.returncode, e.output.strip())
        print(err)
        raise Exception(err)
    else:
        return jsonify(success_result)


@app.route("/load_model", methods=['GET'])
def load_model():
    value = 'load model success'
    try:
        global TextRecogniser
        TextRecogniser = load_text_recogniser_model()
    except Exception as e:
        value = 'load model failed, err={}'.format(str(e))
    return jsonify({'result': value})


@app.route("/extract_time_point", methods=['GET'])
def extract_time_point():
    print('start /extract_time_point')
    file_path = request.json.get('file')
    if file_path in extract_time_point_save:
        print('{} already extract time point'.format(file_path))
        return jsonify({'result': extract_time_point_save[file_path]})
    sound = AudioSegment.from_mp3(file_path)
    chunks = detect_nonsilent(sound, min_silence_len=430, silence_thresh=-45)  # ,keep_silence=400)
    extract_time_point_save[file_path] = chunks
    return jsonify({'result': chunks})


if __name__ == "__main__":
    app.run("0.0.0.0", port=6666)
