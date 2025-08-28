import pygame
import platform
import asyncio
from .sprites import Player, Explosion
from .level import Level
from .score import Score
from .ui import Button, Checkbox, CyclingButton
from .constants import *
from .config import load_config, save_config, load_highscores, save_highscores

async def main():
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
    pygame.mixer.set_num_channels(16)

    info = pygame.display.Info()
    NATIVE_WIDTH = info.current_w
    NATIVE_HEIGHT = info.current_h
    current_resolution = "720p"
    WINDOW_WIDTH, WINDOW_HEIGHT = NATIVE_WIDTH, NATIVE_HEIGHT
    virtual_screen = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("Starship Commander")
    clock = pygame.time.Clock()
    is_fullscreen = True

    scale_factor_x = 1.0
    scale_factor_y = 1.0
    letterbox_x = 0
    letterbox_y = 0

    def update_scaling():
        nonlocal scale_factor_x, scale_factor_y, letterbox_x, letterbox_y, screen, WINDOW_WIDTH, WINDOW_HEIGHT
        if is_fullscreen:
            WINDOW_WIDTH, WINDOW_HEIGHT = NATIVE_WIDTH, NATIVE_HEIGHT
            screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
        else:
            WINDOW_WIDTH, WINDOW_HEIGHT = RESOLUTIONS[current_resolution]
            screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

        window_aspect = WINDOW_WIDTH / WINDOW_HEIGHT
        if window_aspect > ASPECT_RATIO:
            scale_factor_y = WINDOW_HEIGHT / VIRTUAL_HEIGHT
            scale_factor_x = scale_factor_y
            scaled_width = VIRTUAL_WIDTH * scale_factor_x
            scaled_height = WINDOW_HEIGHT
            letterbox_x = (WINDOW_WIDTH - scaled_width) / 2
            letterbox_y = 0
        else:
            scale_factor_x = WINDOW_WIDTH / VIRTUAL_WIDTH
            scale_factor_y = scale_factor_x
            scaled_height = VIRTUAL_HEIGHT * scale_factor_y
            scaled_width = WINDOW_WIDTH
            letterbox_x = 0
            letterbox_y = (WINDOW_HEIGHT - scaled_height) / 2

    update_scaling()

    background_image = pygame.image.load(ASSET_PATHS["background_image"]).convert()
    background_image = pygame.transform.scale(background_image, (VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
    background_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT * 2))
    for y in range(0, VIRTUAL_HEIGHT * 2, VIRTUAL_HEIGHT):
        background_surface.blit(background_image, (0, y))

    config = load_config()
    highscores = load_highscores()

    player = Player(config, scale_factor_x, scale_factor_y)
    player.level = Level(scale_factor_x, scale_factor_y)
    score = Score(player, scale_factor_x, scale_factor_y)
    explosions = pygame.sprite.Group()
    game_state = [LANDING]
    play_bgm = True
    bonus_text = ""
    bonus_timer = 0
    level_up_channel = None
    level_up_timer = 0
    bgm_position = 0
    sound_completion_delay = 0
    difficulty_mode = "Normal"
    player_name = ""
    background_y = 0

    BUTTON_WIDTH = 192
    BUTTON_HEIGHT = 48
    CHECKBOX_HEIGHT = 16
    DIFFICULTY_BUTTON_WIDTH = 96
    DIFFICULTY_BUTTON_HEIGHT = 48
    SPACING = 10
    TOTAL_HEIGHT = (BUTTON_HEIGHT * 4) + CHECKBOX_HEIGHT + (DIFFICULTY_BUTTON_HEIGHT * 1) + (24 * scale_factor_y) + (SPACING * 5)
    START_Y = (VIRTUAL_HEIGHT - TOTAL_HEIGHT) // 2

    # 预加载着陆页面使用的图像，避免在渲染时重复加载
    space_bg_image = pygame.image.load(ASSET_PATHS["space_bg_image"]).convert()
    space_bg_image = pygame.transform.scale(space_bg_image, (VIRTUAL_WIDTH, VIRTUAL_HEIGHT * 2))
    player_image = pygame.image.load(ASSET_PATHS["player_image"]).convert_alpha()
    
    # 修改Start按钮的位置，为两个按钮居中做准备
    start_button = Button("START", VIRTUAL_WIDTH // 2 - BUTTON_WIDTH - SPACING // 2, START_Y, BUTTON_WIDTH, BUTTON_HEIGHT, GRAY, CYAN, scale_factor_y=scale_factor_y)
    # 添加Exit按钮
    exit_button = Button("EXIT", VIRTUAL_WIDTH // 2 + SPACING // 2, START_Y, BUTTON_WIDTH, BUTTON_HEIGHT, GRAY, CYAN, scale_factor_y=scale_factor_y)
    bgm_checkbox = Checkbox("MUSIC", VIRTUAL_WIDTH // 2 - BUTTON_WIDTH // 2, START_Y + BUTTON_HEIGHT + SPACING, scale_factor_y)
    difficulty_y = START_Y + BUTTON_HEIGHT + CHECKBOX_HEIGHT + (2 * SPACING)
    difficulty_easy_button = Button("EASY", VIRTUAL_WIDTH // 2 - (DIFFICULTY_BUTTON_WIDTH * 3 + 2 * SPACING) // 2, difficulty_y, DIFFICULTY_BUTTON_WIDTH, DIFFICULTY_BUTTON_HEIGHT, GRAY, CYAN, GREEN, scale_factor_y)
    difficulty_normal_button = Button("NORMAL", VIRTUAL_WIDTH // 2 - (DIFFICULTY_BUTTON_WIDTH // 2), difficulty_y, DIFFICULTY_BUTTON_WIDTH, DIFFICULTY_BUTTON_HEIGHT, GRAY, CYAN, GREEN, scale_factor_y)
    difficulty_hard_button = Button("HARD", VIRTUAL_WIDTH // 2 + (DIFFICULTY_BUTTON_WIDTH // 2) + SPACING, difficulty_y, DIFFICULTY_BUTTON_WIDTH, DIFFICULTY_BUTTON_HEIGHT, GRAY, CYAN, GREEN, scale_factor_y)
    movement_button = CyclingButton("Movement", VIRTUAL_WIDTH // 2 - BUTTON_WIDTH // 2, difficulty_y + DIFFICULTY_BUTTON_HEIGHT + SPACING, BUTTON_WIDTH, BUTTON_HEIGHT, GRAY, CYAN, [2, 3], "movement_speed", scale_factor_y)
    movement_button.current_index = [2, 3].index(config["movement_speed"])
    shooting_button = CyclingButton("Shooting", VIRTUAL_WIDTH // 2 - BUTTON_WIDTH // 2, difficulty_y + DIFFICULTY_BUTTON_HEIGHT + BUTTON_HEIGHT + (2 * SPACING), BUTTON_WIDTH, BUTTON_HEIGHT, GRAY, CYAN, [2, 3], "shooting_speed", scale_factor_y)
    shooting_button.current_index = [2, 3].index(config["shooting_speed"])
    bullet_button = CyclingButton("Bullet", VIRTUAL_WIDTH // 2 - BUTTON_WIDTH // 2, difficulty_y + DIFFICULTY_BUTTON_HEIGHT + (2 * BUTTON_HEIGHT) + (3 * SPACING), BUTTON_WIDTH, BUTTON_HEIGHT, GRAY, CYAN, [2, 3], "bullet_speed", scale_factor_y)
    bullet_button.current_index = [2, 3].index(config["bullet_speed"])

    PAUSE_TOTAL_HEIGHT = (BUTTON_HEIGHT * 4) + CHECKBOX_HEIGHT + (SPACING * 4)
    PAUSE_START_Y = (VIRTUAL_HEIGHT - PAUSE_TOTAL_HEIGHT) // 2
    pause_resume_button = Button("RESUME", VIRTUAL_WIDTH // 2 - BUTTON_WIDTH // 2, PAUSE_START_Y, BUTTON_WIDTH, BUTTON_HEIGHT, GRAY, CYAN, scale_factor_y=scale_factor_y)
    pause_quit_button = Button("QUIT", VIRTUAL_WIDTH // 2 - BUTTON_WIDTH // 2, PAUSE_START_Y + BUTTON_HEIGHT + SPACING, BUTTON_WIDTH, BUTTON_HEIGHT, GRAY, CYAN, scale_factor_y=scale_factor_y)
    pause_music_checkbox = Checkbox("MUSIC", VIRTUAL_WIDTH // 2 - BUTTON_WIDTH // 2, PAUSE_START_Y + (2 * BUTTON_HEIGHT) + (2 * SPACING), scale_factor_y)
    pause_movement_button = CyclingButton("Movement", VIRTUAL_WIDTH // 2 - BUTTON_WIDTH // 2, PAUSE_START_Y + (2 * BUTTON_HEIGHT) + CHECKBOX_HEIGHT + (3 * SPACING), BUTTON_WIDTH, BUTTON_HEIGHT, GRAY, CYAN, [2, 3], "movement_speed", scale_factor_y)
    pause_movement_button.current_index = [2, 3].index(config["movement_speed"])
    pause_shooting_button = CyclingButton("Shooting", VIRTUAL_WIDTH // 2 - BUTTON_WIDTH // 2, PAUSE_START_Y + (3 * BUTTON_HEIGHT) + CHECKBOX_HEIGHT + (4 * SPACING), BUTTON_WIDTH, BUTTON_HEIGHT, GRAY, CYAN, [2, 3], "shooting_speed", scale_factor_y)
    pause_shooting_button.current_index = [2, 3].index(config["shooting_speed"])
    pause_bullet_button = CyclingButton("Bullet", VIRTUAL_WIDTH // 2 - BUTTON_WIDTH // 2, PAUSE_START_Y + (4 * BUTTON_HEIGHT) + CHECKBOX_HEIGHT + (5 * SPACING), BUTTON_WIDTH, BUTTON_HEIGHT, GRAY, CYAN, [2, 3], "bullet_speed", scale_factor_y)
    pause_bullet_button.current_index = [2, 3].index(config["bullet_speed"])

    gameover_restart_button = Button("RESTART", VIRTUAL_WIDTH // 2 - BUTTON_WIDTH // 2, VIRTUAL_HEIGHT // 2 + 80, BUTTON_WIDTH, BUTTON_HEIGHT, GRAY, CYAN, scale_factor_y=scale_factor_y)
    gameover_quit_button = Button("QUIT", VIRTUAL_WIDTH // 2 - BUTTON_WIDTH // 2, VIRTUAL_HEIGHT // 2 + 140, BUTTON_WIDTH, BUTTON_HEIGHT, GRAY, CYAN, scale_factor_y=scale_factor_y)
    name_submit_button = Button("SUBMIT", VIRTUAL_WIDTH // 2 - BUTTON_WIDTH // 2, VIRTUAL_HEIGHT // 2 + 40, BUTTON_WIDTH, BUTTON_HEIGHT, GRAY, CYAN, scale_factor_y=scale_factor_y)

    bg_scroll_y = 0
    title_alpha = 0
    title_fade_speed = 1
    ship_angle = 0
    ship_x = VIRTUAL_WIDTH * 0.50
    ship_y = VIRTUAL_HEIGHT * 0.1
    welcome_text = "Prepare to command your starship against the alien fleet!"
    welcome_index = 0
    welcome_timer = 0
    welcome_visible = False

    sound_effects = {
        "shoot": pygame.mixer.Sound(ASSET_PATHS["shoot_sound"]),
        "explosion": pygame.mixer.Sound(ASSET_PATHS["explosion_sound"]),
        "lost_life": pygame.mixer.Sound(ASSET_PATHS["lost_life_sound"]),
        "game_over": pygame.mixer.Sound(ASSET_PATHS["game_over_sound"]),
        "level_clear": pygame.mixer.Sound(ASSET_PATHS["level_clear_sound"]),
        "bonus": pygame.mixer.Sound(ASSET_PATHS["bonus_sound"]),
        "power_up_collect": pygame.mixer.Sound(ASSET_PATHS["power_up_collect_sound"]),
        "power_up_activate": pygame.mixer.Sound(ASSET_PATHS["power_up_activate_sound"]),
        "power_up_zero": pygame.mixer.Sound(ASSET_PATHS["power_up_zero_sound"]),
        "click": pygame.mixer.Sound(ASSET_PATHS["click_sound"]),
    }
    pygame.mixer.music.load(ASSET_PATHS["bgm"])
    LEVEL_CLEAR_DURATION = sound_effects["level_clear"].get_length()
    MINIMUM_SOUND_DURATION = LEVEL_CLEAR_DURATION + 0.1

    def reset_game(play_bgm, difficulty):
        nonlocal player, score, explosions, background_y, bonus_text, bonus_timer, bgm_position, difficulty_mode, player_name
        difficulty_mode = difficulty
        player = Player(config, scale_factor_x, scale_factor_y)
        player.level = Level(scale_factor_x, scale_factor_y)
        score = Score(player, scale_factor_x, scale_factor_y)
        explosions = pygame.sprite.Group()
        background_y = 0
        bonus_text = ""
        bonus_timer = 0
        player_name = ""
        player.level.spawn_wave()
        bgm_position = 0
        if play_bgm:
            pygame.mixer.music.play(-1, start=bgm_position)
        return True

    def update_highscore(current_score, name):
        nonlocal highscores
        highscores.append({"name": name, "score": current_score})
        highscores.sort(key=lambda x: x["score"], reverse=True)
        highscores = highscores[:5]
        save_highscores(highscores)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    is_fullscreen = not is_fullscreen
                    update_scaling()
                    player = Player(config, scale_factor_x, scale_factor_y)
                    player.level = Level(scale_factor_x, scale_factor_y)
                    player.level.enemies = pygame.sprite.Group([Enemy(enemy.rect.x, enemy.rect.y, enemy.enemy_type, player.level.difficulty_modifier, scale_factor_x, scale_factor_y) for enemy in player.level.enemies])
                    explosions = pygame.sprite.Group([Explosion(explosion.rect.centerx / scale_factor_x, explosion.rect.centery / scale_factor_y, scale_factor_x, scale_factor_y) for explosion in explosions])
                    score = Score(player, scale_factor_x, scale_factor_y)

                if game_state[0] == GAME_PLAYING:
                    if event.key == pygame.K_SPACE:
                        player.shoot()
                    if event.key == pygame.K_1:
                        player.activate_power_up("shield", score)
                    if event.key == pygame.K_2:
                        player.activate_power_up("spread", score)
                    if event.key == pygame.K_ESCAPE:
                        game_state[0] = PAUSED
                elif game_state[0] == NAME_INPUT:
                    if event.key == pygame.K_RETURN:
                        update_highscore(score.score, player_name or "Anonymous")
                        reset_game(play_bgm, difficulty_mode)
                        game_state[0] = LANDING
                    elif event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    elif event.unicode.isalnum() or event.unicode in " -_":
                        player_name += event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if game_state[0] == LANDING:
                    if start_button.is_clicked(pos, scale_factor_x, scale_factor_y):
                        sound_effects["click"].play()
                        reset_game(play_bgm, difficulty_mode)
                        game_state[0] = GAME_PLAYING
                    # 添加Exit按钮点击事件处理
                    if exit_button.is_clicked(pos, scale_factor_x, scale_factor_y):
                        sound_effects["click"].play()
                        pygame.time.delay(300)  # 等待音效播放完成
                        running = False
                    if bgm_checkbox.toggle(pos, scale_factor_x, scale_factor_y):
                        play_bgm = bgm_checkbox.checked
                        if not play_bgm:
                            pygame.mixer.music.stop()
                        else:
                            pygame.mixer.music.play(-1, start=bgm_position)
                    if difficulty_easy_button.is_clicked(pos, scale_factor_x, scale_factor_y):
                        sound_effects["click"].play()
                        difficulty_mode = "Easy"
                        difficulty_easy_button.selected = True
                        difficulty_normal_button.selected = False
                        difficulty_hard_button.selected = False
                    if difficulty_normal_button.is_clicked(pos, scale_factor_x, scale_factor_y):
                        sound_effects["click"].play()
                        difficulty_mode = "Normal"
                        difficulty_easy_button.selected = False
                        difficulty_normal_button.selected = True
                        difficulty_hard_button.selected = False
                    if difficulty_hard_button.is_clicked(pos, scale_factor_x, scale_factor_y):
                        sound_effects["click"].play()
                        difficulty_mode = "Hard"
                        difficulty_easy_button.selected = False
                        difficulty_normal_button.selected = False
                        difficulty_hard_button.selected = True
                    if movement_button.is_clicked(pos, scale_factor_x, scale_factor_y):
                        sound_effects["click"].play()
                        bonus_text = movement_button.cycle(config)
                        save_config(config)
                        bonus_timer = 120
                    if shooting_button.is_clicked(pos, scale_factor_x, scale_factor_y):
                        sound_effects["click"].play()
                        bonus_text = shooting_button.cycle(config)
                        save_config(config)
                        bonus_timer = 120
                    if bullet_button.is_clicked(pos, scale_factor_x, scale_factor_y):
                        sound_effects["click"].play()
                        bonus_text = bullet_button.cycle(config)
                        save_config(config)
                        bonus_timer = 120
                elif game_state[0] == PAUSED:
                    if pause_resume_button.is_clicked(pos, scale_factor_x, scale_factor_y):
                        game_state[0] = GAME_PLAYING
                    if pause_quit_button.is_clicked(pos, scale_factor_x, scale_factor_y):
                        running = False
                    if pause_music_checkbox.toggle(pos, scale_factor_x, scale_factor_y):
                        play_bgm = pause_music_checkbox.checked
                        if not play_bgm:
                            pygame.mixer.music.stop()
                        else:
                            pygame.mixer.music.play(-1, start=bgm_position)
                    if pause_movement_button.is_clicked(pos, scale_factor_x, scale_factor_y):
                        bonus_text = pause_movement_button.cycle(config)
                        save_config(config)
                        bonus_timer = 120
                    if pause_shooting_button.is_clicked(pos, scale_factor_x, scale_factor_y):
                        bonus_text = pause_shooting_button.cycle(config)
                        save_config(config)
                        bonus_timer = 120
                    if pause_bullet_button.is_clicked(pos, scale_factor_x, scale_factor_y):
                        bonus_text = pause_bullet_button.cycle(config)
                        save_config(config)
                        bonus_timer = 120
                elif game_state[0] == GAME_OVER:
                    if gameover_restart_button.is_clicked(pos, scale_factor_x, scale_factor_y):
                        reset_game(play_bgm, difficulty_mode)
                        game_state[0] = GAME_PLAYING
                    if gameover_quit_button.is_clicked(pos, scale_factor_x, scale_factor_y):
                        running = False
                elif game_state[0] == NAME_INPUT:
                    if name_submit_button.is_clicked(pos, scale_factor_x, scale_factor_y):
                        update_highscore(score.score, player_name or "Anonymous")
                        reset_game(play_bgm, difficulty_mode)
                        game_state[0] = LANDING
                elif game_state[0] == GAME_PLAYING and event.button == 1:
                    player.shoot()

        if game_state[0] in [LANDING, PAUSED]:
            pygame.mouse.set_visible(True)
        else:
            pygame.mouse.set_visible(False)

        if game_state[0] == LANDING:
            bg_scroll_y += 1
            if bg_scroll_y >= VIRTUAL_HEIGHT:
                bg_scroll_y = 0
            # 使用预加载的图像，避免重复加载
            virtual_screen.blit(space_bg_image, (0, bg_scroll_y - VIRTUAL_HEIGHT), (0, 0, VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
            if bg_scroll_y < VIRTUAL_HEIGHT:
                virtual_screen.blit(space_bg_image, (0, bg_scroll_y), (0, 0, VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

            scaled_font = pygame.font.Font(ASSET_PATHS["font"], int(24 * scale_factor_y))
            title_text = scaled_font.render("STARSHIP COMMANDER", True, YELLOW)
            title_surface = pygame.Surface(title_text.get_size(), pygame.SRCALPHA)
            title_surface.blit(title_text, (0, 0))
            title_alpha = min(255, title_alpha + title_fade_speed)
            title_surface.set_alpha(title_alpha)
            title_y = START_Y - 40 - title_text.get_height()
            virtual_screen.blit(title_surface, (VIRTUAL_WIDTH // 2 - title_text.get_width() // 2, title_y))

            ship_angle += 1
            # 使用预加载的图像
            rotated_ship = pygame.transform.rotate(pygame.transform.scale(player_image, (int(64 * scale_factor_x), int(64 * scale_factor_y))), ship_angle)
            ship_rect = rotated_ship.get_rect(center=(ship_x, ship_y))
            virtual_screen.blit(rotated_ship, ship_rect.topleft)

            welcome_timer += 1
            if welcome_timer % 5 == 0 and welcome_index < len(welcome_text):
                welcome_index += 1
            if welcome_index > 0:
                welcome_visible = True
            if welcome_visible:
                welcome_font = pygame.font.Font(ASSET_PATHS["font"], int(12 * scale_factor_y))
                welcome_surface = welcome_font.render(welcome_text[:welcome_index], True, CYAN)
                welcome_box = pygame.Surface((welcome_surface.get_width() + 20, welcome_surface.get_height() + 10), pygame.SRCALPHA)
                pygame.draw.rect(welcome_box, GRAY, welcome_box.get_rect(), border_radius=5)
                welcome_box.blit(welcome_surface, (10, 5))
                virtual_screen.blit(welcome_box, (VIRTUAL_WIDTH // 2 - welcome_box.get_width() // 2, title_y + title_text.get_height() + 2))

            if title_alpha >= 255:
                title_alpha = 255

            highscore_y = START_Y + TOTAL_HEIGHT + 20
            scaled_font = pygame.font.Font(ASSET_PATHS["font"], int(16 * scale_factor_y))
            text = "HIGH SCORE"
            text_width, _ = scaled_font.size(text)
            virtual_screen.blit(scaled_font.render(text, True, YELLOW), (VIRTUAL_WIDTH // 2 - text_width // 2, highscore_y - 20))
            for i, entry in enumerate(highscores):
                text = f"{i + 1}. {entry['name']}: {entry['score']}"
                score_surface = scaled_font.render(text, True, YELLOW)
                virtual_screen.blit(score_surface, (VIRTUAL_WIDTH // 2 - score_surface.get_width() // 2, highscore_y + i * 20))

            mouse_pos = pygame.mouse.get_pos()
            start_button.hovered = start_button.is_clicked(mouse_pos, scale_factor_x, scale_factor_y)
            exit_button.hovered = exit_button.is_clicked(mouse_pos, scale_factor_x, scale_factor_y)
            difficulty_easy_button.hovered = difficulty_easy_button.is_clicked(mouse_pos, scale_factor_x, scale_factor_y)
            difficulty_normal_button.hovered = difficulty_normal_button.is_clicked(mouse_pos, scale_factor_x, scale_factor_y)
            difficulty_hard_button.hovered = difficulty_hard_button.is_clicked(mouse_pos, scale_factor_x, scale_factor_y)
            movement_button.hovered = movement_button.is_clicked(mouse_pos, scale_factor_x, scale_factor_y)
            shooting_button.hovered = shooting_button.is_clicked(mouse_pos, scale_factor_x, scale_factor_y)
            bullet_button.hovered = bullet_button.is_clicked(mouse_pos, scale_factor_x, scale_factor_y)

            difficulty_easy_button.selected = (difficulty_mode == "Easy")
            difficulty_normal_button.selected = (difficulty_mode == "Normal")
            difficulty_hard_button.selected = (difficulty_mode == "Hard")

            start_button.draw(virtual_screen)
            exit_button.draw(virtual_screen)
            bgm_checkbox.draw(virtual_screen)
            difficulty_easy_button.draw(virtual_screen)
            difficulty_normal_button.draw(virtual_screen)
            difficulty_hard_button.draw(virtual_screen)
            movement_button.draw(virtual_screen)
            shooting_button.draw(virtual_screen)
            bullet_button.draw(virtual_screen)

        elif game_state[0] == GAME_PLAYING:
            keys = pygame.key.get_pressed()
            mouse_pos = pygame.mouse.get_pos()
            player.move(keys, mouse_pos)
            player.update()

            player.level.update_group_movement()
            for enemy in player.level.enemies:
                enemy.update(player.rect.center, player.level.group_x_offset)

            enemies_to_remove = []
            for enemy in player.level.enemies:
                for bullet in player.bullets:
                    if pygame.sprite.collide_rect(bullet, enemy):
                        enemy.health -= bullet.damage
                        bullet.kill()
                        if enemy.health <= 0:
                            enemies_to_remove.append(enemy)
                            points = 50 if not enemy.is_boss else 500
                            score.add_points(points)
                            sound_effects["explosion"].play()
                            explosions.add(Explosion(enemy.rect.centerx, enemy.rect.centery, scale_factor_x, scale_factor_y))
                            player.level.spawn_power_up(enemy.rect.centerx, enemy.rect.centery)
                            if enemy.is_boss:
                                player.level.boss_defeated = True

                for bullet in enemy.bullets:
                    if pygame.sprite.collide_rect(bullet, player) and not player.shield_active:
                        player.lives -= 1
                        bullet.kill()
                        sound_effects["lost_life"].play()
                        explosions.add(Explosion(player.rect.centerx, player.rect.centery, scale_factor_x, scale_factor_y))
                        if player.lives <= 0:
                            pygame.mixer.music.stop()
                            sound_effects["game_over"].play()
                            game_state[0] = NAME_INPUT

            for enemy in enemies_to_remove:
                enemy.kill()

            power_up_collisions = pygame.sprite.spritecollide(player, player.level.power_ups, True)
            for power_up in power_up_collisions:
                player.collect_power_up(power_up.power_type, score)

            if not player.level.enemies:
                game_state = player.level.next_wave(game_state, score, sound_effects["bonus"])

            background_y += SCROLL_SPEED
            if background_y >= BACKGROUND_HEIGHT:
                background_y -= BACKGROUND_HEIGHT
            source_y = int(background_y) % BACKGROUND_HEIGHT
            source_rect = pygame.Rect(0, source_y, VIRTUAL_WIDTH, VIRTUAL_HEIGHT)
            if source_y + VIRTUAL_HEIGHT > BACKGROUND_HEIGHT:
                first_part_height = BACKGROUND_HEIGHT - source_y
                virtual_screen.blit(background_surface, (0, 0), pygame.Rect(0, source_y, VIRTUAL_WIDTH, first_part_height))
                second_part_height = VIRTUAL_HEIGHT - first_part_height
                virtual_screen.blit(background_surface, (0, first_part_height), pygame.Rect(0, 0, VIRTUAL_WIDTH, second_part_height))
            else:
                virtual_screen.blit(background_surface, (0, 0), source_rect)

            explosions.update()
            player.level.power_ups.update()
            player.draw(virtual_screen)
            for enemy in player.level.enemies:
                enemy.draw(virtual_screen)
            player.level.power_ups.draw(virtual_screen)
            explosions.draw(virtual_screen)
            score.draw(virtual_screen)

        elif game_state[0] == PAUSED:
            virtual_screen.fill(BLACK)
            scaled_font = pygame.font.Font(ASSET_PATHS["font"], int(16 * scale_factor_y))
            paused_text = scaled_font.render("PAUSED", True, YELLOW)
            paused_y = PAUSE_START_Y - 40 - paused_text.get_height()
            virtual_screen.blit(paused_text, (VIRTUAL_WIDTH // 2 - paused_text.get_width() // 2, paused_y))

            mouse_pos = pygame.mouse.get_pos()
            pause_resume_button.hovered = pause_resume_button.is_clicked(mouse_pos, scale_factor_x, scale_factor_y)
            pause_quit_button.hovered = pause_quit_button.is_clicked(mouse_pos, scale_factor_x, scale_factor_y)
            pause_movement_button.hovered = pause_movement_button.is_clicked(mouse_pos, scale_factor_x, scale_factor_y)
            pause_shooting_button.hovered = pause_shooting_button.is_clicked(mouse_pos, scale_factor_x, scale_factor_y)
            pause_bullet_button.hovered = pause_bullet_button.is_clicked(mouse_pos, scale_factor_x, scale_factor_y)

            pause_resume_button.draw(virtual_screen)
            pause_quit_button.draw(virtual_screen)
            pause_music_checkbox.draw(virtual_screen)
            pause_movement_button.draw(virtual_screen)
            pause_shooting_button.draw(virtual_screen)
            pause_bullet_button.draw(virtual_screen)

        elif game_state[0] == LEVEL_UP:
            virtual_screen.fill(BLACK)
            scaled_font = pygame.font.Font(ASSET_PATHS["font"], int(16 * scale_factor_y))
            level_up_text = scaled_font.render(f"LEVEL UP! LEVEL {player.level.level}", True, YELLOW)
            virtual_screen.blit(level_up_text, (VIRTUAL_WIDTH // 2 - level_up_text.get_width() // 2, VIRTUAL_HEIGHT // 2 - 24))

            if level_up_channel is None:
                bgm_position = pygame.mixer.music.get_pos() / 1000
                if play_bgm:
                    pygame.mixer.music.pause()
                level_up_channel = sound_effects["level_clear"].play()
                level_up_timer = 0
                sound_completion_delay = 0
                score.set_difficulty_message("ENEMIES TOUGHER!")

            level_up_timer += 1

            sound_finished = level_up_channel and not level_up_channel.get_busy()
            min_duration_reached = level_up_timer >= (MINIMUM_SOUND_DURATION * 60)
            timeout_reached = level_up_timer >= 90

            if sound_finished:
                sound_completion_delay += 1
            else:
                sound_completion_delay = 0

            if (min_duration_reached or timeout_reached) and (sound_finished and sound_completion_delay >= 10):
                level_up_channel = None
                level_up_timer = 0
                if play_bgm:
                    pygame.mixer.music.unpause()
                player.level.spawn_wave()
                game_state[0] = GAME_PLAYING

        elif game_state[0] == NAME_INPUT:
            virtual_screen.fill(BLACK)
            scaled_font = pygame.font.Font(ASSET_PATHS["font"], int(16 * scale_factor_y))
            game_over_text = scaled_font.render("GAME OVER", True, YELLOW)
            score_text = scaled_font.render(f"SCORE: {score.score}", True, YELLOW)
            name_prompt = scaled_font.render("Enter Name:", True, YELLOW)
            name_text = scaled_font.render(player_name + ("" if len(player_name) == 0 else "|"), True, YELLOW)
            virtual_screen.blit(game_over_text, (VIRTUAL_WIDTH // 2 - game_over_text.get_width() // 2, VIRTUAL_HEIGHT // 2 - 160))
            virtual_screen.blit(score_text, (VIRTUAL_WIDTH // 2 - score_text.get_width() // 2, VIRTUAL_HEIGHT // 2 - 120))
            virtual_screen.blit(name_prompt, (VIRTUAL_WIDTH // 2 - name_prompt.get_width() // 2, VIRTUAL_HEIGHT // 2 - 40))
            virtual_screen.blit(name_text, (VIRTUAL_WIDTH // 2 - name_text.get_width() // 2, VIRTUAL_HEIGHT // 2))

            mouse_pos = pygame.mouse.get_pos()
            name_submit_button.hovered = name_submit_button.is_clicked(mouse_pos, scale_factor_x, scale_factor_y)
            name_submit_button.draw(virtual_screen)

            highscore_y = VIRTUAL_HEIGHT // 2 + 120
            text = "HIGH SCORE"
            text_width, _ = scaled_font.size(text)
            virtual_screen.blit(scaled_font.render(text, True, YELLOW), (VIRTUAL_WIDTH // 2 - text_width // 2, highscore_y - 20))
            for i, entry in enumerate(highscores):
                text = f"{i + 1}. {entry['name']}: {entry['score']}"
                score_surface = scaled_font.render(text, True, YELLOW)
                virtual_screen.blit(score_surface, (VIRTUAL_WIDTH // 2 - score_surface.get_width() // 2, highscore_y + i * 20))

        elif game_state[0] == GAME_OVER:
            virtual_screen.fill(BLACK)
            scaled_font = pygame.font.Font(ASSET_PATHS["font"], int(16 * scale_factor_y))
            game_over_text = scaled_font.render("GAME OVER", True, YELLOW)
            score_text = scaled_font.render(f"SCORE: {score.score}", True, YELLOW)
            virtual_screen.blit(game_over_text, (VIRTUAL_WIDTH // 2 - game_over_text.get_width() // 2, VIRTUAL_HEIGHT // 2 - 160))
            virtual_screen.blit(score_text, (VIRTUAL_WIDTH // 2 - score_text.get_width() // 2, VIRTUAL_HEIGHT // 2 - 120))

            highscore_y = VIRTUAL_HEIGHT // 2 - 40
            virtual_screen.blit(scaled_font.render("HIGH SCORES", True, YELLOW), (VIRTUAL_WIDTH // 2 - 80, highscore_y - 20))
            for i, entry in enumerate(highscores):
                text = f"{i + 1}. {entry['name']}: {entry['score']}"
                score_surface = scaled_font.render(text, True, YELLOW)
                virtual_screen.blit(score_surface, (VIRTUAL_WIDTH // 2 - score_surface.get_width() // 2, highscore_y + i * 20))

            mouse_pos = pygame.mouse.get_pos()
            gameover_restart_button.hovered = gameover_restart_button.is_clicked(mouse_pos, scale_factor_x, scale_factor_y)
            gameover_quit_button.hovered = gameover_quit_button.is_clicked(mouse_pos, scale_factor_x, scale_factor_y)
            gameover_restart_button.draw(virtual_screen)
            gameover_quit_button.draw(virtual_screen)

        # 添加FPS显示代码到正确位置，在screen.fill之后，pygame.display.flip之前
        fps = str(int(clock.get_fps()))
        scaled_font = pygame.font.Font(ASSET_PATHS["font"], int(16 * scale_factor_y))
        fps_text = scaled_font.render(f"FPS: {fps}", True, YELLOW)
        virtual_screen.blit(fps_text, (20, 100))
        
        screen.fill(BLACK)
        scaled_surface = pygame.transform.scale(virtual_screen, (int(VIRTUAL_WIDTH * scale_factor_x), int(VIRTUAL_HEIGHT * scale_factor_y)))
        screen.blit(scaled_surface, (letterbox_x, letterbox_y))
        
        pygame.display.flip()
        clock.tick(60)
        # await asyncio.sleep(1.0 / 60)

    pygame.quit()

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())