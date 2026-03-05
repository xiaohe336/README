QGroundControl (QGC) 地面站安装与配置1. 系统依赖与权限配置为了让 QGC 正常调用电脑的串口（连接飞控），以及正常渲染图形界面，需要先执行以下环境配置命令：# 将当前用户添加到 dialout 组以获取串口权限
sudo usermod -a -G dialout $USER

# 移除可能占用飞控串口的 modemmanager 服务
sudo apt-get remove modemmanager -y

# 安装多媒体与图形依赖库
sudo apt install gstreamer1.0-plugins-bad gstreamer1.0-libav gstreamer1.0-gl -y
sudo apt install libfuse2 -y
sudo apt install libxcb-xinerama0 libxkbcommon-x11-0 libxcb-cursor-dev -y
2. 赋予权限与运行 QGC确保你已经下载了 QGC 的 AppImage 文件（如 QGroundControl-x86_64.AppImage），进入该文件所在目录并执行：# 赋予 AppImage 可执行权限
chmod +x ./QGroundControl-x86_64.AppImage

# 运行程序
./QGroundControl-x86_64.AppImage
(提示：赋予权限后，也可以直接在系统文件管理器中双击该 AppImage 图标运行)
