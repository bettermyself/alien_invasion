import sys
from time import sleep
import pygame
from settings import Settings
from game_stats import GameStats
from ship import Ship
from bullet import Bullet
from alien import Alien
from button import Button
from scoreboard import Scoreboard

class AlienInvasion:
    """管理游戏资源和⾏为的类"""

    def __init__(self):
        """初始化游戏并创建游戏资源"""
        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = Settings()
        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")
        # # 创建存储游戏统计信息的实例，并创建记分牌
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self._create_fleet()

        # 让游戏在⼀开始处于⾮活动状态
        self.game_active = False

        # 创建 Play 按钮
        self.play_botton = Button(self,'Play')

        # 设置背景色
        self.color = (230,230,230)
    

    def run_game(self):
        """开始游戏的主循环"""

        while True:
            # 侦听键盘和⿏标事件
            self._check_events()

            if self.game_active:
                # 更新飞船位置
                self.ship.update()

                # 更新子弹的位置
                self._update_bullets()

                # 更新外星舰队的位置
                self._update_aliens()

            # 每次循环都重绘屏幕
            self._update_screen()

            self.clock.tick(60)

    def _check_events(self):
        """响应按键和⿏标事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self,mouse_pos):
        """在玩家单击 Play 按钮时开始新游戏"""
        botton_clicked=self.play_botton.rect.collidepoint(mouse_pos)
        if botton_clicked and not self.game_active:
            # 还原游戏设置
            self.settings.initialize_dynamic_settings()
            # 重置游戏的统计信息
            self.stats.reset_stats()
            self.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            # 清空外星⼈列表和⼦弹列表
            self.bullets.empty()
            self.aliens.empty()

            # 创建⼀个新的外星舰队，并将⻜船放在屏幕底部的中央
            self._create_fleet()
            self.ship.center_ship()

            # 隐藏光标
            pygame.mouse.set_visible(False)


    def _check_keydown_events(self, event):
        """响应按下"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_UP:
            self.ship.moving_up = True
        elif event.key == pygame.K_DOWN:
            self.ship.moving_down = True

    def _check_keyup_events(self, event):
        """响应释放"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        elif event.key == pygame.K_UP:
            self.ship.moving_up = False
        elif event.key == pygame.K_DOWN:
            self.ship.moving_down = False


    def _fire_bullet(self):
        """创建⼀颗⼦弹，并将其加⼊编组 bullets """
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)


    def _update_bullets(self):
        """更新⼦弹的位置并删除已消失的⼦弹"""

        # 更新⼦弹的位置
        self.bullets.update()
        
        # 删除已消失的⼦弹
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()
        
    def _check_bullet_alien_collisions(self):
        """响应⼦弹和外星⼈的碰撞"""
        # 删除发⽣碰撞的⼦弹和外星⼈
        collisions = pygame.sprite.groupcollide(self.bullets,self.aliens,True,True)
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points*len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            # 删除现有的所有⼦弹，并创建⼀个新的外星舰队
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # 提⾼等级
            self.stats.level += 1
            self.sb.prep_level()

    def _ship_hit(self):
        """响应⻜船和外星⼈的碰撞"""
        if self.stats.ship_left >0:
            # 将 ships_left 减 1
            self.stats.ship_left -= 1
            self.sb.prep_ships()

            # 清空外星⼈列表和⼦弹列表
            self.bullets.empty()
            self.aliens.empty()

            # 创建⼀个新的外星舰队，并将⻜船放在屏幕底部的中央
            self._create_fleet()
            self.ship.center_ship()

            # 暂停
            sleep(0.5)
        else:
            self.game_active = False
            pygame.mouse.set_visible(True)

    def _check_aliens_bottom(self):
        """检查是否有外星⼈到达了屏幕的下边缘"""
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                # 像⻜船被撞到⼀样进⾏处理
                self._ship_hit()
                break

    def _update_aliens(self):
        """检查是否有外星⼈位于屏幕边缘，并更新整个外星舰队的位置"""
        self._check_fleet_edges()
        self.aliens.update()

        # 检测外星⼈和⻜船之间的碰撞
        if pygame.sprite.spritecollideany(self.ship,self.aliens):
           self._ship_hit()

        # 检查是否有外星⼈到达了屏幕的下边缘
        self._check_aliens_bottom()

    def _create_fleet(self):
        """创建一个外形舰队"""

        # 创建一个外星人，再不断添加，直到没有空间添加外星人为止
        # 外星人的间距为外星人的宽度和外星人的高度
        alien = Alien(self)
        alien_width,alien_height = alien.rect.size

        current_x ,current_y= alien_width, alien_height
        while current_y < (self.settings.screen_height -3*alien_height):
            while current_x < (self.settings.screen_width - 2*alien_width):
                self._create_aline(current_x,current_y)
                current_x += 2*alien_width
            # 添加一行外星人后，重置x值并递增y值
            current_x = alien_width
            current_y += 2*alien_height
            

    def _create_aline(self,x_position,y_position):
        """创建一个外星人并将其放在当前行中"""
        new_aline = Alien(self)
        new_aline.x = x_position
        new_aline.rect.x = x_position
        new_aline.rect.y = y_position
        self.aliens.add(new_aline)

    def _check_fleet_edges(self):
        """在有外星人到达边缘时采取相应的措施"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """将整个外星舰队向下移动，并改变它们的方向"""
        for aline in self.aliens.sprites():
            aline.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1
        


    def _update_screen(self):
        """更新屏幕上的图像，并切换到新屏幕"""
        self.screen.fill(self.settings.bg_color)
        
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        
        self.ship.blitme()

        self.aliens.draw(self.screen)

        # 显⽰得分
        self.sb.show_score()

        # 如果游戏处于⾮活动状态，就绘制 Play 按钮
        if not self.game_active:
            self.play_botton.draw_button()

        pygame.display.flip()

if __name__ == '__main__':
    # 创建游戏实例并运⾏游戏
    ai = AlienInvasion()
    ai.run_game()

