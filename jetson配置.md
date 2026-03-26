sudo docker run \
  -it \                                     # -i: 保持标准输入打开，-t: 分配一个伪终端（让你可以在终端里输入命令交互）
  --device=/dev/video0 \                    # 挂载摄像头设备：将宿主机的摄像头（通常是 /dev/video0）映射进容器，供 YOLO 实时检测使用
  --ipc=host \                              # 共享共享内存：使用宿主机的 IPC 命名空间，防止 PyTorch (DataLoader) 多进程加载数据时出现共享内存不足的报错
  --rm \                                    # 阅后即焚：容器退出后自动删除该容器实例，节省磁盘空间，保持环境整洁
  --runtime=nvidia \                        # 开启 GPU 加速：调用 NVIDIA 容器运行时，使容器能够使用 Jetson 上的 GPU 进行模型推理加速
  -v /home/admin1/yolo:/workspace/yolo \    # 目录映射：将宿主机（你的开发板）上的 /home/admin1/yolo 文件夹挂载到容器内的 /workspace/yolo，方便代码修改和模型文件的保存
  -w /workspace/yolo \                      # 设置工作目录：进入容器后，终端所在的默认路径直接就是 /workspace/yolo
  ultralytics/ultralytics:latest-jetson-jetpack6 # 指定镜像：使用专为安装了 JetPack 6 的 Jetson 设备打包的最新版 Ultralytics (YOLO) 官方镜像
