import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random
from datetime import datetime, timedelta

from customer import Customer, INITIAL_POSITION, NUM_CUSTOMERS
from layout import (
    OBSTACLES, SALAD_BAR, #CUP_BOARD,
    TABLES, SHELF_COLOR, CHAIR_POSITIONS,
    CANDY_SHELVES_BASE, SHELF_WIDTH, SHELF_HEIGHT,
    CANDY_SHELF_POINTS_PER_SHELF,
    REGISTER_POSITIONS, EXIT_POS,
    RETURN_BOX_POS, WATER_SERVER_POS,
    TRASH_BOX_POS
)
import layout  # 描画関数用

ANIMATION_INTERVAL_MS = 50  # アニメーションの更新間隔（ミリ秒）
SIMULATION_STEPS = 10000    # シミュレーションの最大ステップ数
VIRTUAL_TIME_SCALE = 0.5    # 1フレームあたりの仮想時間の秒数

REGISTER1_POS = REGISTER_POSITIONS[0]
REGISTER2_POS = REGISTER_POSITIONS[1]

fig, ax = plt.subplots(figsize=(12, 6))
ax.set_xlim(0, 70)
ax.set_ylim(0, 30)
ax.grid(True)
ax.set_aspect('equal')

layout.draw_shelves(ax, CANDY_SHELVES_BASE, SHELF_COLOR, SHELF_WIDTH, SHELF_HEIGHT)
layout.draw_registers(ax, REGISTER_POSITIONS)
layout.draw_entrance(ax, INITIAL_POSITION)
layout.draw_exit(ax, EXIT_POS)
layout.draw_salad_bar(ax, SALAD_BAR)
#layout.draw_cup_board(ax, CUP_BOARD)
layout.draw_walls(ax, OBSTACLES)
layout.draw_return_box(ax, RETURN_BOX_POS)
layout.draw_water_server(ax, WATER_SERVER_POS)
layout.draw_trash_box(ax, TRASH_BOX_POS)
layout.draw_tables(ax, TABLES)
layout.draw_chairs(ax, CHAIR_POSITIONS)

customer_list = []
customer_points = []

try:
    df = pd.read_excel("Customer_Count.xlsx")
    # 時刻のフォーマットをH:Mに統一
    df['Time'] = df['Time'].astype(str).str.zfill(4).str.replace(r'(\d{2})(\d{2})', r'\1:\2', regex=True)
    df['Time'] = pd.to_datetime(df['Time'], format='%H:%M')
except FileNotFoundError:
    print("Error: Customer_Count.xlsx not found. Please make sure the file is in the same directory.")
    exit() # ファイルがない場合は終了

# 顧客入場スケジュール
entry_schedule = []
for _, row in df.iterrows():
    base_time = row['Time']
    count = row['Count']
    for _ in range(count):
        # -60秒〜+60秒でばらつかせる（中央値は0秒）
        random_second = random.triangular(-60, 60, 0)
        entry_time = base_time + timedelta(seconds=random_second)
        entry_schedule.append(entry_time)

entry_schedule.sort() # 入場時刻順にソート

# 仮想時間の開始
start_virtual_time = datetime.strptime("11:30", "%H:%M") # 11:30から開始

# 新規顧客追加関数
def add_customer():
    pshelf_index = random.randint(0, len(CANDY_SHELF_POINTS_PER_SHELF) - 1)
    
    c = Customer(
        start_pos=INITIAL_POSITION,
        exit_pos=EXIT_POS,
        register1_pos=REGISTER1_POS,
        register2_pos=REGISTER2_POS,
        candy_shelf_points_per_shelf=CANDY_SHELF_POINTS_PER_SHELF,
        preferred_shelf_index=pshelf_index
    )
    
    customer_list.append(c)

    color = np.random.rand(3,) # ランダムな色
    point, = ax.plot([], [], 'o', color=color, markersize=6)
    customer_points.append(point)
  
def init():
    """アニメーションフレームの初期化"""
    for point in customer_points:
        point.set_data([], [])
    layout.draw_customers_shelf_points(ax, customer_list)
    return customer_points

entry_index = 0

def update(frame):
   
    global entry_index
    still_moving = False

    # 仮想時間計算
    virtual_time = start_virtual_time + timedelta(seconds=frame * VIRTUAL_TIME_SCALE)
    ax.set_title(f"University Cafeteria Flow Model   Time: {virtual_time.strftime('%H:%M:%S')}")

    # 新規顧客の入場処理
    while entry_index < len(entry_schedule) and entry_schedule[entry_index] <= virtual_time:
        add_customer() # スケジュールに基づいて顧客を追加
        entry_index += 1

    # 既存顧客の状態更新と描画
    for i, c in enumerate(customer_list):
        # 顧客のupdateメソッドを呼び出し
        moving = c.update(customer_list, OBSTACLES)
        if moving:
            still_moving = True
        
        # 描画オブジェクトが存在する場合のみ更新
        if i < len(customer_points):
            pos = c.pos
            customer_points[i].set_data([pos[0]], [pos[1]])
         
    if not still_moving and entry_index >= len(entry_schedule):
        ani.event_source.stop()
        print("アニメーション停止")
        plt.close() # ウィンドウを閉じる

    return customer_points

ani = FuncAnimation(
    fig, update, frames=range(SIMULATION_STEPS),
    interval=ANIMATION_INTERVAL_MS, blit=False, init_func=init
)

plt.show()
