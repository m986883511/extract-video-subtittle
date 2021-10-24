# extract-video-subtittle
使用深度学习框架提取视频硬字幕；

本地识别无需联网；

CPU识别速度较慢，GPU识别很快；

容器提供API接口；

### 说明文档

https://extract-video-subtittle.readthedocs.io/


### 本项目缺少文件
因网速墙的问题，大文件推送不上去，可以参考.gitignore中写的


## 其他
视频提取
```shell
# 视频片段提取
ffmpeg -ss 00:15:45 -t 00:02:15 -i test/three_body_3_7.mp4 -vcodec copy -acodec copy test/3body.mp4
# 打包界面程序
C:/Python/Python38-32/Scripts/pyinstaller.exe main.spec

```

# 参考资料
本项目中深度学习源代码为/docker/backend

原作者为：https://github.com/YaoFANGUK/video-subtitle-extractor
