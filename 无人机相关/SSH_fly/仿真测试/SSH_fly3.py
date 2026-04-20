#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import sys
import threading
from pymavlink import mavutil

# ================= 🔧 飞行配置 (模拟器版) =================
# 1. 修改连接地址：模拟器使用 UDP 端口 14540
CONN_STR = 'udpin:localhost:14540'  

# 2. 波特率在 UDP 模式下无效，保持原样即可，不影响
BAUD_RATE = 921600
# 目标高度 (NED坐标系，负数为上)
TARGET_ALT = -0.5  
# 悬停时间 (秒)
HOVER_TIME = 10    
# 🐌 爬升速度 (米/秒) - 设置得越小越慢！建议室内 0.1~0.3
ASCEND_SPEED = 0.2 
# =======================================================

# 全局变量
running = True
current_z = 0.0     # 当前发送给飞控的高度设定点 (从0开始)
start_climb = False # 是否开始爬升的标志

def send_setpoint(master):
    """
    后台线程：负责发送平滑的设定点
    """
    global current_z, running
    
    # 计算每次循环需要改变的高度步长
    # 频率 20Hz (0.05s)，速度 ASCEND_SPEED
    # 步长 = 速度 * 时间
    step_size = ASCEND_SPEED * 0.05 

    while running:
        # --- 平滑爬升逻辑 ---
        if start_climb:
            # 如果当前设定点还没达到目标高度 (注意 NED 坐标系，-0.5 小于 0)
            if current_z > TARGET_ALT:
                current_z -= step_size # 慢慢减小 z 值 (即慢慢升高)
                
                # 防止超调
                if current_z < TARGET_ALT:
                    current_z = TARGET_ALT
        else:
            # 如果还没下令起飞，这就死死锁在地面 (0米)
            current_z = 0.0

        # 发送设定点
        master.mav.set_position_target_local_ned_send(
            0, 
            master.target_system, master.target_component,
            mavutil.mavlink.MAV_FRAME_LOCAL_NED,
            0b110111111000, # 只控位置 (x,y,z)
            0, 0, current_z, # 这里的 z 是动态变化的！
            0, 0, 0, 
            0, 0, 0, 
            0, 0 
        )
        time.sleep(0.05) # 20Hz

def main():
    global running, start_climb
    print(f"🔌 正在连接 PX4: {CONN_STR} ...")
    try:
        master = mavutil.mavlink_connection(CONN_STR, baud=BAUD_RATE)
        master.wait_heartbeat(timeout=5)
        print("✅ 连接成功! 系统ID: {}".format(master.target_system))
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return

    # 1. 启动线程
    # 注意：此时 start_climb = False，所以发的是 z=0 (地面)，非常安全
    print("💓 启动 Setpoint 线程 (当前锁定在地面)...")
    t = threading.Thread(target=send_setpoint, args=(master,))
    t.start()
    
    time.sleep(1)

    print("\n[1/3] 🔄 切换 OFFBOARD 模式...")
    offboard_ok = False
    for i in range(5):
        master.mav.command_long_send(
            master.target_system, master.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
            1, 6, 0, 0, 0, 0, 0 
        )
        time.sleep(0.2)
        msg = master.recv_match(type='HEARTBEAT', blocking=True, timeout=0.5)
        if msg and (msg.custom_mode >> 16) & 6:
            print("✅ OFFBOARD 模式已激活！")
            offboard_ok = True
            break
        print(f"   >>> 尝试切换 ({i+1}/5)...")
    
    if not offboard_ok:
        print("❌ 切换失败。退出。")
        running = False
        t.join()
        return

    print("\n[2/3] 🔓 准备解锁 (电机即将旋转)...")
    time.sleep(1)
    
    # 解锁
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
        1, 0, 0, 0, 0, 0, 0
    )
    master.motors_armed_wait()
    print("🔥 电机已解锁！(目前仍在地面怠速)")

    # 2. 发出起飞指令，让线程开始增加高度
    print(f"\n🚀 启动平滑起飞逻辑 (速度: {ASCEND_SPEED} m/s)...")
    time.sleep(1) # 给用户 1秒 反应时间
    start_climb = True 

    # 3. 悬停监控
    try:
        print(f"\n[3/3] 🛸 正在缓慢上升至 {abs(TARGET_ALT)}m ...")
        
        # 估算上升所需时间
        ascent_time = abs(TARGET_ALT) / ASCEND_SPEED
        total_wait = int(ascent_time + HOVER_TIME)
        
        for i in range(total_wait):
            # 打印当前发给飞控的目标高度，让你心里有底
            print(f"   飞行中... 设定高度: {abs(current_z):.2f}m | 剩余时间: {total_wait - i}s")
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🚨 紧急中断！立即降落！")

    # 4. 降落
    print("\n🛬 任务结束，切换自动降落 (LAND模式)...")
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_LAND, 0,
        0, 0, 0, 0, 0, 0, 0
    )

    master.motors_disarmed_wait()
    print("✅ 降落完成，电机已上锁。")
    
    running = False
    t.join()

if __name__ == "__main__":
    main()

