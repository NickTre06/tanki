import pygame
import random
import math
import json
import os

# Инициализация Pygame
pygame.init()

# Настройки экрана
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Танчики")

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)

# Шрифты
font_small = pygame.font.SysFont(None, 36)
font_large = pygame.font.SysFont(None, 72)


class Tank:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 5
        self.angle = 0
        self.health = 100
        self.max_health = 100
        self.bullets = []
        self.rect = pygame.Rect(x - 20, y - 20, 40, 40)

    def draw(self, screen):
        # Корпус танка
        pygame.draw.rect(screen, GREEN, self.rect)

        # Дуло танка
        barrel_length = 30
        end_x = self.x + barrel_length * math.cos(math.radians(self.angle))
        end_y = self.y - barrel_length * math.sin(math.radians(self.angle))
        pygame.draw.line(screen, GREEN, (self.x, self.y), (end_x, end_y), 5)

        # Полоска здоровья
        health_bar_width = 40
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, RED, (self.x - 20, self.y - 30, health_bar_width, 5))
        pygame.draw.rect(screen, GREEN, (self.x - 20, self.y - 30, health_bar_width * health_ratio, 5))

    def move(self, keys, walls):
        new_x, new_y = self.x, self.y

        if keys[pygame.K_a]:
            new_x -= self.speed
        if keys[pygame.K_d]:
            new_x += self.speed
        if keys[pygame.K_w]:
            new_y -= self.speed
        if keys[pygame.K_s]:
            new_y += self.speed

        # Обновляем rect для проверки столкновений
        temp_rect = pygame.Rect(new_x - 20, new_y - 20, 40, 40)
        collision = False
        for wall in walls:
            if temp_rect.colliderect(wall.rect):
                collision = True
                break

        if not collision:
            self.x = max(20, min(WIDTH - 20, new_x))
            self.y = max(20, min(HEIGHT - 20, new_y))
            self.rect.x = self.x - 20
            self.rect.y = self.y - 20

    def rotate(self, mouse_pos):
        dx = mouse_pos[0] - self.x
        dy = self.y - mouse_pos[1]
        self.angle = math.degrees(math.atan2(dy, dx))

    def shoot(self):
        bullet_speed = 10
        bullet_x = self.x + 30 * math.cos(math.radians(self.angle))
        bullet_y = self.y - 30 * math.sin(math.radians(self.angle))
        self.bullets.append(Bullet(bullet_x, bullet_y, self.angle, bullet_speed, True))


class EnemyTank:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 2
        self.angle = 0
        self.health = 50
        self.bullets = []
        self.shoot_delay = 60
        self.shoot_timer = 0
        self.rect = pygame.Rect(x - 20, y - 20, 40, 40)

    def draw(self, screen):
        pygame.draw.rect(screen, RED, self.rect)

        barrel_length = 30
        end_x = self.x + barrel_length * math.cos(math.radians(self.angle))
        end_y = self.y - barrel_length * math.sin(math.radians(self.angle))
        pygame.draw.line(screen, RED, (self.x, self.y), (end_x, end_y), 5)

    def update(self, player_x, player_y, walls):
        # Поворот в сторону игрока
        dx = player_x - self.x
        dy = self.y - player_y
        self.angle = math.degrees(math.atan2(dy, dx))

        # Движение к игроку
        new_x = self.x + self.speed * math.cos(math.radians(self.angle))
        new_y = self.y - self.speed * math.sin(math.radians(self.angle))

        # Обновляем rect для проверки столкновений
        temp_rect = pygame.Rect(new_x - 20, new_y - 20, 40, 40)
        collision = False
        for wall in walls:
            if temp_rect.colliderect(wall.rect):
                collision = True
                break

        if not collision:
            self.x = new_x
            self.y = new_y
            self.rect.x = self.x - 20
            self.rect.y = self.y - 20

        # Стрельба
        self.shoot_timer += 1
        if self.shoot_timer >= self.shoot_delay:
            self.shoot()
            self.shoot_timer = 0

    def shoot(self):
        bullet_speed = 5
        bullet_x = self.x + 30 * math.cos(math.radians(self.angle))
        bullet_y = self.y - 30 * math.sin(math.radians(self.angle))
        self.bullets.append(Bullet(bullet_x, bullet_y, self.angle, bullet_speed, False))


class Bullet:
    def __init__(self, x, y, angle, speed, is_player):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.is_player = is_player
        self.rect = pygame.Rect(x - 5, y - 5, 10, 10)

    def update(self):
        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y -= self.speed * math.sin(math.radians(self.angle))
        self.rect.x = self.x - 5
        self.rect.y = self.y - 5

    def draw(self, screen):
        color = BLUE if self.is_player else RED
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 5)


class Wall:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, screen):
        pygame.draw.rect(screen, GRAY, self.rect)


class MedKit:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 15, y - 15, 30, 30)
        self.heal_amount = 25

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, self.rect)
        pygame.draw.line(screen, RED, (self.rect.x + 5, self.rect.y + 15), (self.rect.x + 25, self.rect.y + 15), 4)
        pygame.draw.line(screen, RED, (self.rect.x + 15, self.rect.y + 5), (self.rect.x + 15, self.rect.y + 25), 4)


def get_player_name():
    name = ""
    input_active = True
    while input_active:
        screen.fill(BLACK)
        title_text = font_large.render("Введите ваше имя:", True, WHITE)
        name_text = font_large.render(name, True, GREEN)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 50))
        screen.blit(name_text, (WIDTH // 2 - name_text.get_width() // 2, HEIGHT // 2 + 20))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    name += event.unicode
    return name


def save_stats(player_name, score):
    stats = []
    if os.path.exists("stats.json"):
        with open("stats.json", "r") as f:
            stats = json.load(f)

    stats.append({"name": player_name, "score": score})

    with open("stats.json", "w") as f:
        json.dump(stats, f)


def load_stats():
    if os.path.exists("stats.json"):
        with open("stats.json", "r") as f:
            return json.load(f)
    return []


def reset_stats():
    if os.path.exists("stats.json"):
        os.remove("stats.json")


def is_position_valid(x, y, objects, padding=50):
    test_rect = pygame.Rect(x - 25, y - 25, 50, 50)
    if x < 50 or x > WIDTH - 50 or y < 50 or y > HEIGHT - 50:
        return False
    for obj in objects:
        if hasattr(obj, 'rect'):
            if test_rect.colliderect(obj.rect):
                return False
    return True


def show_stats():
    stats = load_stats()
    stats.sort(key=lambda x: x["score"], reverse=True)
    showing = True
    while showing:
        screen.fill(BLACK)
        title_text = font_large.render("Топ игроков:", True, WHITE)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

        for i, stat in enumerate(stats[:5]):
            stat_text = font_small.render(f"{i + 1}. {stat['name']}: {stat['score']}", True, WHITE)
            screen.blit(stat_text, (WIDTH // 2 - stat_text.get_width() // 2, 150 + i * 40))

        back_text = font_small.render("Нажмите любую клавишу для возврата", True, WHITE)
        screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT - 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                showing = False


def show_menu():
    menu_active = True
    while menu_active:
        screen.fill(BLACK)
        title_text = font_large.render("ТАНЧИКИ", True, GREEN)
        start_text = font_small.render("1. Начать игру", True, WHITE)
        stats_text = font_small.render("2. Статистика", True, WHITE)
        reset_text = font_small.render("3. Сбросить статистику", True, WHITE)
        exit_text = font_small.render("4. Выход", True, WHITE)

        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))
        screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, 250))
        screen.blit(stats_text, (WIDTH // 2 - stats_text.get_width() // 2, 300))
        screen.blit(reset_text, (WIDTH // 2 - reset_text.get_width() // 2, 350))
        screen.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, 400))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "start"
                elif event.key == pygame.K_2:
                    show_stats()
                elif event.key == pygame.K_3:
                    reset_stats()
                elif event.key == pygame.K_4:
                    pygame.quit()
                    return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if 250 <= mouse_pos[1] <= 280:
                    return "start"
                elif 300 <= mouse_pos[1] <= 330:
                    show_stats()
                elif 350 <= mouse_pos[1] <= 380:
                    reset_stats()
                elif 400 <= mouse_pos[1] <= 430:
                    pygame.quit()
                    return None


def game_loop(player_name, current_round=1, total_score=0):
    # Настройки сложности
    round_settings = {
        1: {"enemies": 3, "enemy_speed": 2},
        2: {"enemies": 4, "enemy_speed": 2.2},
        3: {"enemies": 5, "enemy_speed": 2.5},
        4: {"enemies": 6, "enemy_speed": 2.7},
        5: {"enemies": 7, "enemy_speed": 3}
    }
    settings = round_settings.get(current_round, round_settings[5])

    # Инициализация игры
    clock = pygame.time.Clock()
    player = Tank(WIDTH // 2, HEIGHT // 2)

    # Создание объектов
    walls = [
        Wall(100, 100, 50, 200),
        Wall(300, 400, 200, 50),
        Wall(600, 200, 50, 300)
    ]

    medkits = [
        MedKit(150, 150),
        MedKit(450, 450),
        MedKit(700, 300)
    ]

    enemies = []
    for _ in range(settings["enemies"]):
        while True:
            x = random.randint(50, WIDTH - 50)
            y = random.randint(50, HEIGHT - 50)
            if is_position_valid(x, y, [player] + walls + medkits):
                enemy = EnemyTank(x, y)
                enemy.speed = settings["enemy_speed"]
                enemies.append(enemy)
                break

    running = True
    round_score = 0

    while running:
        screen.fill(BLACK)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                player.shoot()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_stats(player_name, total_score + round_score)
                    return True

        # Управление танком
        keys = pygame.key.get_pressed()
        player.move(keys, walls)
        player.rotate(pygame.mouse.get_pos())

        # Обновление пуль игрока
        for bullet in player.bullets[:]:
            bullet.update()

            # Удаление пуль за пределами экрана
            if (bullet.x < 0 or bullet.x > WIDTH or
                    bullet.y < 0 or bullet.y > HEIGHT):
                player.bullets.remove(bullet)
                continue

            # Проверка попадания во врагов
            for enemy in enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    enemy.health -= 25
                    if enemy.health <= 0:
                        enemies.remove(enemy)
                        round_score += 10
                    if bullet in player.bullets:
                        player.bullets.remove(bullet)
                    break

            # Проверка попадания в стены
            for wall in walls:
                if bullet.rect.colliderect(wall.rect):
                    if bullet in player.bullets:
                        player.bullets.remove(bullet)
                    break

        # Обновление врагов
        for enemy in enemies:
            enemy.update(player.x, player.y, walls)

            # Обновление пуль врагов
            for bullet in enemy.bullets[:]:
                bullet.update()

                # Удаление пуль за пределами экрана
                if (bullet.x < 0 or bullet.x > WIDTH or
                        bullet.y < 0 or bullet.y > HEIGHT):
                    enemy.bullets.remove(bullet)
                    continue

                # Проверка попадания в игрока
                if bullet.rect.colliderect(player.rect):
                    player.health -= 10
                    enemy.bullets.remove(bullet)

                # Проверка попадания в стены
                for wall in walls:
                    if bullet.rect.colliderect(wall.rect):
                        if bullet in enemy.bullets:
                            enemy.bullets.remove(bullet)
                        break

        # Проверка подбора аптечек
        for medkit in medkits[:]:
            if player.rect.colliderect(medkit.rect):
                player.health = min(player.max_health, player.health + medkit.heal_amount)
                medkits.remove(medkit)

        # Отрисовка
        for wall in walls:
            wall.draw(screen)

        for medkit in medkits:
            medkit.draw(screen)

        player.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)

        for bullet in player.bullets:
            bullet.draw(screen)

        for enemy in enemies:
            for bullet in enemy.bullets:
                bullet.draw(screen)

        # Отображение информации
        score_text = font_small.render(f"Очки: {round_score}", True, WHITE)
        total_text = font_small.render(f"Общий счет: {total_score + round_score}", True, WHITE)
        health_text = font_small.render(f"Здоровье: {player.health}", True, WHITE)
        name_text = font_small.render(f"Игрок: {player_name}", True, WHITE)
        round_text = font_small.render(f"Раунд: {current_round}/5", True, WHITE)

        screen.blit(score_text, (10, 10))
        screen.blit(total_text, (10, 50))
        screen.blit(health_text, (10, 90))
        screen.blit(name_text, (10, 130))
        screen.blit(round_text, (10, 170))

        # Проверка здоровья игрока
        if player.health <= 0:
            save_stats(player_name, total_score + round_score)
            game_over_text = font_large.render("Игра окончена!", True, RED)
            restart_text = font_small.render("Нажмите R для рестарта или ESC для выхода", True, WHITE)

            screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 50))
            pygame.display.flip()

            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            return game_loop(player_name, 1, 0)
                        if event.key == pygame.K_ESCAPE:
                            return True

        # Проверка победы
        if len(enemies) == 0:
            total_score += round_score
            if current_round < 5:
                # Победа в раунде
                victory_text = font_large.render(f"Раунд {current_round} пройден!", True, GREEN)
                continue_text = font_small.render("Нажмите N для следующего раунда или ESC в меню", True, WHITE)
                score_text = font_small.render(f"Общий счет: {total_score}", True, WHITE)

                screen.blit(victory_text, (WIDTH // 2 - victory_text.get_width() // 2, HEIGHT // 2 - 50))
                screen.blit(continue_text, (WIDTH // 2 - continue_text.get_width() // 2, HEIGHT // 2 + 20))
                screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 + 70))
                pygame.display.flip()

                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            return False
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_n:
                                return game_loop(player_name, current_round + 1, total_score)
                            if event.key == pygame.K_ESCAPE:
                                save_stats(player_name, total_score)
                                return True
            else:
                # Полная победа - возвращаемся к выбору игрока
                save_stats(player_name, total_score)

                # Экран победы
                victory_text = font_large.render("ПОБЕДА!", True, GREEN)
                score_text = font_large.render(f"Финальный счет: {total_score}", True, YELLOW)
                continue_text = font_small.render("Нажмите любую клавишу для выбора игрока", True, WHITE)

                screen.blit(victory_text, (WIDTH // 2 - victory_text.get_width() // 2, HEIGHT // 2 - 70))
                screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
                screen.blit(continue_text, (WIDTH // 2 - continue_text.get_width() // 2, HEIGHT // 2 + 70))
                pygame.display.flip()

                # Ждем нажатия любой клавиши
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            return False
                        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                            return "new_player"  # Специальный код для выбора нового игрока

        pygame.display.flip()
        clock.tick(60)

    return False


def main():
    pygame.display.set_caption("Танчики")

    while True:
        choice = show_menu()
        if choice == "start":
            while True:
                player_name = get_player_name()
                if player_name is None:  # Если игрок закрыл окно ввода имени
                    break

                result = game_loop(player_name, 1, 0)
                if result == "new_player":
                    continue  # Возвращаемся к выбору игрока
                elif not result:
                    break  # Выход из игры
                else:
                    break  # Возврат в меню
        else:
            break

    pygame.quit()


if __name__ == "__main__":
    main()