#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import math
from pymavlink import mavutil

# ================= 配置区域 =================
CONN_STR = 'udpin:localhost:14540'
ALTITUDE = -2.0     # 飞行高度 (NED坐标系，负数代表向上)
RADIUS = 2.0        # 圆的半径 (米)
SPEED = 0.05        # 画圆的角速度 (值越小越慢)
# ===========================================

def main():
    print(f"正在连接: {CONN_STR}")
    master = mavutil.mavlink_connection(CONN_STR)
    master.wait_heartbeat()
    print("✅ 连接成功! 等待位置估计初始化...")

    # --- 1. 辅助函数：发送位置设定点 (Setpoint) ---
    # Offboard 模式的核心：必须持续不断地发送这个消息
    def send_pos_target(x, y, z, yaw=0):
        master.mav.set_position_target_local_ned_send(
            0,                          # time_boot_ms
            master.target_system,       
            master.target_component,
            mavutil.mavlink.MAV_FRAME_LOCAL_NED, # 使用 NED 本地坐标系
            0b110111111000,             # type_mask: 只控制位置 (忽略速度加速度)
            x, y, z,                    # x, y, z (位置)
            0, 0, 0,                    # vx, vy, vz (速度，忽略)
            0, 0, 0,                    # afx, afy, afz (加速度，忽略)
            yaw, 0                      # yaw, yaw_rate
        )

    # --- 2. 准备阶段 ---
    # 在切换到 Offboard 模式前，必须先发送几十个设定点
    # 否则飞控会拒绝切换 (Failsafe)
    print(">>> 正在预热 Offboard 流...")
    for _ in range(20):
        send_pos_target(0, 0, 0) # 发送原地坐标
        time.sleep(0.05)

    # --- 3. 解锁与切模式 ---
    print(">>> 解锁 (Arming)...")
    master.arducopter_arm()
    master.motors_armed_wait()
    
    print(">>> 切换 Offboard 模式...")
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
        1, 6, 0, 0, 0, 0, 0) # 6 = Offboard

    # --- 4. 起飞阶段 (Takeoff) ---
    print(f">>> 起飞至 {abs(ALTITUDE)} 米高度...")
    for i in range(100):
        # 平滑上升，避免瞬间跳变
        current_z = 0 + (ALTITUDE - 0) * (i / 100)
        send_pos_target(0, 0, current_z)
        time.sleep(0.05)
    
    # 悬停 2 秒
    start_time = time.time()
    while time.time() - start_time < 2:
        send_pos_target(0, 0, ALTITUDE)
        time.sleep(0.05)

    # --- 5. 移动到圆周起点 ---
    print(f">>> 移动到圆周起点 (X={RADIUS})...")
    # 简单的线性插值移动
    steps = 50
    for i in range(steps):
        curr_x = RADIUS * (i / steps)
        send_pos_target(curr_x, 0, ALTITUDE)
        time.sleep(0.05)

    # --- 6. 画圆主逻辑 (Circle) ---
    print(">>> 开始画圆...")
    # 0 到 2*PI (一个完整的圆)
    angle = 0.0
    while angle <= 2 * math.pi:
        # 参数方程: x = R*cos(t), y = R*sin(t)
        # 注意: 这里我们让机头始终朝向圆心 (或者切线方向)，这里简化为固定朝向
        px = RADIUS * math.cos(angle)
        py = RADIUS * math.sin(angle)
        
        send_pos_target(px, py, ALTITUDE)
        
        angle += SPEED # 增加角度
        time.sleep(0.05) # 保持 20Hz 发送频率

    print(">>> 画圆完成!")

    # --- 7. 回到中心 ---
    print(">>> 回到中心...")
    for i in range(steps):
        # 此时飞机在 (RADIUS, 0)，需要慢慢回到 (0,0)
        curr_x = RADIUS * (1 - i / steps)
        send_pos_target(curr_x, 0, ALTITUDE)
        time.sleep(0.05)

    # --- 8. 自动降落 (Land) ---
    print(">>> 任务完成，切换自动降落 (AUTO.LAND)...")
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_LAND, 0,
        0, 0, 0, 0, 0, 0, 0)
    
    print("✅ 程序结束")

if __name__ == "__main__":
    main()