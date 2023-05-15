import pygame
from copy import deepcopy
import random
from random import choice, randrange


def check_borders(figure, i, field, W, H):
    if figure[i].x < 0 or figure[i].x > W - 1:
        return False
    elif figure[i].y > H - 1 or field[figure[i].y][figure[i].x]:
        return False
    return True


def get_record():
    try:
        with open('record') as f:
            return f.readline()
    except FileNotFoundError:
        with open('record', 'w') as f:
            f.write('0')

def get_last_score():
    try:
        with open('last_score') as f:
            return f.readline()
    except FileNotFoundError:
        with open('last_score', 'w') as f:
            f.write('0')

def set_record(record, score):
    rec = max(int(record), score)
    with open('record', 'w') as f:
        f.write(str(rec))

def set_last_score(score):
    with open('last_score', 'w') as f:
        f.write(str(score))

def game(sc):
    W, H = 10, 20
    TILE = 35
    GAME_RES = W * TILE, H * TILE
    FPS = 60

    game_sc = pygame.Surface(GAME_RES)
    clock = pygame.time.Clock()

    grid = [pygame.Rect(x * TILE, y * TILE, TILE, TILE) for x in range(W) for y in range(H)]

    figures_pos = [[(-1, 0), (-2, 0), (0, 0), (1, 0)],
                   [(0, -1), (-1, -1), (-1, 0), (0, 0)],
                   [(-1, 0), (-1, 1), (0, 0), (0, -1)],
                   [(0, 0), (-1, 0), (0, 1), (-1, -1)],
                   [(0, 0), (0, -1), (0, 1), (-1, -1)],
                   [(0, 0), (0, -1), (0, 1), (1, -1)],
                   [(0, 0), (0, -1), (0, 1), (-1, 0)]]

    bg = pygame.image.load('img/bg.jpg').convert()
    game_bg = pygame.image.load('img/bg2.jpg').convert()
    good_job_bg = pygame.image.load('img/good_job.jpg').convert()
    good_job_duration = 1200

    main_font = pygame.font.Font('font/font.ttf', 65)
    font = pygame.font.Font('font/font.ttf', 45)

    title_tetris = main_font.render('TETRIS', True, pygame.Color('white'))
    title_score = font.render('score:', True, pygame.Color('green'))
    title_record = font.render('record:', True, pygame.Color('purple'))

    move_sound = pygame.mixer.Sound("tetris-assets/sounds/move_sound.wav")
    rotate_sound = pygame.mixer.Sound("tetris-assets/sounds/rotate_sound.wav")
    fall_sound = pygame.mixer.Sound("tetris-assets/sounds/fall_sound.wav")
    line_sound1 = pygame.mixer.Sound("tetris-assets/sounds/line_sound1.wav")
    line_sound2 = pygame.mixer.Sound("tetris-assets/sounds/line_sound2.wav")
    line_sounds = [line_sound1, line_sound2]
    gameover_sound = pygame.mixer.Sound("tetris-assets/sounds/gameover_sound.wav")


    get_color = lambda : (randrange(30, 256), randrange(30, 256), randrange(30, 256))

    global figure, next_figure
    color, next_color = get_color(), get_color()

    global score, lines
    scores = {0: 0, 1: 100, 2: 300, 3: 700, 4: 1500}


    figures = [[pygame.Rect(x + W // 2, y + 1, 1, 1) for x, y in fig_pos] for fig_pos in figures_pos]
    figure_rect = pygame.Rect(0, 0, TILE - 2, TILE - 2)
    score, lines = 0, 0
    anim_count, anim_speed, anim_limit = 0, 60, 2000
    field = [[0 for i in range(W)] for j in range(H)]

    figure, next_figure = deepcopy(choice(figures)), deepcopy(choice(figures))
    while True:
        record = get_record()
        dx, rotate = 0, False
        sc.blit(bg, (0, 0))
        sc.blit(game_sc, (20, 20))
        game_sc.blit(game_bg, (0, 0))
        # delay for full lines
        for i in range(lines):
            pygame.time.wait(200)
        # control
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    move_sound.play()
                    dx = -1
                elif event.key == pygame.K_RIGHT:
                    move_sound.play()
                    dx = 1
                elif event.key == pygame.K_DOWN:
                    fall_sound.play()
                    anim_limit = 100
                elif event.key == pygame.K_UP:
                    rotate_sound.play()
                    rotate = True
        # move x
        figure_old = deepcopy(figure)
        for i in range(4):
            figure[i].x += dx
            if not check_borders(figure, i, field, W, H):
                figure = deepcopy(figure_old)
                break
        # move y
        anim_count += anim_speed
        if anim_count > anim_limit:
            anim_count = 0
            figure_old = deepcopy(figure)
            for i in range(4):
                figure[i].y += 1
                if not check_borders(figure, i, field, W, H):
                    for i in range(4):
                        field[figure_old[i].y][figure_old[i].x] = color
                    figure, color = next_figure, next_color
                    next_figure, next_color = deepcopy(choice(figures)), get_color()
                    anim_limit = 2000
                    break
        # rotate
        center = figure[0]
        figure_old = deepcopy(figure)
        if rotate:
            for i in range(4):
                x = figure[i].y - center.y
                y = figure[i].x - center.x
                figure[i].x = center.x - x
                figure[i].y = center.y + y
                if not check_borders(figure, i, field, W, H):
                    figure = deepcopy(figure_old)
                    break
        # check lines
        line, lines = H - 1, 0
        for row in range(H - 1, -1, -1):
            count = 0
            for i in range(W):
                if field[row][i]:
                    count += 1
                field[line][i] = field[row][i]
            if count < W:
                line -= 1
            else:
                anim_speed += 3
                lines += 1
                
        # compute score
        prev_score = score
        score += scores[lines]

        # line breaking
        if prev_score != score:
            start_time = pygame.time.get_ticks()
            pygame.mixer.music.pause()
            line_sound = random.choice(line_sounds)
            line_sound.play()
            
            while pygame.time.get_ticks() - start_time < good_job_duration:
                game_sc.blit(good_job_bg, (0, 0))
                sc.blit(game_sc, (20, 20))
                pygame.display.flip()
            pygame.mixer.music.unpause()
        
        # draw grid
        [pygame.draw.rect(game_sc, (40, 40, 40), i_rect, 1) for i_rect in grid]
        # draw figure
        for i in range(4):
            figure_rect.x = figure[i].x * TILE
            figure_rect.y = figure[i].y * TILE
            pygame.draw.rect(game_sc, color, figure_rect)
        # draw field
        for y, raw in enumerate(field):
            for x, col in enumerate(raw):
                if col:
                    figure_rect.x, figure_rect.y = x * TILE, y * TILE
                    pygame.draw.rect(game_sc, col, figure_rect)
        # draw next figure
        for i in range(4):
            figure_rect.x = next_figure[i].x * TILE + 360
            figure_rect.y = next_figure[i].y * TILE + 185
            pygame.draw.rect(sc, next_color, figure_rect)
        # draw titles
        sc.blit(title_tetris, (400, 20))
        sc.blit(title_score, (460, 530))
        sc.blit(font.render(str(score), True, pygame.Color('white')), (470, 590))
        sc.blit(title_record, (450, 400))
        sc.blit(font.render(record, True, pygame.Color('gold')), (470, 460))
        # game over
        for i in range(W):
            if field[0][i]:
                pygame.mixer.music.pause()
                gameover_sound.play()
                set_record(record, score)
                set_last_score(score)
                field = [[0 for i in range(W)] for i in range(H)]
                anim_count, anim_speed, anim_limit = 0, 60, 2000
                score = 0
                for i_rect in grid:
                    pygame.draw.rect(game_sc, get_color(), i_rect)
                    sc.blit(game_sc, (20, 20))
                    pygame.display.flip()
                    clock.tick(35)
                return

        pygame.display.flip()
        clock.tick(FPS)
    sc.fill((0,0,0))
# game()


def menu():

    pygame.init()
    RES = 700, 750
    sc = pygame.display.set_mode(RES)
    run = True

    good_morning = pygame.mixer.Sound("tetris-assets/sounds/good_morning.wav")
    pygame.mixer.music.load("tetris-assets/sounds/background_music.mp3")
    

    
    main_font = pygame.font.Font('font/font.ttf', 65)
    font = pygame.font.Font('font/font.ttf', 45)
    fontMenu = pygame.font.Font('font/font.ttf', 25)

    title_tetris = main_font.render('TETRIS', True, pygame.Color('white'))
    title_score = font.render('Score:', True, pygame.Color('green'))
    title_record = font.render('Record:', True, pygame.Color('purple'))
    title_last_score = font.render('Last score:', True, pygame.Color('green'))

    title_menu = fontMenu.render('Press "SPACE" to start a new game', True, pygame.Color('White'))

    good_morning_duration = 4000
    good_morning.play()
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < good_morning_duration:
        pass
    pygame.mixer.music.set_volume(0.4)
    pygame.mixer.music.play(-1)

    while run:
        record = get_record()
        last_score = get_last_score()
        sc.blit(title_tetris, (230, 80))
        sc.blit(title_record, (270, 220))
        sc.blit(font.render(record, True, pygame.Color('gold')), (300, 290))
        sc.blit(title_last_score, (220, 370))
        sc.blit(font.render(last_score, True, pygame.Color('gold')), (300, 440))
        sc.blit(title_menu, (110, 600))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
 
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    sc.fill((0, 0, 0))  # Clear the screen
                    game(sc)
                    sc.fill((0, 0, 0))  # Clear the screen
                    pygame.mixer.music.unpause()
    pygame.quit()

menu()