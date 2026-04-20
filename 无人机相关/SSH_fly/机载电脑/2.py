#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import sys
import threading
from pymavlink import mavutil

# ================= 🔧 飞行配置 (安全版) =================
CONN_STR = '/dev/ttyACM0'
BAUD_RATE = 921600

# 目标高度 (NED坐标系，负数为上)
TARGET_ALT = -0.5  
# 悬停时间 (秒)
HOVER_TIME = 10    
# 🐌 爬升速度 (米/秒) - 设置得越小越慢！建议室内 0.1~0.3
ASCEND_SPEED = 0.1
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
        
        # 唤醒飞控
        print("🔔 正在发送唤醒包 (伪装成地面站, 激活数据流)...")
        for _ in range(5):
            master.mav.heartbeat_send(
                mavutil.mavlink.MAV_TYPE_GCS,
                mavutil.mavlink.MAV_AUTOPILOT_INVALID,
                0, 0, 0
            )
            time.sleep(0.1)

        master.wait_heartbeat(timeout=5)
        print("✅ 连接成功! 系统ID: {}".format(master.target_system))
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return

    # 1. 启动线程 (锁定在地面)
    print("💓 启动 Setpoint 线程 (当前锁定在地面)...")
    t = threading.Thread(target=send_setpoint, args=(master,))
    t.start()
    time.sleep(1)

    # 2. 切换 OFFBOARD
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
        print("❌ 切换失败。请确认 EKF 位置已锁定 (绿灯闪烁)。")
        running = False
        t.join()
        return

    # 3. 解锁阶段 (带诊断窃听器)
    print("\n[2/3] 🔓 准备发送解锁指令...")
    time.sleep(1)
    
    # 清空之前的缓存消息，准备抓取报错
    while master.recv_match(blocking=False): pass
    
    # 发送解锁指令
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
        1, 0, 0, 0, 0, 0, 0
    )
    
    # 监听飞控的反馈 (最多等 5 秒)
    armed = False
    start_time = time.time()
    print("⏳ 等待飞控回应...")
    
    while time.time() - start_time < 5:
        # 监听文本消息、命令确认包和心跳包
        msg = master.recv_match(type=['STATUSTEXT', 'COMMAND_ACK', 'HEARTBEAT'], blocking=True, timeout=0.1)
        if msg:
            if msg.get_type() == 'STATUSTEXT':
                # 这就是飞控骂你的话！
                print(f"💬 飞控系统提示: {msg.text}") 
                
            elif msg.get_type() == 'COMMAND_ACK' and msg.command == mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM:
                if msg.result == 0:
                    print("✅ 飞控接受了解锁指令！")
                else:
                    print(f"❌ 飞控拒绝解锁！错误码 (Result): {msg.result}")
                    
            elif msg.get_type() == 'HEARTBEAT':
                # 检查心跳包里的解锁标志位
                if msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED:
                    armed = True
                    break

    # 如果没成功解锁，安全退出
    if not armed:
        print("\n🚨 解锁失败！请看上面的【飞控系统提示】找出原因。")
        print("💡 常见原因：插着USB没拔、没插电池、安全开关没按、传感器未校准。")
        running = False
        t.join()
        return

    # 4. 起飞爬升
    print("🔥 电机已解锁！(目前仍在地面怠速)")
    print(f"\n🚀 启动平滑起飞逻辑 (爬升速度: {ASCEND_SPEED} m/s)...")
    time.sleep(1) 
    start_climb = True 

    # 5. 悬停监控
    try:
        print(f"\n[3/3] 🛸 正在缓慢上升至 {abs(TARGET_ALT)}m ...")
        ascent_time = abs(TARGET_ALT) / ASCEND_SPEED
        total_wait = int(ascent_time + HOVER_TIME)
        
        for i in range(total_wait):
            print(f"   飞行中... 设定高度: {abs(current_z):.2f}m | 剩余时间: {total_wait - i}s")
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🚨 紧急中断！立即降落！")

    # 6. 降落
    print("\n🛬 任务结束，切换自动降落 (LAND模式)...")
    master.mav.command_long_send(
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_CMD_NAV_LAND, 0,
        0, 0, 0, 0, 0, 0, 0
    )

    # 等待彻底停转
    while running:
        msg = master.recv_match(type='HEARTBEAT', blocking=True, timeout=1)
        if msg and not (msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED):
            break
            
    print("✅ 降落完成，电机已上锁。")
    
    running = False
    t.join()

if __name__ == "__main__":
    main()