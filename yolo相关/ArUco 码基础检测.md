# ArUco 码基础检测与位姿估计指引 (`aruco_detector.py`)

`aruco_detector.py` 是本项目中最核心的底层检测工具。它能够直接识别画面中的 ArUco 码，标注其边框、中心点和 ID，并利用相机内参计算其相对于相机的 **3D 位姿**（XYZ 平移与旋转角度）。

## 运行环境与路径
- **运行平台**: NVIDIA Jetson
- **工作目录**: `/home/admin1/catkin_ws/src/apriltag_detection`

---

## 核心使用方法

在运行前，请确保已进入工作目录：
```bash
cd /home/admin1/catkin_ws/src/apriltag_detection
```

### 1. 开启摄像头实时检测（最常用）
如果您想直接通过摄像头识别 ArUco 码并实时查看 3D 坐标，请运行：
```bash
python aruco_detector.py -c
```
* **实时操作**: 
    * 画面会实时显示检测到的 ID、距离以及 XYZ 坐标。
    * 按 **`q`** 键退出程序。
    * 按 **`s`** 键保存当前带有检测标注的画面快照。

### 2. 批量处理图片文件夹
如果您已采集了图片并需要提取其中的位姿数据，请运行：
```bash
python aruco_detector.py -i ./你的图片文件夹路径
```
* **导出数据**: 若要将检测到的位姿（位置、旋转、欧拉角等）保存到 JSON 文件，请添加 `-o` 参数：
  ```bash
  python aruco_detector.py -i ./images -o aruco_poses.json
  ```

### 3. 获取打印用的测试码
如果您需要制作物理测试标记，推荐直接访问在线生成器生成并打印：
* **在线工具地址**: [https://chev.me/arucogen/](https://chev.me/arucogen/)

---

##  关键参数配置

为了获得准确的定位结果，运行命令时可根据实际情况调整参数：

| 参数 | 完整指令 | 说明 | 默认值 |
| :--- | :--- | :--- | :--- |
| **`-m`** | `--marker_length` | **标记的实际物理边长** (单位: 米) | `0.075` (即 7.5cm) |
| **`-a`** | `--aruco_type` | **ArUco 标记的字典类型** | `DICT_5X5_1000` |

**示例命令（检测 5cm 边长的 4x4 标记）:**
```bash
python aruco_detector.py -c -m 0.05 -a DICT_4X4_50
```

---

## 🛠 相机参数说明
脚本目前使用了您提供的校准数据（分辨率 640x480）：
* **焦距 (fx, fy)**: `437.159, 437.261`
* **主点 (cx, cy)**: `314.694, 224.603`
* **畸变系数**: 已包含针对径向和切向畸变的补偿参数。
