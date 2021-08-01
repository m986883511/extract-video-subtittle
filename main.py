import datetime
import json
import os
import time
import sys
import base64

current_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(current_dir, 'ffmpeg'))

import cv2
import srt
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QTextEdit, QLabel, QFileDialog, QMessageBox
from PyQt5.QtWidgets import QSlider, QVBoxLayout, QLineEdit, QWidget, QHBoxLayout
from PyQt5.QtWidgets import QPushButton, QGridLayout, QDialog, QTabWidget

from interface import ExtractSubtitleApi
from custom_component import PaintRectLabel
from scripts import get_extract_voice_progress, get_data_time


class SaveResult:
    def __init__(self):
        self.result = {
            'video': {},
            'text': {
                'sub_tittle': []
            }
        }

    def get_data_time(self, str_time):
        return datetime.timedelta(hours=int(str_time[0:2]), minutes=int(str_time[4:5]),
                                  seconds=int(str_time[7:8]), milliseconds=int(str_time[9:11]))

    def add_sub_tittle(self, start_time, end_time, text):
        if text:
            self.result['text']['sub_tittle'].append(
                {'start_time': start_time, 'end_time': end_time, 'text': text})

    def set_video_msg(self, video_path):
        self.result['video_path'] = video_path

    def save_json(self):
        video_path = self.result.get('video_path', '')
        video_name = ''.join(os.path.basename(video_path).split('.')[:-1])
        if video_name:
            save_path = os.path.join(current_dir, 'temp', video_name + '.json')
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(json.dumps(self.result, indent=4, ensure_ascii=False))
        else:
            print('not set video name')

    def save_srt(self):
        video_path = self.result.get('video_path', '')
        video_name = ''.join(os.path.basename(video_path).split('.')[:-1])
        save_path = os.path.join(current_dir, 'temp', video_name + '.srt')
        sub_tittles = [
            srt.Subtitle(i, start=get_data_time(i['start_time']), end=get_data_time(i['end_time']), content=i['text'])
            for i in self.result['text']['sub_tittle']
        ]
        with open(save_path, 'w') as f:
            f.write(srt.compose(sub_tittles))


class SoftData:
    class Step:
        step1 = '第一步：选择视频文件，您可以在视频TAB页中预览此视频'
        step2 = '第二步：鼠标左键划取视频中的大致字幕范围'
        step3 = '第三步：测试连接后端解析api接口'

    class Button:
        select_video_path = '选择视频文件'
        select_subtitle_area = '选择字幕区域'
        test_connect_api = '测试连接API'
        extract_preparing = '请先完成前几步'
        extract_prepared = '准备就绪 开始提取'

    class Tab:
        video_tab = '视频演示'
        background_tab = '后台打印'
        thank_tab = '感谢作者'

    class Video:
        fps = None
        count = None
        height = None
        width = None
        opened_cv = None
        rect = None
        current_frame = None

    class Path:
        video = None
        sound = None


class LoadVideoPicture(QThread):
    def __init__(self, show_video_label, video_slider, subtittle_result_label):
        super().__init__()
        self.show_video_label = show_video_label
        self.video_slider = video_slider
        self.subtittle_result_label = subtittle_result_label
        self.busy = False
        self.value = None

    def set_value(self, value):
        self.value = value
        time.sleep(0.2)
        while self.busy:
            time.sleep(0.1)

    def show_video_by_count(self):
        value = self.value if isinstance(self.value, int) else self.value[0]
        SoftData.Video.opened_cv.set(cv2.CAP_PROP_POS_FRAMES, value)
        ret, frame = SoftData.Video.opened_cv.read()
        if ret:
            SoftData.Video.current_frame = frame
            resized_frame = cv2.resize(src=frame, dsize=(800, 600))
            show = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
            showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format_RGB888)
            self.show_video_label.setPixmap(QtGui.QPixmap.fromImage(showImage))
            if isinstance(self.value, int):
                self.video_slider.setValue(value)

    def run(self):
        while True:
            if self.busy:
                time.sleep(0.1)
            elif self.value is not None:
                self.busy = True
                self.show_video_by_count()
                self.busy = False
                self.value = None
            else:
                time.sleep(0.1)


class ExtractSubtitleThread(QThread):
    progress_signal = pyqtSignal(int)
    log_signal = pyqtSignal(str)
    change_video_frame_signal = pyqtSignal(int)

    def __init__(self, load_picture_thread: LoadVideoPicture):
        super().__init__()
        self.api_interface = ExtractSubtitleApi()
        self.load_picture_thread = load_picture_thread

    def get_current_sub_tittle_base64_img(self):
        rect_frame = SoftData.Video.current_frame[SoftData.Video.rect[1]:SoftData.Video.rect[3],
                     SoftData.Video.rect[0]:SoftData.Video.rect[2]]
        image = cv2.imencode('.jpg', rect_frame)[1]
        image_code = str(base64.b64encode(image))[2:-1]
        return image_code

    def run(self):
        save_result = SaveResult()
        save_result.set_video_msg(SoftData.Path.video)
        # 1、视频人声和背景声音分离
        self.log_signal.emit('开始提取人声结果，可能等待较长时间......')
        result = self.api_interface.extract_human_voice_from_sound(SoftData.Path.sound)
        self.log_signal.emit('提取人声结果的容器内路径为 {}'.format(result))
        self.progress_signal.emit(30)
        # 2、识别声音停顿点
        self.log_signal.emit('开始提取人声说话时间点，稍等一会会就好...')
        result = self.api_interface.get_human_voice_time_point(result.get('file'))
        self.log_signal.emit('开始提取人声说话时间点结果为 {}'.format(result))
        self.progress_signal.emit(40)
        # 3、识别字幕
        length = len(result['result'])
        self.log_signal.emit('需要识别{}次'.format(length))
        for i, value in enumerate(result['result']):
            progress = 40 + int(60.0 * i / length)
            progress = 99 if progress > 99 else progress
            self.progress_signal.emit(progress)
            time_zhong = (value[1] + value[0]) / 2
            zheng = int(time_zhong / (1000 / SoftData.Video.fps))
            self.load_picture_thread.set_value(zheng)
            result = self.api_interface.text_recognition(self.get_current_sub_tittle_base64_img())
            self.log_signal.emit('{}'.format(value))
            self.log_signal.emit('{}'.format(result))
            text = ';'.join([value[1] for value in result])
            start_time = time.strftime("%H:%M:%S", time.gmtime(value[0] // 1000))
            start_time = start_time + '.{}'.format(value[0] % 1000)
            end_time = time.strftime("%H:%M:%S", time.gmtime(value[1] // 1000))
            end_time = end_time + '.{}'.format(value[1] % 1000)
            print(value, start_time, end_time)
            time_point = '{}-{}'.format(start_time, end_time)
            self.load_picture_thread.subtittle_result_label.setText('{}: {}'.format(time_point, text))
            text = '{}'.format(text)
            save_result.add_sub_tittle(start_time, end_time, text)
        else:
            self.progress_signal.emit(100)
            self.log_signal.emit('视频字幕提取成功')
            save_result.save_json()
            save_result.save_srt()


class MainUi(QDialog):
    process = QProcess()

    def __init__(self):
        super().__init__()
        self.setWindowTitle('视频硬字幕提取 https://github.com/m986883511/extract-video-subtittle')
        self.api_interface = ExtractSubtitleApi()
        self.init_ui()
        self.video_capture = None
        self.video_file_path = ''
        self.output_voice_path = os.path.abspath(os.path.join(current_dir, 'temp', 'extract.mp3'))
        self.temp_path = os.path.abspath(os.path.join(current_dir, 'temp'))
        self.human_voice_file = os.path.abspath(os.path.join(self.temp_path, 'extract', 'vocals.wav'))
        self.voice_path = os.path.abspath(os.path.join(self.temp_path, 'voice'))
        self.process.finished.connect(self.process_finished)
        self.process.readyReadStandardError.connect(self.update_stderr)
        self.process.readyReadStandardOutput.connect(self.update_stdout)
        os.makedirs(os.path.join(current_dir, 'temp'), exist_ok=True)
        self.show_video_label_thread = LoadVideoPicture(self.show_video_label,
                                                        self.video_slider,
                                                        self.subtittle_result_label)
        self.extract_thread = ExtractSubtitleThread(self.show_video_label_thread)
        self.extract_thread.progress_signal.connect(self.update_progress_bar)
        self.extract_thread.log_signal.connect(self.add_log)
        self.extract_thread.change_video_frame_signal.connect(self.show_video_by_count)

    def get_video_widget_tab(self):
        video_widget_tab = QWidget()
        layout = QVBoxLayout()
        self.show_video_label = PaintRectLabel('选择视频文件之后才会显示')
        self.show_video_label.mouse_release_signal.connect(self.select_subttle_area_complete)
        self.show_video_label.setScaledContents(True)
        self.video_slider = QSlider(Qt.Horizontal)  # 水平（左右拖动）
        self.video_slider.setMinimum(0)
        self.video_slider.setValue(0)
        self.video_slider.valueChanged.connect(self.show_video_by_count)
        self.subtittle_result_label = QLineEdit()
        self.subtittle_result_label.setEnabled(False)
        self.subtittle_result_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.show_video_label)
        layout.addWidget(self.subtittle_result_label)
        layout.addWidget(self.video_slider)
        video_widget_tab.setLayout(layout)
        return video_widget_tab, '视频演示'

    def get_background_print_tab(self):
        background_print_tab = QWidget()
        layout = QVBoxLayout()
        self.background_print_textedit = QTextEdit()
        layout.addWidget(self.background_print_textedit)
        background_print_tab.setLayout(layout)
        return background_print_tab, '后台打印'

    def get_thank_author_tab(self):
        thank_author_tab = QWidget()
        layout = QHBoxLayout()
        self.thank_author_label = QLabel('软件觉得不错，可以打赏')
        self.thank_author_picture = QLabel()
        picture = os.path.join(current_dir, 'image', 'weixin.jpg')
        self.thank_author_picture.setScaledContents(True)
        self.thank_author_picture.setPixmap(QPixmap(picture))
        layout.addWidget(self.thank_author_label)
        layout.addWidget(self.thank_author_picture)
        thank_author_tab.setLayout(layout)
        return thank_author_tab, '感谢作者'

    def init_ui(self):
        self.setMinimumWidth(1000)
        self.setMinimumHeight(800)
        layout = QVBoxLayout()
        self.video_path_button = QPushButton(SoftData.Button.select_video_path)
        self.video_path_button.clicked.connect(self.open_dialog_select_video_file)
        self.video_path_lineedit = QLineEdit(SoftData.Step.step1)
        self.video_path_lineedit.setEnabled(False)
        self.select_subtitle_area_button = QPushButton(SoftData.Button.select_subtitle_area)
        self.select_subtitle_area_button.clicked.connect(self.set_subtitle_area)
        self.subtitle_area_lineedit = QLineEdit(SoftData.Step.step2)
        self.subtitle_area_lineedit.setEnabled(False)

        self.connect_api_button = QPushButton(SoftData.Button.test_connect_api)
        self.connect_api_button.clicked.connect(self.test_connect_api)
        self.connect_api_lineedit = QLineEdit(SoftData.Step.step3)
        self.connect_api_lineedit.setEnabled(False)

        self.extract_subtitle_button = QPushButton(SoftData.Button.extract_preparing)
        self.extract_subtitle_button.clicked.connect(self.start_extract)
        self.extract_progress = QtWidgets.QProgressBar()
        self.extract_progress.setValue(0)
        self.extract_progress.setFixedHeight(20)

        grid_layout = QGridLayout()
        grid_layout.addWidget(self.video_path_button, 0, 0)
        grid_layout.addWidget(self.video_path_lineedit, 0, 1, 1, 3)
        grid_layout.addWidget(self.select_subtitle_area_button, 1, 0)
        grid_layout.addWidget(self.subtitle_area_lineedit, 1, 1, 1, 3)
        grid_layout.addWidget(self.connect_api_button, 2, 0)
        grid_layout.addWidget(self.connect_api_lineedit, 2, 1, 1, 3)
        grid_layout.addWidget(self.extract_subtitle_button, 3, 0)
        grid_layout.addWidget(self.extract_progress, 3, 1, 1, 3)
        layout.addLayout(grid_layout)

        tab_widget = QTabWidget()
        tab_widget.addTab(*self.get_video_widget_tab())
        tab_widget.addTab(*self.get_background_print_tab())
        tab_widget.addTab(*self.get_thank_author_tab())
        layout.addWidget(tab_widget)
        self.setLayout(layout)

    def image_callback(self, image):  # 这里的image就是任务线程传回的图像数据,类型必须是已经定义好的数据类型
        self.show_video_label.setPixmap(QPixmap.fromImage(image))
        return None

    def select_subttle_area_complete(self, value):
        label_w, label_h = self.show_video_label.width(), self.show_video_label.height()
        rect_x0, rect_y0, rect_x1, rect_y1 = value
        x_b, y_b = SoftData.Video.width / label_w, SoftData.Video.height / label_h
        real_x0, real_x1 = int(rect_x0 * x_b), int(rect_x1 * x_b)
        real_y0, real_y1 = int(rect_y0 * y_b), int(rect_y1 * y_b)
        msg = '在真实视频分辨率下矩形范围为 A=({},{}) B=({},{})'.format(real_x0, real_y0, real_x1, real_y1)
        self.add_log(msg)
        SoftData.Video.rect = real_x0, real_y0, real_x1, real_y1
        self.subtitle_area_lineedit.setText(msg)

    def set_subtitle_area(self):
        self.show_video_label.enable_paint_rect_flag = True
        self.subtitle_area_lineedit.setText('开始')

    def start_extract(self):
        self.extract_video_sound()

    def __deal_with_process_output_string(self, input_str):
        str1 = bytearray(input_str)
        str1 = str1.decode('gbk').strip()
        if str1:
            self.add_log(str1)
            progress = get_extract_voice_progress(str1)
            if progress:
                progress = progress / 100 * 10
                self.update_progress_bar(progress)

    def test_connect_api(self):
        self.add_log('开始测试api接口是否连通')
        value = self.api_interface.detect_recognition_model()
        if isinstance(value, dict) and value.get('result') == 'load model success':
            msg = '文字识别API接口已连通:{}'.format(self.api_interface.base_url)
            self.add_log(msg)
            self.connect_api_lineedit.setText(msg)
            return
        msg = '无法连接文字识别API接口'
        self.add_log(msg)
        self.connect_api_lineedit.setText(msg)

    def update_progress_bar(self, progress):
        self.extract_progress.setValue(progress)

    def add_log(self, str1):
        self.background_print_textedit.append(str1)

    def open_video(self):
        video_path = self.video_path_lineedit.text()
        self.video_capture = cv2.VideoCapture(video_path)
        SoftData.Video.opened_cv = self.video_capture
        if self.video_capture and self.video_capture.isOpened():
            ret, frame = self.video_capture.read()
            if ret:
                self.add_log('成功打开视频 {}'.format(video_path))
                SoftData.Video.count = int(self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
                self.video_slider.setMaximum(SoftData.Video.count)
                SoftData.Video.height = self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
                SoftData.Video.width = self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH)
                SoftData.Video.fps = self.video_capture.get(cv2.CAP_PROP_FPS)
                # self.load_picture.
                self.show_video_label_thread.start()
                self.show_video_label_thread.value = 0

    def show_video_by_count(self, value):
        if not self.show_video_label_thread.busy:
            self.show_video_label_thread.value = [value]
        else:
            time.sleep(0.1)

    def open_dialog_select_video_file(self):
        video_file_path = QFileDialog.getOpenFileName(self, '选择文件')[0]
        SoftData.Path.video = video_file_path
        video_filename = os.path.split(video_file_path)[1]
        just_name = ''.join(video_filename.split('.')[:-1])
        SoftData.Path.sound = os.path.abspath(os.path.join(current_dir, 'temp', '{}.mp3'.format(just_name)))
        self.add_log('设置{}提取出的声音文件为 {}'.format(video_filename, SoftData.Path.sound))
        if video_file_path:
            self.video_path_lineedit.setText(video_file_path)
            self.open_video()
        else:
            self.video_path_lineedit.setText(SoftData.Step.step1)

    def update_stderr(self):
        str1 = self.process.readAllStandardError()
        self.__deal_with_process_output_string(str1)

    def update_stdout(self):
        str1 = self.process.readAllStandardOutput()
        self.__deal_with_process_output_string(str1)

    def add_string_text(self, str1):
        self.add_log(str1)

    def process_finished(self, exitCode, exitStatus):
        if exitCode != 0:
            self.log_signal.emit('Abnormal End, exitCode={}, existStatus={}'.format(exitCode, exitStatus))
            QMessageBox.critical(self, 'command exception', 'process existed abnormally',
                                 QMessageBox.Yes, QMessageBox.Yes)

        else:
            self.add_log('Normal End, exitCode={}, existStatus={}'.format(exitCode, exitStatus))
            self.extract_thread.start()

    def extract_video_sound(self):
        if os.path.isfile(SoftData.Path.sound):
            self.add_log('已经提取了声音文件 {}'.format(SoftData.Path.sound))
            self.update_progress_bar(10)
            self.extract_thread.start()
        else:
            cmd = "ffmpeg -i {} {} -y".format(SoftData.Path.video, SoftData.Path.sound)
            self.add_log(cmd)
            cmd_list = cmd.split(' ')
            self.process.start(cmd_list[0], cmd_list[1:])


def main():
    import cgitb

    cgitb.enable()
    app = QtWidgets.QApplication(sys.argv)
    gui = MainUi()
    gui.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
