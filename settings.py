class Settings:
    """存储游戏《外星⼈⼊侵》中所有设置的类"""
    def __init__(self):
        """初始化游戏的设置"""
        # 屏幕设置
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (230, 230, 230)

        # ⻜船的设置
        # self.ship_speed = 1.5
        self.ship_limit = 3

        # ⼦弹设置
        # self.bullet_speed = 2.5
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (60, 60, 60)
        self.bullets_allowed = 30

        # 外星人设置
        # self.alien_speed = 1.0
        self.fleet_drop_speed = 10

        # fleet_direction 为1表示向右运动，为-1表示为向左移动
        # self.fleet_direction = 1

        # 以什么速度加快游戏的节奏
        self.speedup_scale = 1.1
        # 外星⼈分数的提⾼速度
        self.score_scale = 1.5
        self.initialize_dynamic_settings()
    
    def initialize_dynamic_settings(self):
        """初始化随游戏进⾏⽽变化的设置"""
        self.ship_speed = 3.5
        self.bullet_speed = 2.5
        self.alien_speed = 1.0

        # fleet_direction 为 1 表⽰向右，为-1 表⽰向左
        self.fleet_direction = 1
        self.alien_points = 50

    def increase_speed(self):
        """提⾼速度设置的值"""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale
        self.alien_points = int(self.alien_points * self.score_scale)
       

