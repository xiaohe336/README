#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import termios
import tty
import select
import time
from pymavlink import mavutil

# ================= ⚡️ 室内动力增强版 =================
CONN_STR = 'udpin:localhost:14540'
FREQ = 50.0            
DELAY = 1.0 / FREQ     

# 1. 力度参数 (范围 0-1000)
# 之前是 200/600 (太肉)，现在改为标准室内参数
STEP_XY = 500          # 前后左右力度 (中等速度)
STEP_Z_UP = 800        # 上升力度 (800 足够果断起飞)
STEP_Z_DOWN = 350      # 下降力度
STEP_YAW = 400         # 旋转速度

# 2. 响应速度 (0.0 ~ 1.0)
# 0.2 = 兼顾平滑和跟手，比之前的 0.08 快两倍多
SMOOTH_FACTOR = 0.20   
# ====================================================

def main():
    print(f"正在连接飞控: {CONN_STR} ...")
    try:
        master = mavutil.mavlink_connection(CONN_STR)
        master.wait_heartbeat(timeout=5)
        print(f"✅ 连接成功! System ID: {master.target_system}")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return

    # 初始化变量
    val_x, val_y, val_z, val_r = 0, 0, 500, 0
    curr_x, curr_y, curr_z, curr_r = 0, 0, 500, 0

    print("="*50)
    print("      ⚡️ PX4 动力增强控制器 ⚡️")
    print("="*50)
    print(" [ W / S ]  : 前进 / 后退")
    print(" [ A / D ]  : 左移 / 右移")
    print(" [ I / K ]  : 上升 / 下降 (按住 I 起飞)")
    print(" [ J / L ]  : 左旋 / 右旋")
    print("-" * 50)
    print(" [  T  ]    : 🟢 解锁 (Arm)")
    print(" [  P  ]    : 📍 切定点模式 (空中切换)")
    print(" [ Space ]  : 🛑 急停/重置")
    print(" [  Q  ]    : 🚪 退出")
    print("="*50)

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    
    try:
        tty.setraw(sys.stdin.fileno())
        last_print_time = time.time()

        while True:
            # 读取键盘
            rlist, _, _ = select.select([sys.stdin], [], [], 0.01)
            
            if rlist:
                key = sys.stdin.read(1).lower()
                
                if key == 'q': break
                elif key == 't': master.arducopter_arm()
                elif key == 'p':
                    master.mav.command_long_send(
                        master.target_system, master.target_component,
                        mavutil.mavlink.MAV_CMD_DO_SET_MODE, 0,
                        1, 4, 0, 0, 0, 0, 0)

                # 设定目标值
                elif key == 'w': val_x = STEP_XY
                elif key == 's': val_x = -STEP_XY
                elif key == 'a': val_y = -STEP_XY
                elif key == 'd': val_y = STEP_XY
                elif key == 'i': val_z = STEP_Z_UP   # 这里的 800 会让你飞起来
                elif key == 'k': val_z = STEP_Z_DOWN
                elif key == 'j': val_r = -STEP_YAW
                elif key == 'l': val_r = STEP_YAW
                elif key == ' ': 
                    val_x, val_y, val_z, val_r = 0, 0, 500, 0
            
            else:
                # 无按键回中
                val_x = 0
                val_y = 0
                val_r = 0
                val_z = 500

            # 平滑插值 (现在更快了)
            curr_x += (val_x - curr_x) * SMOOTH_FACTOR
            curr_y += (val_y - curr_y) * SMOOTH_FACTOR
            curr_z += (val_z - curr_z) * SMOOTH_FACTOR
            curr_r += (val_r - curr_r) * SMOOTH_FACTOR

            # 发送指令
            master.mav.manual_control_send(
                master.target_system,
                int(curr_x),
                int(curr_y),
                int(curr_z),
                int(curr_r),
                0
            )

            # 状态打印
            if time.time() - last_print_time > 0.2:
                status = f"\r⚡️ [BOOST] X:{int(curr_x):3} Y:{int(curr_y):3} Z:{int(curr_z):3} Yaw:{int(curr_r):3}  "
                sys.stdout.write(status)
                sys.stdout.flush()
                last_print_time = time.time()

            time.sleep(DELAY)

    except Exception as e:
        sys.stdout.write("\n")
        print(f"Error: {e}")

    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        print("\n\n已退出。")

if __name__ == "__main__":
    main()