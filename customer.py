import numpy as np
import random

from layout import CANDY_SHELF_POINTS_PER_SHELF, REGISTER_POSITIONS, EXIT_POS, OBSTACLES, RETURN_BOX_POS, CHAIR_POSITIONS #CUP_BOARD

NUM_CUSTOMERS = 1
INITIAL_POSITION = np.array([40.0, 0.0])
QUEUE_SPACING = 0.8 # 基本の行列間隔
SPECIAL_QUEUE_SPACING = 6.0 # 1人目と2人目の間の特別な間隔
NORMAL_QUEUE_SPACING = 1.2 # それ以降の通常の間隔

WAIT_TIME_SHELF = 60  # 棚での待機時間
WAIT_TIME_REGISTER = 100 # レジでの待機時間
WAIT_TIME_GENERAL = 0 # その他の目的地での待機時間
WAIT_TIME_CHAIR = 500 # 座席での待機時間
CUSTOMER_SPEED = 3.5 #エージェントの希望速度
ARRIVAL_THRESHOLD = 0.5 # 目的地に到達したとみなす距離
QUEUE_ARRIVAL_THRESHOLD = 0.3 # 待ち行列の定位置に到達したとみなす距離
REPULSION_DISTANCE_CUSTOMER = 2.0 #エージェント同士の反発を始める距離
REPULSION_EXP_FACTOR_CUSTOMER = 1.0 #エージェント同士の反発力の減衰係数（小さいほど急に力が弱くなる）
REPULSION_DISTANCE_LINE_OBS = 2.0 #線に反発を感じ始める距離
REPULSION_EXP_FACTOR_LINE_OBS = 1.0 #線に対する反発力の減衰係数
REPULSION_DISTANCE_RECT_OBS = 10.0 #テーブルに反発を感じ始める距離
REPULSION_EXP_FACTOR_RECT_OBS = 20.0 #テーブルに対する反発力の減衰係数
COLLISION_VELOCITY_REDUCTION_FACTOR = 0.3
ROUTE_LINE_POINT_OFFSET = 0.5
r = 1

SHELF_QUEUE_ENTRY_POINTS = [
    np.array([3.0, 1]),
    np.array([3.0, 4]),
    np.array([3.0, 12])
]

REGISTER_QUEUE_DIRECTION_VEC = np.array([-1.0, 0.0])

class Customer:
    """顧客エージェントを表すクラス"""

    register_queues = {
        "register1": [],
        "register2": []
    }
    shelf_queues = {
        0: [],  # 棚0の待ち行列
        1: [],  # 棚1の待ち行列
        2: []   # 棚2の待ち行列
    }

    def __init__(self, start_pos, exit_pos, candy_shelf_points_per_shelf,
                 preferred_shelf_index=None, register1_pos=None, register2_pos=None):

        self.pos = np.array(start_pos, dtype=float)  # 現在位置
        self.vel = np.array([0.0, 0.0])  # 速度ベクトル
        self.current_dest_index = 0  # 目的地インデックス
        self.wait_time = 0  # 待機時間カウンタ
        self.completed_rounds = 0  # ラウンド完了回数

        self.preferred_shelf_index = preferred_shelf_index
        self.exit_pos = exit_pos
        self.speed = CUSTOMER_SPEED

        if preferred_shelf_index == 2: #棚2（インデックス2の棚） を好んでいる
            self.chosen_register = register2_pos
            self.register_name = "register2"
        else:
            self.chosen_register = register1_pos
            self.register_name = "register1" # デフォルト

        if isinstance(self.preferred_shelf_index, np.ndarray):
            self.preferred_shelf_index = self.preferred_shelf_index.item()

        chosen_shelf_points_range = CANDY_SHELF_POINTS_PER_SHELF[self.preferred_shelf_index]
        y_min = min(chosen_shelf_points_range[0][1], chosen_shelf_points_range[1][1])
        y_max = max(chosen_shelf_points_range[0][1], chosen_shelf_points_range[1][1])
        y_rand = random.uniform(y_min, y_max)
        self.chosen_point = np.array([chosen_shelf_points_range[0][0], y_rand])

        self.shelf_queue_entry_point = SHELF_QUEUE_ENTRY_POINTS[self.preferred_shelf_index]

        self.chosen_chair_pos = random.choice(CHAIR_POSITIONS)

        self.dest_list = self._build_route(
            start_pos=start_pos,
            chosen_point=self.chosen_point, # 棚の最終目標地点
            shelf_queue_entry_point=self.shelf_queue_entry_point, # 棚の行列開始地点
            register_pos=self.chosen_register,
            exit_pos=exit_pos,
            chosen_chair_pos=self.chosen_chair_pos,
            return_box_pos=RETURN_BOX_POS
        )

        try: #顧客が「棚の行列に並び始める位置」が、dest_list の何番目かを特定
            self.shelf_target_dest_index = next(
                i for i, dest in enumerate(self.dest_list)
                if isinstance(dest, np.ndarray) and np.array_equal(dest, self.shelf_queue_entry_point)
            )
        except StopIteration:
            self.shelf_target_dest_index = -1 
        
        if self.shelf_target_dest_index != -1:#棚に並ぶ必要あり
            Customer.shelf_queues[self.preferred_shelf_index].append(self)
            self.waiting_for_shelf = True
        else:
            self.waiting_for_shelf = False

        self.register_target_dest_index = len(self.dest_list) - 4
        
        
        if self.register_name in Customer.register_queues:
            Customer.register_queues[self.register_name].append(self)
        
        self.skip_wait_index = -1


    def _build_route(self, start_pos, chosen_point, shelf_queue_entry_point, register_pos, exit_pos, chosen_chair_pos, return_box_pos): # 引数を追加,顧客が移動するルート（経路）を作成
        
        route = []

        def _random_pass_point(x_min, x_max, y_min, y_max):
            return np.array([
                np.random.uniform(x_min, x_max),
                np.random.uniform(y_min, y_max)
            ])

        def _make_line_point(from_pos, to_pos):
            direction = to_pos - from_pos
            norm = np.linalg.norm(direction)
            if norm > ROUTE_LINE_POINT_OFFSET:
                return to_pos - (direction / norm) * ROUTE_LINE_POINT_OFFSET
            return to_pos.copy()

        if self.preferred_shelf_index == 0:
            pass_point1 = _random_pass_point(25, 33, 0.5, 2.5)
            pass_point2 = np.array([7.0, 6.0])
            pass_point3 = np.array([40.0, 5.0])
            pass_point4 = np.array([30.0, 15.0])
            route.extend([
                pass_point1, 
                shelf_queue_entry_point, 
                chosen_point, 
                pass_point2, 
                register_pos,
                pass_point3,
                chosen_chair_pos,
                pass_point4,
                return_box_pos
            ])
        elif self.preferred_shelf_index == 1:
            pass_point1 = _random_pass_point(25, 33, 3.5, 5.5)
            pass_point2 = np.array([7.0, 6.0])
            pass_point3 = np.array([40.0, 5.0])
            pass_point4 = np.array([30.0, 15.0])
            route.extend([
                pass_point1, 
                shelf_queue_entry_point, 
                chosen_point, 
                pass_point2, 
                register_pos, 
                pass_point3,
                chosen_chair_pos,
                pass_point4,
                return_box_pos
            ])
        elif self.preferred_shelf_index == 2:
            pass_point1 = _random_pass_point(37, 41, 9, 10)
            pass_point2 = _random_pass_point(28.5, 30, 11.5, 13.5)
            pass_point3 = np.array([30.0, 15.0])
            pass_point4 = np.array([30.0, 15.0])
            route.extend([
                pass_point1,
                pass_point2,
                shelf_queue_entry_point,
                chosen_point,
                register_pos,
                pass_point3,
                chosen_chair_pos,
                pass_point4,
                return_box_pos
            ])
            
        else:
            route.extend([shelf_queue_entry_point, chosen_point, register_pos, chosen_chair_pos, return_box_pos])


        route.append(exit_pos)
        return route

    def current_goal(self):
        if self.current_dest_index >= len(self.dest_list):
            return None
        return self.dest_list[self.current_dest_index]

    def _compute_repulsive_force(self, others, obstacles_data):
  
        F_rep = np.zeros(2)

        # 他の顧客からの反発力
        for other in others:
            if other is self:
                continue
            diff = self.pos - other.pos
            dist = np.linalg.norm(diff)
            if 0 < dist < REPULSION_DISTANCE_CUSTOMER:
                F_rep += 8.0 * (diff / dist) * np.exp(-dist / REPULSION_EXP_FACTOR_CUSTOMER) 

        # 障害物に対する反発力
        for obs in obstacles_data:
            if obs.get("type") == "line":
                a, b = obs["start"], obs["end"]
                ab = b - a # 線分ベクトル
                ap = self.pos - a # 始点からposへのベクトル
                t = np.clip(np.dot(ap, ab) / np.dot(ab, ab), 0.0, 1.0)
                closest = a + t * ab # 線分上の最近接点
                diff = self.pos - closest
                dist = np.linalg.norm(diff)
                if 0 < dist < REPULSION_DISTANCE_LINE_OBS:
                    F_rep += (diff / dist) * np.exp(-dist / REPULSION_EXP_FACTOR_LINE_OBS)

            elif obs.get("type") == "rect":
                center = obs["pos"] + np.array([obs["width"]/2, obs["height"]/2])
                diff = self.pos - center
                dist = np.linalg.norm(diff)
                if 0 < dist < REPULSION_DISTANCE_RECT_OBS:
                    F_rep += (diff / dist) * np.exp(-dist / REPULSION_EXP_FACTOR_RECT_OBS)
        return F_rep

    def _is_collision(self, pos, obstacles_data):
      
        for obs in obstacles_data:
            if obs.get("type") == "rect":
                x, y = pos
                ox, oy = obs["pos"]
                w, h = obs["width"], obs["height"]
                if ox <= x <= ox + w and oy <= y <= oy + h:
                    return True
        return False

    def update(self, others, obstacles_data, delta_sec=0.04):

        if self.completed_rounds >= 1: # 1回出口に到達したらそれ以上は動かない
            return False

        goal = self.current_goal()
        if goal is None:
            self.completed_rounds += 1
            return False

        if self.current_dest_index == self.shelf_target_dest_index and self.waiting_for_shelf:
            queue = Customer.shelf_queues.get(self.preferred_shelf_index, [])
            idx_in_queue = queue.index(self) if self in queue else -1
           
            queue_direction_vec = np.array([1.0, 0.0])

        
            if idx_in_queue == 0:
                my_queue_offset = 0.0
            elif idx_in_queue == 1:
                my_queue_offset = SPECIAL_QUEUE_SPACING
            else:
                my_queue_offset = SPECIAL_QUEUE_SPACING + (idx_in_queue - 1) * NORMAL_QUEUE_SPACING
            
            my_queue_pos = self.shelf_queue_entry_point + queue_direction_vec * my_queue_offset
            dist_to_my_queue_pos = np.linalg.norm(self.pos - my_queue_pos)

            if dist_to_my_queue_pos < QUEUE_ARRIVAL_THRESHOLD:
                if idx_in_queue == 0:
                    if self.wait_time < WAIT_TIME_SHELF:
                        self.wait_time += 1
                        return True
                    else:
                        self.wait_time = 0
                        self.current_dest_index += 1
                        self.waiting_for_shelf = False
                        if self in queue:
                            queue.pop(0)
                        return True
                else:
                    return True
            else: 
                goal = my_queue_pos
        elif self.current_dest_index == self.register_target_dest_index:
            queue = Customer.register_queues.get(self.register_name, [])
            idx_in_queue = queue.index(self) if self in queue else -1
            
            my_queue_pos = goal + REGISTER_QUEUE_DIRECTION_VEC * (idx_in_queue * QUEUE_SPACING)
            dist_to_my_queue_pos = np.linalg.norm(self.pos - my_queue_pos)

            if dist_to_my_queue_pos < QUEUE_ARRIVAL_THRESHOLD: 
                if idx_in_queue == 0: # 先頭なら待機カウント後に進む
                    if self.wait_time < WAIT_TIME_REGISTER:
                        self.wait_time += 1
                        return True
                    else: # 待機終了後、行列から除外し次の目的地へ
                        self.wait_time = 0
                        self.current_dest_index += 1
                        if self in queue: # 念のためキューに存在するかチェック
                            queue.pop(0)
                        return True
                else: # 待機中（先頭ではないので）
                    return True
            else: # 順番待ち位置に移動
                goal = my_queue_pos # 待ち行列の自分の位置を目標とする

        elif np.array_equal(goal, self.chosen_chair_pos): #座席（椅子）での待機
            if self.wait_time < WAIT_TIME_CHAIR:
                self.wait_time += 1
                return True
            else:
                self.wait_time = 0
                self.current_dest_index += 1
                if self.current_dest_index >= len(self.dest_list):
                    self.completed_rounds += 1
                    return False
                return True

        elif np.linalg.norm(self.pos - goal) < ARRIVAL_THRESHOLD:
            if self.wait_time < WAIT_TIME_GENERAL: # WAIT_TIME_GENERAL が0なので、ここはスキップされる
                self.wait_time += 1
                return True
            else:
                self.wait_time = 0
                self.current_dest_index += 1
                if self.current_dest_index >= len(self.dest_list):
                    self.completed_rounds += 1
                    return False
                return True

        tau = 0.5 # 応答時間
        V0 = self.speed # 希望進行速度

        # 目標への方向と加速度を計算
        dist_vec = goal - self.pos
        dist_norm = np.linalg.norm(dist_vec)
        e = dist_vec / dist_norm if dist_norm > 0 else np.zeros_like(dist_vec)
        F_goal = (V0 * e - self.vel) / tau
        F_rep = self._compute_repulsive_force(others, obstacles_data)
        acc = F_goal + F_rep # 総加速度

        # 速度と位置を更新
        self.vel += acc * delta_sec
        new_pos = self.pos + self.vel * delta_sec

        if self._is_collision(new_pos, obstacles_data):
            self.vel *= COLLISION_VELOCITY_REDUCTION_FACTOR # 衝突時は速度を抑制
            self.pos = self.pos # 位置の更新をキャンセルし、元の位置に留まることでめり込みを防ぐ
            return True # 移動を継続 (次のフレームで反発力により押し戻されるのを待つ)

        def _ccw(a_ccw, b_ccw, c_ccw):
            return (c_ccw[1]-a_ccw[1]) * (b_ccw[0]-a_ccw[0]) > (b_ccw[1]-a_ccw[1]) * (c_ccw[0]-a_ccw[0])

        collided_with_line = False
        for obs in obstacles_data:
            if obs.get("type") == "line":
                a, b = obs["start"], obs["end"]
                # self.pos と new_pos を結ぶ線分が、障害物の線分 a-b と交差するか判定
                if _ccw(self.pos, a, b) != _ccw(new_pos, a, b) and _ccw(self.pos, new_pos, a) != _ccw(self.pos, new_pos, b):
                    self.vel *= COLLISION_VELOCITY_REDUCTION_FACTOR # 速度抑制

                    current_direction = self.vel / np.linalg.norm(self.vel) if np.linalg.norm(self.vel) > 0 else np.zeros_like(self.vel)
                    obs_direction = b - a
                    obs_direction_norm = np.linalg.norm(obs_direction)
                    obs_unit_direction = obs_direction / obs_direction_norm if obs_direction_norm > 0 else np.zeros_like(obs_direction)

                    tangential_speed = np.dot(self.vel, obs_unit_direction)
                    self.vel = tangential_speed * obs_unit_direction # 障害物に沿う速度成分のみ残す

                    new_pos = self.pos + self.vel * delta_sec # 調整された速度で新しい位置を計算
                    self.pos = new_pos # 位置を更新
                    collided_with_line = True
                    break

        if not collided_with_line:
            self.pos = new_pos
            
        return True
