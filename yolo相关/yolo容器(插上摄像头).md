sudo docker run -it \
  --device=/dev/video0 \
  --ipc=host \
  --rm \
  --runtime=nvidia \
  -v /home/admin1/yolo:/workspace/yolo \
  -w /workspace/yolo \
  ultralytics/ultralytics:latest-jetson-jetpack6
