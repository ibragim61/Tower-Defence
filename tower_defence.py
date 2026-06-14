import pygame
import math
import random

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
UI_PANEL_X = 850
UI_PANEL_WIDTH = 350
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 205, 50)
RED = (220, 20, 60)
BLUE = (65, 105, 225)
GRAY = (128, 128, 128)
BROWN = (139, 69, 19)
YELLOW = (255, 215, 0)
PURPLE = (147, 112, 219)
ORANGE = (255, 140, 0)
CYAN = (0, 255, 255)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tower Defence - Хардкор")
clock = pygame.time.Clock()

PATH = [
    (0, 400), (200, 400), (200, 600), (450, 600),
    (450, 650), (600, 650), (600, 550), (800, 550),
    (800, 250), (650, 250), (650, 400), (500, 400), (500, 350), (450, 350),
    (450, 250), (200, 250), (200, 550), (0, 550)
]

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 7)
        self.dx = math.cos(angle) * speed
        self.dy = math.sin(angle) * speed
        self.timer = random.randint(15, 30)
        self.color = color
        self.size = random.uniform(3, 6)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.timer -= 1
        self.size = max(0, self.size - 0.2)

    def draw(self, surface):
        if self.timer > 0 and self.size > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))

def draw_background(surface):
    for y in range(SCREEN_HEIGHT):
        t = y / SCREEN_HEIGHT
        r = int(120 * (1 - t) + 40 * t)
        g = int(200 * (1 - t) + 120 * t)
        b = int(255 * (1 - t) + 40 * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))

    pygame.draw.rect(surface, (45, 150, 45), (0, SCREEN_HEIGHT // 3, SCREEN_WIDTH, SCREEN_HEIGHT))

    tree_positions = [(100, 450), (500, 500), (700, 450), (300, 550), (600, 480), (150, 300), (750, 350)]
    for pos in tree_positions:
        shadow = pygame.Surface((50, 25), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 70), (0, 0, 50, 25))
        surface.blit(shadow, (pos[0]-25, pos[1]+5))
        
        pygame.draw.rect(surface, (100, 50, 20), (pos[0]-6, pos[1]-15, 12, 35))
        
        pygame.draw.circle(surface, (34, 139, 34), (pos[0], pos[1]-20), 25)
        pygame.draw.circle(surface, (50, 205, 50), (pos[0]-10, pos[1]-30), 20)
        pygame.draw.circle(surface, (50, 205, 50), (pos[0]+10, pos[1]-25), 18)

def draw_path(surface):
    for i in range(len(PATH) - 1):
        pygame.draw.line(surface, (60, 45, 25), PATH[i], PATH[i + 1], 56)
    for point in PATH:
        pygame.draw.circle(surface, (60, 45, 25), point, 28)

    for i in range(len(PATH) - 1):
        pygame.draw.line(surface, (130, 95, 55), PATH[i], PATH[i + 1], 50)
    for point in PATH:
        pygame.draw.circle(surface, (130, 95, 55), point, 25)

    for i in range(len(PATH) - 1):
        pygame.draw.line(surface, (160, 120, 75), PATH[i], PATH[i + 1], 20)
    for point in PATH:
        pygame.draw.circle(surface, (160, 120, 75), point, 10)

class GameState:
    def __init__(self):
        self.money = 250
        self.lives = 20
        self.score = 0
        self.wave = 1
        self.enemies_spawned = 0
        self.enemies_to_spawn = 5
        self.game_over = False
        self.wave_in_progress = False
        self.last_spawn_time = 0
        self.spawn_delay = 1000

    def add_money(self, amount):
        self.money += amount

    def spend_money(self, amount):
        if self.money >= amount:
            self.money -= amount
            return True
        return False

    def lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self.game_over = True

    def start_wave(self):
        if not self.wave_in_progress:
            self.wave_in_progress = True
            self.enemies_spawned = 0
            # Увеличиваем количество врагов в волне
            self.enemies_to_spawn = 5 + int(self.wave * 2.5) 
            # УСЛОЖНЕНИЕ: С каждой волной задержка между спавнами уменьшается (минимум 250мс)
            self.spawn_delay = max(250, 1000 - (self.wave - 1) * 80)
            return True
        return False

    def can_spawn_enemy(self):
        current_time = pygame.time.get_ticks()
        return (self.wave_in_progress and 
                self.enemies_spawned < self.enemies_to_spawn and
                current_time - self.last_spawn_time > self.spawn_delay)

    def enemy_spawned(self):
        self.enemies_spawned += 1
        self.last_spawn_time = pygame.time.get_ticks()

    def wave_cleared(self, enemies):
        if self.wave_in_progress and self.enemies_spawned >= self.enemies_to_spawn and len(enemies) == 0:
            self.wave_in_progress = False
            self.wave += 1
            self.money += 50
            return True
        return False

    def draw(self, surface):
        font = pygame.font.Font(None, 36)
        def draw_text(text, x, y, color):
            shadow = font.render(text, True, (0, 0, 0))
            main_text = font.render(text, True, color)
            surface.blit(shadow, (x+2, y+2))
            surface.blit(main_text, (x, y))

        draw_text(f"Деньги: {self.money}$", 20, 20, YELLOW)
        draw_text(f"Жизни: {self.lives}", 20, 60, RED)
        draw_text(f"Счёт: {self.score}", 20, 100, WHITE)
        draw_text(f"Волна: {self.wave}", 20, 140, CYAN)

        if self.wave_in_progress:
            draw_text(f"Врагов: {self.enemies_spawned}/{self.enemies_to_spawn}", 20, 180, WHITE)

class Enemy:
    def __init__(self, path, base_health, base_speed, base_reward, image_path, size, wave, color=RED):
        # --- СИСТЕМА УСЛОЖНЕНИЯ ---
        # +60% ХП за волну, +5% скорости, +15% награды
        health_mult = 1.0 + (wave - 1) * 0.60
        speed_mult = 1.0 + (wave - 1) * 0.05
        reward_mult = 1.0 + (wave - 1) * 0.15 
        
        self.path = path
        self.path_index = 0
        self.position = list(path[0])
        self.speed = base_speed * speed_mult
        self.health = int(base_health * health_mult)
        self.max_health = self.health
        self.alive = True
        self.reward = int(base_reward * reward_mult)
        self.size = size
        self.color = color
        
        try:
            self.image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(self.image, (size*2, size*2))
        except:
            self.image = None

    def move(self):
        if self.path_index < len(self.path) - 1:
            target = self.path[self.path_index + 1]
            dx = target[0] - self.position[0]
            dy = target[1] - self.position[1]
            distance = math.sqrt(dx*dx + dy*dy)

            if distance < self.speed:
                self.path_index += 1
            else:
                self.position[0] += (dx / distance) * self.speed
                self.position[1] += (dy / distance) * self.speed

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.alive = False
            return self.reward
        return 0

    def draw(self, surface):
        shadow_surface = pygame.Surface((self.size * 2 + 10, self.size + 5), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, 80), (0, 0, self.size * 2 + 10, self.size + 5))
        surface.blit(shadow_surface, (self.position[0] - self.size - 5, self.position[1] + self.size // 2 - 5))

        if self.image:
            image_rect = self.image.get_rect(center=(int(self.position[0]), int(self.position[1])))
            surface.blit(self.image, image_rect)
        else:
            pygame.draw.circle(surface, BLACK, (int(self.position[0]), int(self.position[1])), self.size + 2)
            pygame.draw.circle(surface, self.color, (int(self.position[0]), int(self.position[1])), self.size)
            pygame.draw.circle(surface, WHITE, (int(self.position[0]) - self.size//3, int(self.position[1]) - self.size//3), self.size//3)

        health_width = self.size * 2.5
        health_height = 6
        health_x = self.position[0] - health_width // 2
        health_y = self.position[1] - self.size - 12
        
        pygame.draw.rect(surface, (40, 40, 40), (health_x - 1, health_y - 1, health_width + 2, health_height + 2))
        
        health_ratio = max(0.0, self.health / self.max_health)
        r = min(255, max(0, int(255 * (1 - health_ratio) * 2)))
        g = min(255, max(0, int(255 * health_ratio * 2)))
        
        pygame.draw.rect(surface, (r, g, 0), (health_x, health_y, health_width * health_ratio, health_height))

    def reached_end(self):
        return self.path_index >= len(self.path) - 1

class BasicEnemy(Enemy):
    def __init__(self, path, wave):
        super().__init__(path, 120, 1.5, 15, 'images/basic.png', 20, wave, RED)
        if self.image:
            self.image = pygame.transform.flip(self.image, True, False)

class FastEnemy(Enemy):
    def __init__(self, path, wave):
        super().__init__(path, 70, 3.0, 25, 'images/fast.png', 16, wave, YELLOW)
        if self.image:
            self.image = pygame.transform.flip(self.image, True, False)

class TankEnemy(Enemy):
    def __init__(self, path, wave):
        super().__init__(path, 350, 0.8, 40, 'images/tank.png', 28, wave, GRAY)
        if self.image:
            w, h = self.image.get_size()
            self.image = pygame.transform.scale(self.image, (int(w * 1.4), h))
            self.image = pygame.transform.flip(self.image, True, False)

class BossEnemy(Enemy):
    def __init__(self, path, wave):
        super().__init__(path, 800, 1.0, 100, 'images/boss.png', 35, wave, PURPLE)

class Tower:
    def __init__(self, x, y, damage, range_radius, cooldown, cost, image_path, projectile_color, name):
        self.position = [x, y]
        self.damage = damage
        self.range = range_radius
        self.cooldown = cooldown
        self.cooldown_timer = 0
        self.cost = cost
        self.projectile_color = projectile_color
        self.name = name
        self.level = 1
        self.upgrade_cost = cost // 2
        self.color = projectile_color
        
        try:
            self.image = pygame.image.load(image_path)
            self.image = pygame.transform.scale(self.image, (70, 70))
        except:
            self.image = None

    def update(self, enemies):
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1
            return None

        closest_enemy = None
        closest_distance = float('inf')

        for enemy in enemies:
            if enemy.alive:
                dx = enemy.position[0] - self.position[0]
                dy = enemy.position[1] - self.position[1]
                distance = math.sqrt(dx*dx + dy*dy)

                if distance <= self.range and distance < closest_distance:
                    closest_enemy = enemy
                    closest_distance = distance

        if closest_enemy:
            self.cooldown_timer = self.cooldown
            return closest_enemy

        return None

    def upgrade(self):
        self.level += 1
        self.damage = int(self.damage * 1.5)
        self.range = int(self.range * 1.1)
        self.cooldown = max(5, self.cooldown - 2)
        self.upgrade_cost = int(self.upgrade_cost * 1.5)

    def draw(self, surface):
        pygame.draw.circle(surface, (0, 0, 0, 100), (int(self.position[0]) + 4, int(self.position[1]) + 4), 22)
        pygame.draw.circle(surface, (70, 70, 70), (int(self.position[0]), int(self.position[1])), 22)
        pygame.draw.circle(surface, (100, 100, 100), (int(self.position[0]), int(self.position[1])), 18)
        
        if self.image:
            image_rect = self.image.get_rect(center=(int(self.position[0]), int(self.position[1])))
            surface.blit(self.image, image_rect)
        else:
            pygame.draw.circle(surface, self.color, (int(self.position[0]), int(self.position[1])), 12)

        if hasattr(self, 'selected') and self.selected:
            range_surface = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA)
            pygame.draw.circle(range_surface, (*self.projectile_color, 40), (self.range, self.range), self.range)
            surface.blit(range_surface, (self.position[0] - self.range, self.position[1] - self.range))
            pygame.draw.circle(surface, self.projectile_color, (int(self.position[0]), int(self.position[1])), self.range, 2)

class BasicTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, 20, 150, 30, 100, 'images/basicTower.png', BLUE, "Базовая")

class SniperTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, 60, 300, 60, 200, 'images/sniper.png', PURPLE, "Снайпер")

class RapidTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, 10, 120, 10, 150, 'images/rapid.png', GREEN, "Пулемёт")

class CannonTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 180, 45, 250, 'images/cannon.png', ORANGE, "Пушка")

class Projectile:
    def __init__(self, start_pos, target_enemy, damage, speed, color):
        self.position = list(start_pos)
        self.target = target_enemy
        self.speed = speed
        self.damage = damage
        self.color = color
        self.alive = True

    def update(self, enemies):
        if not self.target.alive:
            self.alive = False
            return []

        dx = self.target.position[0] - self.position[0]
        dy = self.target.position[1] - self.position[1]
        distance = math.sqrt(dx*dx + dy*dy)

        if distance < self.speed:
            reward = self.target.take_damage(self.damage)
            self.alive = False
            if reward > 0:
                return [reward]
            return []
        else:
            self.position[0] += (dx / distance) * self.speed
            self.position[1] += (dy / distance) * self.speed
            return []

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.position[0]), int(self.position[1])), 8)
        pygame.draw.circle(surface, WHITE, (int(self.position[0]), int(self.position[1])), 4)

class Button:
    def __init__(self, x, y, width, height, text, color=GREEN, cost=0):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.cost = cost

    def draw(self, surface, game_state=None):
        mouse_pos = pygame.mouse.get_pos()
        is_wave_btn_disabled = (self.text == "Волна идёт...")
        
        enabled = game_state is None or (game_state.money >= self.cost and not is_wave_btn_disabled)
        
        if enabled and self.rect.collidepoint(mouse_pos):
            color = (min(self.color[0] + 40, 255), min(self.color[1] + 40, 255), min(self.color[2] + 40, 255))
        elif not enabled:
            color = (max(0, self.color[0] - 80), max(0, self.color[1] - 80), max(0, self.color[2] - 80))
        else:
            color = self.color
        
        shadow_rect = self.rect.copy()
        shadow_rect.y += 3
        pygame.draw.rect(surface, (20, 20, 20), shadow_rect, border_radius=8)
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=8)
        
        font = pygame.font.Font(None, 24)
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        if self.cost > 0:
            text_rect.y -= 8
            
        surface.blit(text_surface, text_rect)
        
        if self.cost > 0:
            cost_font = pygame.font.Font(None, 20)
            cost_text = cost_font.render(f"{self.cost}$", True, BLACK)
            cost_rect = cost_text.get_rect(center=(self.rect.centerx, self.rect.centery + 10))
            surface.blit(cost_text, cost_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def main():
    game_state = GameState()
    enemies = []
    towers = []
    projectiles = []
    particles = []

    buttons = [
        Button(UI_PANEL_X + 20, 40, UI_PANEL_WIDTH - 40, 45, "Начать волну", color=RED),
        Button(UI_PANEL_X + 20, 100, UI_PANEL_WIDTH - 40, 45, "Базовая башня", color=BLUE, cost=100),
        Button(UI_PANEL_X + 20, 160, UI_PANEL_WIDTH - 40, 45, "Снайперская", color=PURPLE, cost=200),
        Button(UI_PANEL_X + 20, 220, UI_PANEL_WIDTH - 40, 45, "Пулемёт", color=GREEN, cost=150),
        Button(UI_PANEL_X + 20, 280, UI_PANEL_WIDTH - 40, 45, "Пушка", color=ORANGE, cost=250),
        Button(UI_PANEL_X + 20, 340, UI_PANEL_WIDTH - 40, 45, "Улучшить", color=YELLOW, cost=50)
    ]

    grid_size = 50
    available_cells = []

    for x in range(0, 800, grid_size):
        for y in range(250, SCREEN_HEIGHT, grid_size):
            cell_center = (x + grid_size // 2, y + grid_size // 2)
            on_path = False
            
            exclusion_zone = int(grid_size * 0.95) 
            
            for i in range(len(PATH) - 1):
                p1 = PATH[i]
                p2 = PATH[i + 1]
                min_x, max_x = min(p1[0], p2[0]), max(p1[0], p2[0])
                min_y, max_y = min(p1[1], p2[1]), max(p1[1], p2[1])
                
                if (min_x - exclusion_zone <= cell_center[0] <= max_x + exclusion_zone and
                        min_y - exclusion_zone <= cell_center[1] <= max_y + exclusion_zone):
                    on_path = True
                    break
            
            if not on_path:
                available_cells.append(cell_center)

    selected_tower = None
    placing_tower = None
    tower_types = [BasicTower, SniperTower, RapidTower, CannonTower]

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and not game_state.game_over:
                mouse_pos = pygame.mouse.get_pos()

                for i, button in enumerate(buttons):
                    if button.is_clicked(mouse_pos):
                        if i == 0:
                            game_state.start_wave()
                        elif 1 <= i <= 4:
                            tower_class = tower_types[i-1]
                            if game_state.spend_money(button.cost):
                                placing_tower = tower_class
                        elif i == 5 and selected_tower:
                            if game_state.spend_money(selected_tower.upgrade_cost):
                                selected_tower.upgrade()

                if placing_tower:
                    min_distance = float('inf')
                    best_cell = None
                    for cell in available_cells:
                        distance = math.sqrt((mouse_pos[0] - cell[0])**2 + (mouse_pos[1] - cell[1])**2)
                        if distance < min_distance and distance < grid_size:
                            min_distance = distance
                            best_cell = cell
                    if best_cell:
                        new_tower = placing_tower(best_cell[0], best_cell[1])
                        towers.append(new_tower)
                        available_cells.remove(best_cell)
                        placing_tower = None
                else:
                    selected_tower = None
                    for tower in towers:
                        dx = mouse_pos[0] - tower.position[0]
                        dy = mouse_pos[1] - tower.position[1]
                        if math.sqrt(dx*dx + dy*dy) <= 35:
                            selected_tower = tower
                            tower.selected = True
                        else:
                            if hasattr(tower, 'selected'):
                                delattr(tower, 'selected')

        if game_state.wave_in_progress:
            buttons[0].text = "Волна идёт..."
            buttons[0].color = GRAY
        else:
            buttons[0].text = "Начать волну"
            buttons[0].color = RED

        if game_state.can_spawn_enemy():
            enemy_type = random.choices(
                [BasicEnemy, FastEnemy, TankEnemy, BossEnemy],
                weights=[0.5, 0.3, 0.15, 0.05], k=1)[0]
            # ПЕРЕДАЕМ НОМЕР ВОЛНЫ ПРИ СОЗДАНИИ ВРАГА
            enemies.append(enemy_type(PATH, game_state.wave))
            game_state.enemy_spawned()

        for enemy in enemies[:]:
            enemy.move()
            if enemy.reached_end():
                game_state.lose_life()
                enemies.remove(enemy)
            elif not enemy.alive:
                enemies.remove(enemy)

        for tower in towers:
            target = tower.update(enemies)
            if target:
                projectile = Projectile(tower.position, target, tower.damage, 10, tower.projectile_color)
                projectiles.append(projectile)

        for projectile in projectiles[:]:
            rewards = projectile.update(enemies)
            
            if rewards:
                game_state.add_money(sum(rewards))
                game_state.score += len(rewards)

            if not projectile.alive:
                if projectile.target:
                    for _ in range(12):
                        particles.append(Particle(projectile.position[0], projectile.position[1], projectile.color))
                projectiles.remove(projectile)

        if game_state.wave_cleared(enemies):
            print(f"Волна {game_state.wave-1} завершена!")

        draw_background(screen)
        draw_path(screen)

        for cell in available_cells:
            rect = (cell[0] - grid_size//2 + 4, cell[1] - grid_size//2 + 4, grid_size - 8, grid_size - 8)
            pygame.draw.rect(screen, (70, 180, 70), rect, 2, border_radius=6)
            pygame.draw.circle(screen, (70, 180, 70), cell, 3)

        for enemy in enemies:
            enemy.draw(screen)

        for tower in towers:
            tower.draw(screen)

        for projectile in projectiles:
            projectile.draw(screen)

        for p in particles[:]:
            p.update()
            p.draw(screen)
            if p.timer <= 0:
                particles.remove(p)

        pygame.draw.rect(screen, (30, 35, 45), (UI_PANEL_X, 0, UI_PANEL_WIDTH, SCREEN_HEIGHT))
        pygame.draw.rect(screen, (50, 60, 80), (UI_PANEL_X, 0, 5, SCREEN_HEIGHT)) 

        for button in buttons:
            button.draw(screen, game_state)

        if selected_tower:
            font = pygame.font.Font(None, 26)
            info_lines = [
                f"--- {selected_tower.name} ---",
                f"Уровень: {selected_tower.level}",
                f"Урон: {selected_tower.damage}",
                f"Радиус: {selected_tower.range}",
                f"Скорость: {selected_tower.cooldown}",
                f"Улучшение: {selected_tower.upgrade_cost}$"
            ]
            
            for i, line in enumerate(info_lines):
                text = font.render(line, True, WHITE)
                screen.blit(text, (UI_PANEL_X + 30, 420 + i * 35))

        game_state.draw(screen)

        if game_state.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            font = pygame.font.Font(None, 80)
            game_over_text = font.render("ИГРА ОКОНЧЕНА", True, RED)
            score_text = font.render(f"Итоговый счёт: {game_state.score}", True, WHITE)
            wave_text = font.render(f"Дойдено до волны: {game_state.wave}", True, WHITE)
            
            screen.blit(game_over_text, game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 60)))
            screen.blit(score_text, score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20)))
            screen.blit(wave_text, wave_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 70)))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()