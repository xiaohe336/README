#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import math
from pymavlink import mavutil

# ================= 🐢 慢速配置区域 =================
CONN_STR = 'udpin:localhost:14540'
TARGET_ALT = -1.0      # 目标高度 (1米)
HOVER_TIME = 10.0      # 悬停时间
ROTATE_TIME = 12.0     # 旋转耗时 (12秒转90度，非常慢)
TARGET_ANGLE = 90.0    # 旋转角度
# =================================================

def main():
    print(f"正在连接飞控: {CONN_STR} ...")
    master = mavutil.mavlink_connection(CONN_STR)
    master.wait_heartbeat()
    print("✅ 连接成功!")

    # 定义掩码
    MASK_POS_ONLY = 0b110111111000      # 忽略 Yaw
    MASK_POS_WITH_YAW = 0b100111111000  # 启用 Yaw

    # 发送指令通用函数
    def send_cmd(x, y, z, yaw, mask):
        master.mav.set_position_target_local_ned_send(
            0, master.target_system, master.target_component,
            mavutil.mavlink.MAV_FRAME_LOCAL_NED,
            mask, x, y, z, 0, 0, 0, 0, 0, 0, yaw, 0
        )

    # 获取当前 Yaw 的函数 (用于无缝衔接)
    def get_current_yaw():
        # 尝试读取 ATTITUDE 消息，最多等待 1 秒
        msg = master.recv_match(type='ATTITUDE', blocking=True, timeout=1)
        if msg:
            return msg.yaw # 返回弧度
        return 0 # 如果读不到，默认返回0

    # 1. 预热
    print(">>> [1/6] 预热...")
    for _ in range(20):
        send_cmd(0, 0, 0, 0, MASK_POS_ONLY)
        time.sleep(0.05)

    # 2. 解锁 & Offboard
    print(">>> [2/6] 解锁 & 启动...")
    master.arducopter_arm()
    master.motors_armed_wait()
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
        1, 6, 0, 0, 0, 0, 0)

    # 3. 缓慢起飞
    print(f">>> [3/6] 缓慢起飞...")
    steps = 100
    for i in range(steps):
        curr_z = TARGET_ALT * (i / steps)
        send_cmd(0, 0, curr_z, 0, MASK_POS_ONLY)
        time.sleep(0.05)

    # 4. 悬停
    print(f">>> [4/6] 悬停 {HOVER_TIME} 秒...")
    start_time = time.time()
    while time.time() - start_time < HOVER_TIME:
        send_cmd(0, 0, TARGET_ALT, 0, MASK_POS_ONLY)
        time.sleep(0.05)

    # --- 关键步骤：读取当前朝向，防止顿挫 ---
    print(">>> 正在读取当前机头朝向...")
    current_actual_yaw = get_current_yaw()
    print(f"    当前 Yaw: {math.degrees(current_actual_yaw):.2f} 度")
    
    # 设定起始角度(就是当前角度) 和 结束角度(当前+90度)
    start_yaw_rad = current_actual_yaw
    end_yaw_rad = current_actual_yaw + math.radians(TARGET_ANGLE)

    # 5. 超慢速旋转
    print(f">>> [5/6] 开始极慢速旋转 (耗时 {ROTATE_TIME}s)...")
    rotate_steps = int(ROTATE_TIME * 20) # 20Hz

    for i in range(rotate_steps):
        # 线性插值
        progress = i / rotate_steps
        # 公式: 当前 = 起点 + (总路程 * 进度)
        target_yaw = start_yaw_rad + (end_yaw_rad - start_yaw_rad) * progress
        
        # 切换掩码，发送计算好的平滑角度
        send_cmd(0, 0, TARGET_ALT, target_yaw, MASK_POS_WITH_YAW)
        time.sleep(0.05)

    # 旋转结束，稳住姿态 3 秒
    print(">>> 旋转到位，保持...")
    for _ in range(60):
        send_cmd(0, 0, TARGET_ALT, end_yaw_rad, MASK_POS_WITH_YAW)
        time.sleep(0.05)

    # 6. 降落
    print(">>> [6/6] 降落...")
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_LAND, 0,
        0, 0, 0, 0, 0, 0, 0)
    
    print("✅ 演示结束")

if __name__ == "__main__":
    main()