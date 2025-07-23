import numpy as np
import matplotlib.patches as patches

# 定数として定義
SHELF_WIDTH = 3.0
SHELF_HEIGHT = 17.0
REGISTER_POSITIONS = np.array([[32, 8], [32, 9]])
EXIT_POS = np.array([50, 0])
RETURN_BOX_POS = np.array([17, 17])
WATER_SERVER_POS = np.array([23.5, 18])
TRASH_BOX_POS = np.array([48.5, 0.5])
COLLISION_OFFSET = 0.01 # 衝突とみなす最小距離

# 棚の定義（基準位置）
CANDY_SHELVES_BASE = [np.array([0, 0])]

# 各棚の顧客が目指すポイントを棚ごとにリストで定義
CANDY_SHELF_POINTS_PER_SHELF = [
    [np.array([3.0, 0.5]), np.array([3.0, 2.5])],  # 棚1の範囲（下部）
    [np.array([3.0, 3.5]), np.array([3.0, 5.5])],  # 棚2の範囲（中央）
    [np.array([3.0, 13.5]), np.array([3.0, 11.5])] # 棚3の範囲（上部）
]

# 店舗内の主要なオブジェクトの定義
SALAD_BAR = {"pos": np.array([12, 8], dtype=float), "width": 18, "height": 1, "type": "rect"}
#CUP_BOARD = {"pos": np.array([34, 7.75], dtype=float), "width": 2.5, "height": 1.5, "type": "rect"}

# 壁の定義（線分）
WALLS_LINE = [
    {"type": "line", "start": np.array([9, 3], dtype=float), "end": np.array([24, 3], dtype=float)},
    {"type": "line", "start": np.array([9, 6], dtype=float), "end": np.array([24, 6], dtype=float)},
    {"type": "line", "start": np.array([15, 11], dtype=float), "end": np.array([28, 11], dtype=float)},
    {"type": "line", "start": np.array([15, 14], dtype=float), "end": np.array([28, 14], dtype=float)},
    {"type": "line", "start": np.array([13, 16], dtype=float), "end": np.array([15, 14], dtype=float)}
]

# 空間の定義（矩形）
SPACES_RECT = [
    {"type": "rect", "pos": np.array([0, 17], dtype=float), "width": 23, "height": 13},
    {"type": "rect", "pos": np.array([45.5, 0], dtype=float), "width": 2, "height": 2},
    {"type": "rect", "pos": np.array([68, 0], dtype=float), "width": 2, "height": 2}
]

# テーブルの定義（矩形）
TABLES = [
    {"type": "rect", "pos": np.array([30, 28], dtype=float), "width": 9, "height": 2},
    {"type": "rect", "pos": np.array([42, 28], dtype=float), "width": 6, "height": 2},
    {"type": "rect", "pos": np.array([51, 28], dtype=float), "width": 15, "height": 2},
    {"type": "rect", "pos": np.array([68, 18], dtype=float), "width": 2, "height": 9},
    {"type": "rect", "pos": np.array([68, 4], dtype=float), "width": 2, "height": 6},
    {"type": "rect", "pos": np.array([52, 0], dtype=float), "width": 12, "height": 2},
    {"type": "rect", "pos": np.array([55, 23], dtype=float), "width": 9, "height": 2},
    {"type": "rect", "pos": np.array([44, 23], dtype=float), "width": 9, "height": 2},
    {"type": "rect", "pos": np.array([33, 23], dtype=float), "width": 9, "height": 2},
    {"type": "rect", "pos": np.array([55, 18], dtype=float), "width": 9, "height": 2},
    {"type": "rect", "pos": np.array([44, 18], dtype=float), "width": 9, "height": 2},
    {"type": "rect", "pos": np.array([36, 18], dtype=float), "width": 6, "height": 2},
    {"type": "rect", "pos": np.array([55, 4], dtype=float), "width": 9, "height": 2},
    {"type": "rect", "pos": np.array([50, 4], dtype=float), "width": 3, "height": 2},
    {"type": "rect", "pos": np.array([55, 8], dtype=float), "width": 9, "height": 2},
    {"type": "rect", "pos": np.array([44, 8], dtype=float), "width": 9, "height": 2}
]

# 障害物のリストを統合
OBSTACLES = [SALAD_BAR] + WALLS_LINE + SPACES_RECT + TABLES
#OBSTACLES = [SALAD_BAR, CUP_BOARD] + WALLS_LINE + SPACES_RECT + TABLES

# 座席の位置を格納するリスト
CHAIR_POSITIONS = []

# 座席の位置を定義 (chair_positionsも定数化)
CHAIR_CONFIG_1 = [
    {'y': 28, 'x_ranges': [np.linspace(31, 38, 6), np.linspace(43, 47, 4), np.linspace(52, 65, 10)]},
    {'y': 2, 'x_ranges': [np.linspace(52.5, 63.5, 8)]},
    {'x': 68, 'y_ranges': [np.linspace(4.5, 9.5, 4), np.linspace(18.5, 26.5, 6)]}
]

for config in CHAIR_CONFIG_1:
    if 'y' in config:
        for x_vals in config['x_ranges']:
            for x in x_vals:
                CHAIR_POSITIONS.append(np.array([x, config['y']]))
    elif 'x' in config:
        for y_vals in config['y_ranges']:
            for y in y_vals:
                CHAIR_POSITIONS.append(np.array([config['x'], y]))
                
CHAIR_CONFIG_2 = {
    (23, 25): [
        np.linspace(33.5, 41.5, 9),
        np.linspace(44.5, 52.5, 9),
        np.linspace(55.5, 63.5, 9)],
    (18, 20): [
        np.linspace(36.5, 41.5, 6),
        np.linspace(44.5, 52.5, 9),
        np.linspace(55.5, 63.5, 9)],
    (8, 10): [
        np.linspace(44.5, 52.5, 9),
        np.linspace(55.5, 63.5, 9)],
    (4, 6): [
        np.linspace(50.5, 52.5, 3),
        np.linspace(55.5, 63.5, 9)]
}

for ys, x_ranges in CHAIR_CONFIG_2.items():
    for y in ys:
        for x_vals in x_ranges:
            for x in x_vals:
                CHAIR_POSITIONS.append(np.array([x, y]))

SHELF_COLOR = {(0, 0): '#636AF2'} # 棚の色を指定 (タプルキーに修正)

def draw_tables(ax, tables_data):
    """テーブルを描画する関数"""
    for table in tables_data:
        rect = patches.Rectangle(
            table["pos"],
            table["width"],
            table["height"],
            edgecolor='black',
            facecolor='lightblue'
            )
        ax.add_patch(rect)

def draw_chairs(ax, chair_positions_data, radius=0.3, color='black'):
    """座席を描画する関数"""
    for pos in chair_positions_data:
        circle = patches.Circle(
            pos,
            radius=radius,
            facecolor=color,
            edgecolor='black',
            zorder=2
            )
        ax.add_patch(circle)

def do_segments_intersect(p1, p2, q1, q2):
    """線分の交差判定"""
    def ccw(a, b, c):
        return (c[1]-a[1]) * (b[0]-a[0]) > (b[1]-a[1]) * (c[0]-a[0])
    return ccw(p1, q1, q2) != ccw(p2, q1, q2) and ccw(p1, p2, q1) != ccw(p1, p2, q2)

def keep_out_of_obstacles(pos, prev_pos, obstacles_data):
    for obs in obstacles_data:
        if obs.get("type") == "line":
            a = obs["start"]
            b = obs["end"]
            ab = b - a
            ap = pos - a
            t = np.clip(np.dot(ap, ab) / np.dot(ab, ab), 0.0, 1.0)
            closest = a + t * ab
            dist = np.linalg.norm(pos - closest)
            if dist < COLLISION_OFFSET:
                return prev_pos # 衝突しているので前の位置に戻す
            
        else: # 矩形障害物
            x, y = pos
            ox, oy = obs["pos"]
            w, h = obs["width"], obs["height"]
            if ox - COLLISION_OFFSET <= x <= ox + w + COLLISION_OFFSET and oy - COLLISION_OFFSET <= y <= oy + h + COLLISION_OFFSET:
                return prev_pos
    return pos

def adjust_position_for_line_obstacles(prev_pos, new_pos, obstacles_data):
    for obs in obstacles_data:
        if obs.get("type") != "line":
            continue
        a, b = obs["start"], obs["end"]
        if do_segments_intersect(prev_pos, new_pos, a, b):
            return prev_pos
    return new_pos

def draw_shelves(ax, candy_shelves_data, shelf_color_map, width, height):
    for shelf in candy_shelves_data:
        color = shelf_color_map.get(tuple(shelf), 'sandybrown')
        rect = patches.Rectangle(
            shelf, width, height, linewidth=1,
            edgecolor='black', facecolor=color, alpha=0.8, zorder=1
        )
        ax.add_patch(rect)

def draw_customers_shelf_points(ax, customer_list):
    for c in customer_list:
        if hasattr(c, 'chosen_point'): # chosen_pointが存在するか確認
            ax.scatter(c.chosen_point[0], c.chosen_point[1], s=40, marker='o',
                       facecolors='white', edgecolors='black', linewidths=0.7, alpha=0.3, zorder=3)

def draw_registers(ax, register_positions_data):
    for reg in register_positions_data:
        ax.scatter(reg[0], reg[1], color='blue', s=130, marker='P', zorder=4)

def draw_entrance(ax, entrance_pos):
    ax.scatter(entrance_pos[0], entrance_pos[1], color='orange', s=130, marker='*', zorder=4)

def draw_exit(ax, exit_pos):
    ax.scatter(exit_pos[0], exit_pos[1], color='green', s=130, marker='*', zorder=4)

def draw_salad_bar(ax, salad_bar_data):
    rect = patches.Rectangle(
        salad_bar_data["pos"], salad_bar_data["width"], salad_bar_data["height"],
        linewidth=1, edgecolor='black', facecolor='sandybrown', alpha=0.8, zorder=1
    )
    ax.add_patch(rect)

#def draw_cup_board(ax, cup_board_data):
    #rect = patches.Rectangle(
        #cup_board_data["pos"], cup_board_data["width"], cup_board_data["height"],
        #linewidth=1, edgecolor='black', facecolor='sandybrown', alpha=0.8, zorder=1
    #)
    #ax.add_patch(rect)

def draw_return_box(ax, return_box_pos):
    ax.scatter(return_box_pos[0], return_box_pos[1], color='purple', s=130, marker='*', zorder=4)

def draw_water_server(ax, water_server_pos):
    ax.scatter(water_server_pos[0], water_server_pos[1], color='deepskyblue', s=130, marker='*', zorder=4)

def draw_trash_box(ax, trash_box_pos):
    ax.scatter(trash_box_pos[0], trash_box_pos[1], color='brown', s=130, marker='*', zorder=4)

def draw_walls(ax, obstacles_data):
    labeled = False
    for obs in obstacles_data:
        if obs.get("type") == "line":
            x_vals = [obs["start"][0], obs["end"][0]]
            y_vals = [obs["start"][1], obs["end"][1]]
            label = 'Wall' if not labeled else None
            ax.plot(x_vals, y_vals, color='black', linewidth=2, label=label, zorder=1)
            labeled = True
            
        elif obs.get("type") == "rect":
            label = 'Wall' if not labeled else None
            rect = patches.Rectangle(
                obs["pos"], obs["width"], obs["height"],
                linewidth=2, edgecolor='black', facecolor='dimgray', alpha=0.8,
                label=label, zorder=1
            )
            ax.add_patch(rect)
            labeled = True
