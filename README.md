# extract-video-subtittle
使用深度学习框架提取视频硬字幕





# 运行环境

本项目运行环境非常好搭建，我做好了docker容器免安装各种深度学习包

提供界面操作



## 视频演示

xxxx







## 运行后台

后端接口容器地址[Docker Hub](https://hub.docker.com/repository/docker/m986883511/extract_subtitles)

此过程可能时间较长，您需要预先安装好好docker，并配置好docker加速器

```shell
docker run -d -p 6666:6666 m986883511/extract_subtitles
```

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

# 深度学习后端
本项目中深度学习源代码为/docker/backend.tar

原作者为：https://github.com/YaoFANGUK/video-subtitle-extractor
