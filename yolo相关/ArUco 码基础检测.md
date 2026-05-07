```markdown
# ArUco 码基础检测与位姿估计 (`aruco_detector.py`)

`aruco_detector.py` 是本项目中最基础的底层检测工具。它专门用于直接检测画面中的 ArUco 码，并在图像上标注出它们的边框、中心点和 ID。更重要的是，它能利用相机的内参和畸变系数，计算出每个 ArUco 码距离相机的实际距离、平移向量（XYZ）以及欧拉角（旋转角度）。

## 如何使用

确保你已经进入了项目目录：
```bash
cd /home/admin1/catkin_ws/src/apriltag_detection
```

你可以通过命令行参数运行此脚本，实现不同的检测需求：

### 1. 开启摄像头实时检测（最常用）
如果你想直接测试摄像头能否识别 ArUco 码并实时查看其 3D 坐标，请运行：
```bash
python3 aruco_detector.py -c
```
* **操作：** 按 `q` 键退出，按 `s` 键保存当前带有检测结果的画面。

### 2. 处理本地图片文件夹
如果你已经采集好了一批包含 ArUco 码的图片，需要批量检测它们的位姿数据，请运行：
```bash
python3 aruco_detector.py -i ./你的图片文件夹路径
```
* 如果需要将检测到的位姿数据保存为特定的 JSON 文件名，可以使用 `-o` 参数：
  ```bash
  python3 aruco_detector.py -i ./test_images -o results.json
  ```

### 3. 生成测试用的 ArUco 码图片
如果你需要打印一些 ArUco 码用于测试，可以通过此脚本生成：
```bash
python3 aruco_detector.py -g
```
* 默认会生成 `DICT_5X5_1000` 字典中的 ID 0 到 3 的四张标记图片。

## 关键参数说明

* `-a`, `--aruco_type`: 指定要检测的 ArUco 标记类型（默认为 `DICT_5X5_1000`）。
* `-m`, `--marker_length`: 标记的实际物理边长，单位为米（默认为 `0.075` 米，即 7.5 厘米）。**准确的物理尺寸对于计算距离和位姿至关重要。**

**注意：** 如果你的 ArUco 码实际尺寸不是 7.5cm，或者你想检测其他类型的字典，请在运行时带上参数，例如：
```bash
python3 aruco_detector.py -c -a DICT_4X4_50 -m 0.05
```
*(表示检测 4x4_50 字典，且标记边长为 5 厘米)*
```
