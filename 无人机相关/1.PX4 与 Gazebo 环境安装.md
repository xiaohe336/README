# PX4 与 Gazebo 环境安装

* 安装 empy 依赖：`pip3 install empy==3.3.4`
* 克隆 PX4 源码：`git clone https://github.com/PX4/PX4-Autopilot.git --recursive`
* 进入目录：`cd PX4-Autopilot/`
* 更新子模块：`git submodule update --init --recursive`
* 运行 Ubuntu 环境Gazebo安装脚本：`bash ./PX4-Autopilot/Tools/setup/ubuntu.sh`
* 再次进入目录（如路径重置）：`cd PX4-Autopilot/`
* 检查当前源码分支的版本标签：`git describe --tags`
