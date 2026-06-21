from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Line
import math

# Включаем горизонтальный полноэкранный режим
Window.fullscreen = 'auto'

class Kivy3DEngine(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # КАРТА ЛАБИРИНТА БЕЗ ЗАПЯТЫХ (1 - СТЕНА, 0 - ПУСТО)
        self.MAP = [
            "11111111",
            "10000001",
            "10110101",
            "10000101",
            "10111101",
            "10000001",
            "11111111"
        ]
        self.MAP_SIZE = 8
        self.TILE_SIZE = 50

        # Игрок
        self.player_x = 100.0
        self.player_y = 100.0
        self.player_angle = 0.0

        # Настройки 3D (Raycasting)
        self.FOV = math.pi / 3  
        self.HALF_FOV = self.FOV / 2
        self.NUM_RAYS = 65  
        self.MAX_DEPTH = 400
        self.DELTA_ANGLE = self.FOV / self.NUM_RAYS

        # Переменные тачскрина
        self.is_touching = False
        self.touch_x = 0
        self.touch_y = 0

        # Игровой цикл на 30 кадров в секунду
        Clock.schedule_interval(self.game_loop, 1.0 / 30.0)

    def on_touch_down(self, touch):
        self.is_touching = True
        self.touch_x, self.touch_y = touch.x, touch.y

    def on_touch_move(self, touch):
        self.touch_x, self.touch_y = touch.x, touch.y

    def on_touch_up(self, touch):
        self.is_touching = False

    def game_loop(self, dt):
        WIDTH = Window.width
        HEIGHT = Window.height
        SCALE = WIDTH // self.NUM_RAYS

        # --- СЕНСОРНОЕ УПРАВЛЕНИЕ ---
        move_speed = 3.5
        rot_speed = 0.05

        if self.is_touching:
            mx, my = self.touch_x, self.touch_y
            
            if mx < WIDTH / 2:
                # В Kivy координата Y=0 находится СНИЗУ экрана
                if my > HEIGHT / 2:
                    self.player_x += move_speed * math.cos(self.player_angle)
                    self.player_y += move_speed * math.sin(self.player_angle)
                else:
                    self.player_x -= move_speed * math.cos(self.player_angle)
                    self.player_y -= move_speed * math.sin(self.player_angle)
            else:
                if mx < (WIDTH / 2) + (WIDTH / 4):
                    self.player_angle -= rot_speed
                else:
                    self.player_angle += rot_speed

        # Коррекция положения (физика стен)
        self.player_x = max(self.TILE_SIZE + 5, min(self.player_x, (self.MAP_SIZE - 1) * self.TILE_SIZE - 5))
        self.player_y = max(self.TILE_SIZE + 5, min(self.player_y, (len(self.MAP) - 1) * self.TILE_SIZE - 5))

        # --- РЕНДЕРИНГ ГРАФИКИ ---
        self.canvas.clear()
        with self.canvas:
            # 1. Небо (верхняя половина)
            Color(30/255, 30/255, 30/255)
            Rectangle(pos=(0, HEIGHT / 2), size=(WIDTH, HEIGHT / 2))
            
            # 2. Земля (нижняя половина)
            Color(60/255, 60/255, 60/255)
            Rectangle(pos=(0, 0), size=(WIDTH, HEIGHT / 2))

            # 3. Отрисовка 3D-стен лучами
            start_angle = self.player_angle - self.HALF_FOV
            for ray in range(self.NUM_RAYS):
                for depth in range(1, self.MAX_DEPTH, 4): 
                    target_x = self.player_x + depth * math.cos(start_angle)
                    target_y = depth * math.sin(start_angle) + self.player_y
                    
                    col = int(target_x // self.TILE_SIZE)
                    row = int(target_y // self.TILE_SIZE)
                    
                    if 0 <= col < self.MAP_SIZE and 0 <= row < len(self.MAP):
                        # Считываем символ строки: '1' это стена
                        if self.MAP[row][col] == '1':
                            depth *= math.cos(self.player_angle - start_angle)
                            wall_height = min(int((self.TILE_SIZE * 300) / (depth + 0.0001)), HEIGHT)
                            
                            # Настройка яркости цвета
                            color_val = max(0.0, min(1.0, (180 - depth * 0.4) / 255.0))
                            
                            Color(color_val, color_val / 2, 0)
                            Rectangle(pos=(ray * SCALE, (HEIGHT - wall_height) / 2), size=(SCALE + 1, wall_height))
                            break
                start_angle += self.DELTA_ANGLE

            # 4. СТРЕЛОЧКИ И КНОПКИ НА ЭКРАНЕ
            Color(80/255, 80/255, 80/255)
            Line(points=[WIDTH / 2, 0, WIDTH / 2, HEIGHT], width=1)
            
            Color(200/255, 200/255, 200/255)
            # Вперед
            Line(points=[WIDTH // 4, HEIGHT - 40, WIDTH // 4 - 40, HEIGHT - 90, WIDTH // 4 + 40, HEIGHT - 90], close=True, width=2)
            # Назад
            Line(points=[WIDTH // 4, 40, WIDTH // 4 - 40, 90, WIDTH // 4 + 40, 90], close=True, width=2)
            
            Color(0, 130/255, 230/255)
            # Влево
            Line(points=[WIDTH // 2 + 70, HEIGHT // 2, WIDTH // 2 + 120, HEIGHT // 2 - 40, WIDTH // 2 + 120, HEIGHT // 2 + 40], close=True, width=2)
            # Вправо
            Line(points=[WIDTH - 70, HEIGHT // 2, WIDTH - 130, HEIGHT // 2 - 40, WIDTH - 130, HEIGHT // 2 + 40], close=True, width=2)

class GameApp(App):
    def build(self):
        return Kivy3DEngine()

if __name__ == '__main__':
    GameApp().run()
