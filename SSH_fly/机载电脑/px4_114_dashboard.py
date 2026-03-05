#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import sys
import os
import math
from pymavlink import mavutil

# ================= 🔧 配置 =================
CONN_STR = '/dev/ttyACM0'
BAUD_RATE = 921600
# ==========================================

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"🔌 正在连接 PX4 v1.14 (RAD模式): {CONN_STR} ...")
    
    try:
        master = mavutil.mavlink_connection(CONN_STR, baud=BAUD_RATE)
        
        # ================= 核心修复：自动唤醒飞控 =================
        print("🔔 正在发送唤醒包 (伪装成地面站, 激活数据流)...")
        for _ in range(5):
            master.mav.heartbeat_send(
                mavutil.mavlink.MAV_TYPE_GCS,
                mavutil.mavlink.MAV_AUTOPILOT_INVALID,
                0, 0, 0
            )
            time.sleep(0.1)
        # ==========================================================

        master.wait_heartbeat(timeout=5)
        print("✅ 连接成功! 正在配置数据流...")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return

    # 强制请求消息
    msg_requests = [
        (106, 30), # OPTICAL_FLOW_RAD
        (132, 20), # DISTANCE_SENSOR
        (32,  10), # LOCAL_POSITION_NED
        (230, 5),  # ESTIMATOR_STATUS
    ]
    
    for mid, rate in msg_requests:
        master.mav.command_long_send(
            master.target_system, master.target_component,
            mavutil.mavlink.MAV_CMD_SET_MESSAGE_INTERVAL, 0,
            mid, int(1000000/rate), 0, 0, 0, 0, 0
        )

    print("\n🚀 监控已启动 (按 Ctrl+C 退出)")
    print("=" * 60)

    # 数据缓存
    data = {
        'rad_q': 0, 'int_x': 0, 'int_y': 0, 'int_time': 0,
        'dist': -1,
        'pos_x': 0, 'pos_y': 0, 'pos_z': 0, 'pos_valid': False,
        'ekf_flags': 0,
    }

    last_print = time.time()
    cnt_flow = 0
    total_msgs = 0 # 总消息计数器

    try:
        while True:
            # 增加 timeout，防止死锁
            msg = master.recv_match(blocking=True, timeout=0.05)
            
            if msg:
                total_msgs += 1
                mtype = msg.get_type()

                if mtype == 'OPTICAL_FLOW_RAD':
                    cnt_flow += 1
                    data['rad_q'] = msg.quality
                    data['int_x'] = msg.integrated_x
                    data['int_y'] = msg.integrated_y
                    data['int_time'] = msg.integration_time_us

                elif mtype == 'DISTANCE_SENSOR':
                    data['dist'] = msg.current_distance / 100.0
                
                elif mtype == 'LOCAL_POSITION_NED':
                    data['pos_x'] = msg.x
                    data['pos_y'] = msg.y
                    data['pos_z'] = msg.z
                    data['pos_valid'] = True
                
                elif mtype == 'ESTIMATOR_STATUS':
                    data['ekf_flags'] = msg.flags

            # --- 独立刷新逻辑 ---
            # 不管有没有收到消息，每 0.2 秒强制刷新一次屏幕
            if time.time() - last_print > 0.2:
                sys.stdout.write("\033[H\033[J") # 清屏
                
                dt = data['int_time'] / 1e6
                w_x = data['int_x'] / dt if dt > 0 else 0
                w_y = data['int_y'] / dt if dt > 0 else 0

                print(f"🚁 PX4 v1.14 RAD 专用仪表盘")
                print("=" * 60)
                print(f"📡 通信状态: 共收到 {total_msgs} 个数据包")
                
                print(f"\n📷 光流 (OPTICAL_FLOW_RAD):")
                q_str = f"{data['rad_q']}/255"
                if data['rad_q'] == 0: q_state = "🔴 无信号 (可能太暗/太低)"
                elif data['rad_q'] < 100: q_state = "🟡 信号弱"
                else: q_state = "🟢 信号强"
                
                print(f"   - 质量 : {q_str:<8} {q_state}")
                print(f"   - 积分 : X:{data['int_x']:.4f}   Y:{data['int_y']:.4f}")
                print(f"   - 速度 : X:{w_x:.2f} rad/s  Y:{w_y:.2f} rad/s")
                
                if cnt_flow == 0:
                    print("   ⚠️  尚未收到光流数据！")

                print(f"\n📏 测距 (DISTANCE_SENSOR):")
                dist_state = "🟢" if data['dist'] > 0.1 else "🔴 盲区"
                print(f"   - 高度 : {data['dist']:.2f} m  {dist_state}")

                print(f"\n🧠 EKF2 状态 (Flags: {bin(data['ekf_flags'])}):")
                att_ok = (data['ekf_flags'] & 1) > 0
                vel_ok = (data['ekf_flags'] & 2) > 0
                pos_ok = (data['ekf_flags'] & 8) > 0
                print(f"   - 姿态: {'✅' if att_ok else '❌'} | 速度(光流): {'✅' if vel_ok else '❌'} | 位置: {'✅' if pos_ok else '⏳'}")

                print(f"\n📍 位置 (Local Position):")
                if data['pos_valid']:
                    print(f"   X: {data['pos_x']:.2f} m | Y: {data['pos_y']:.2f} m | Z: {data['pos_z']:.2f} m")
                else:
                    print("   ⚠️  EKF 未输出位置")

                last_print = time.time()

    except KeyboardInterrupt:
        print("\n退出。")

if __name__ == "__main__":
    main()