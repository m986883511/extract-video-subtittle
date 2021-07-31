import requests
import base64

with open('test.png', 'rb') as f:
    img = base64.b64encode(f.read()).decode()

res = {"image": [img]}
result = requests.post("http://127.0.0.1:6666/text_recognition", data=res)
print(result.json())
