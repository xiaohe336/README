# YOLO-Pose 模型训练指南

本文档介绍了如何使用准备好的数据集（`button13_Dataset`），通过执行 `train_pose.py` 脚本来训练 YOLO 关键点检测（Pose）模型。

## 1. 环境准备

在开始训练之前，请确保你已经安装了 Ultralytics 官方库（YOLOv8/YOLO11 的运行环境）：
```bash
pip install ultralytics
```

## 2. 脚本概览 (`train_pose.py`)

该脚本是模型训练的启动入口。它会自动读取之前数据流水线生成的 `data.yaml` 配置文件，并加载预训练权重开始迁移学习。

**核心训练参数说明：**

| 参数 | 设定值 | 说明 |
| :--- | :--- | :--- |
| `model` | `yolo26n-pose.pt` | 使用的预训练模型权重（请确保本地存在该文件或输入正确的官方版本名称如 `yolo11n-pose.pt`）。 |
| `data` | `/.../data.yaml` | 数据集配置文件的绝对路径。 |
| `epochs` | `300` | 总训练轮次。模型将遍历整个数据集 300 次。 |
| `batch` | `8` | 批次大小。设置为 8 适合显存有限的设备（如 Jetson 或普通笔记本）。 |
| `project` | `button` | 训练结果的主保存目录。 |
| `name` | `v1MuSGD_n_pose` | 本次训练实验的子文件夹名称，方便与后续的调参实验作区分。 |
| `optimizer` | `MuSGD` | 指定使用的优化器。 |

## 3. 启动训练

请在终端中运行以下命令开始训练：

```bash
cd /home/user/PycharmProjects/yolo
python3 train_pose.py
```

*💡 提示：训练 300 个 epoch 可能需要较长时间。在此期间，你可以随时按 `Ctrl+C` 中断训练，YOLO 会自动保存当前的进度，支持断点续传（通过传递 `resume=True` 参数）。*

## 4. 预期产出与结果查看

训练一旦开始，程序会自动在当前目录下创建一个 `button/v1MuSGD_n_pose/` 文件夹。

训练结束后，你可以在该目录中找到以下核心文件：
* **`weights/best.pt`**：**最重要的文件！** 这是整个训练过程中验证集精度最高的一组权重，后续在板子上部署或推理时，就用这个文件。
* **`weights/last.pt`**：最后一次 epoch 保存的权重（用于断点续训）。
* **`results.png`**：包含 Loss 下降曲线和关键点精度（mAP）提升曲线的可视化图表。
* **`val_batch0_pred.jpg`**：验证集上的预测效果预览图，可以直接点开看框和点标得准不准。

---

### 下一步：推理与部署
拿到 `best.pt` 后，你的模型就已经具备了识别按键面板 4 个关键点的能力。接下来即可将其部署到 Jetson 的摄像头节点中进行实时检测了！
