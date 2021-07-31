import os

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder


class ExtractSubtitleApi:
    ip = '127.0.0.1'
    port = '6666'
    debug = True

    def __init__(self):
        self.ip = ExtractSubtitleApi.ip
        self.port = ExtractSubtitleApi.port
        self.headers = {'content-type': 'application/json'}
        self.print_flag = True

    @property
    def base_url(self):
        return "http://{}:{}".format(self.ip, self.port)

    def text_recognition(self, base64_img):
        url = '{}/text_recognition'.format(self.base_url)
        data = {"image": [base64_img]}
        res = requests.post(url,  data=data)
        return self.deal_with_response(res)

    def extract_human_voice_from_sound(self, local_mp3_filepath):
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
        url = '{}/extract_time_point'.format(self.base_url)
        res = requests.get(url, headers=self.headers, json={'file': remote_wav_filename})
        return self.deal_with_response(res)

    def detect_recognition_model(self):
        url = '{}/load_model'.format(self.base_url)
        response = requests.get(url, headers=self.headers)
        return self.deal_with_response(response)

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
