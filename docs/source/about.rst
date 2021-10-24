项目简介
===========

提取视频硬字幕软件，能够将视频中的硬字幕提取出来，并生成srt字幕文件。

.. |date| date::
.. |time| date:: %H:%M

此文档构建时间 |date| at |time|.


程序原理
:::::::::::::::

..  csv-table:: 提取进度-原理对照
    :header: "总进度", "程序正在做什么事"
    :widths: 15, 30

    "0%-10%", "通过ffmpeg提取视频原声"
    "10%-30%", "利用spleeter提取视频原声中的人声"
    "30%-40%","利用pydub根据人声的停顿切分音频"
    "40%-99%","利用深度学习识别字幕"
    "100%","生成srt字幕文件"

项目优缺点
:::::::::::::::

..  csv-table:: 项目优缺点
    :header: "条目", "优点", "缺点"
    :widths: 15, 30, 30

    "部署难度", "提供容器集成升读学习环境，将以将后端部署在GPU服务器上面，速度极快","win无法利用GPU资源速度慢"
    "操作难度", "提供傻瓜式的界面前端","此前端只能在win上运行"
    "扩展性","容器提供api接口,可将后端部署在GPU服务器",""

视频演示
:::::::::::::::

https://www.bilibili.com/video/BV18Q4y1f774/

下载文件
:::::::::::::::

1. `前端界面release <https://github.com/m986883511/extract-video-subtittle/releases>`_
#. `后端容器 <https://hub.docker.com/repository/docker/m986883511/extract_subtitles>`_

