import json
import os
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder


class ExtractSubtitleApi:
    """
    识别字幕接口类
    """
    ip = '127.0.0.1'
    port = '6666'
    debug = True

    def __init__(self):
        self.set_ip_port()
        self.headers = {'content-type': 'application/json'}
        self.print_flag = True

    def set_ip_port(self):
        try:
            with open(os.path.join(os.path.dirname(__file__), 'config.json')) as f:
                content = f.read()
            content = json.loads(content)
            self.ip = content['ip']
            self.port = content['port']
        except Exception as e:
            print('read config.json failed, err={}'.format(e))
            self.ip = ExtractSubtitleApi.ip
            self.port = ExtractSubtitleApi.port

    @property
    def base_url(self):
        return "http://{}:{}".format(self.ip, self.port)

    def detect_recognition_model(self):
        """
        加载深度模型

        Returns:
            dict: 成功或者失败
        """
        self.set_ip_port()
        url = '{}/load_model'.format(self.base_url)
        response = requests.get(url, headers=self.headers)
        return self.deal_with_response(response)

    def text_recognition(self, base64_img):
        """
        文字识别接口

        Args:
            base64_img (str): 转化为base64格式的图片

        Returns:
            dict: 图片中的坐标：文字
        """
        url = '{}/text_recognition'.format(self.base_url)
        data = {"image": [base64_img]}
        res = requests.post(url, data=data)
        return self.deal_with_response(res)

    def extract_human_voice_from_sound(self, local_mp3_filepath):
        """
        提取人声接口

        Args:
            local_mp3_filepath (str): 本地的视频原声mp3格式文件

        Returns:
            dict: 转化成功后的wav文件地址
        """
        url = '{}/extract_voice'.format(self.base_url)
        name = os.path.split(local_mp3_filepath)[1]
        multipart_encoder = MultipartEncoder(fields={
            'save_name': name,
            'save_data': (name, open(local_mp3_filepath, 'rb'), 'application/octet-stream')
        }
        )
        headers = {'Content-Type': multipart_encoder.content_type}
        res = requests.post(url, headers=headers, data=multipart_encoder)
        return self.deal_with_response(res)

    def get_human_voice_time_point(self, remote_wav_filename):
        """
        根据声音停顿返回有声音的区间段

        Args:
            remote_wav_filename (str): 远程的wav格式音频的绝对路径

        Returns:
            dict: 有声音的区间段列表
        """
        url = '{}/extract_time_point'.format(self.base_url)
        res = requests.get(url, headers=self.headers, json={'file': remote_wav_filename})
        return self.deal_with_response(res)

    @staticmethod
    def deal_with_response(res):
        if str(res.status_code)[0] == '2':
            return_value = res.json()
            if ExtractSubtitleApi.debug:
                print('url={}, result={}'.format(res.url, return_value))
            return return_value
        err_msg = 'status_code={}, url={}, content={}, text={}'.format(
            res.status_code, res.url, res.content, res.text)
        raise Exception(err_msg)


if __name__ == '__main__':
    a = ExtractSubtitleApi()
    result = a.detect_recognition_model()
