sudo docker run -it \                           # -i: 保持标准输入打开，-t: 分配伪终端 (允许交互)
  --device=/dev/video0 \                        # 挂载宿主机摄像头 (如 /dev/video0) 供 YOLO 实时检测使用
  --ipc=host \                                  # 使用宿主机共享内存，防止 DataLoader 多进程加载时报错
  --rm \                                        # 阅后即焚：退出后自动删除容器实例，保持环境整洁
  --runtime=nvidia \                            # 开启 GPU 加速：调用底层 NVIDIA 算力进行推理
  -v /home/admin1/yolo:/workspace/yolo \        # 目录映射：将宿主机代码映射到容器内，确保代码和模型持久化保存
  -w /workspace/yolo \                          # 工作目录：设置进入容器后的默认终端路径
  ultralytics/ultralytics:latest-jetson-jetpack6 # 指定镜像：使用专为 JetPack 6 打包的 YOLO 官方镜像
