# QGroundControl (QGC) 地面站安装与配置

* 将当前用户添加到 dialout 组以获取串口权限：`sudo usermod -a -G dialout $USER`
* 移除可能占用飞控串口的 modemmanager 服务：`sudo apt-get remove modemmanager -y`
* 安装 gstreamer 多媒体相关依赖：`sudo apt install gstreamer1.0-plugins-bad gstreamer1.0-libav gstreamer1.0-gl -y`
* 安装 libfuse2 依赖：`sudo apt install libfuse2 -y`
* 安装图形与其他系统依赖：`sudo apt install libxcb-xinerama0 libxkbcommon-x11-0 libxcb-cursor-dev -y`
* 赋予 AppImage 可执行权限：`chmod +x ./QGroundControl-x86_64.AppImage`
* 运行程序：`./QGroundControl-x86_64.AppImage`
