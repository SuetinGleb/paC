import pygame
import os
import sys


pygame.init()
size = WIDTH, HEIGHT = 475, 475
screen = pygame.display.set_mode(size)
running = True
screen.fill((0, 0, 0))
clock = pygame.time.Clock()
FPS = 24


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if colorkey is not None:
        image = pygame.image.load(fullname).convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = pygame.image.load(fullname).convert_alpha()
    return image


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return [list(i) for i in list(map(lambda x: x.ljust(max_width, '-'), level_map))]


def terminate():
    pygame.quit()
    sys.exit()


def valid_coord(x, y):
    return game_map[y % level_y][x % level_x] != '#'


def get_ch(x, y):
    return game_map[y % level_y][x % level_x]


def change_ch(x, y, ch):
    game_map[y % level_y][x % level_x] = ch


def start_screen():
    global game_state
    intro_text = ["PACMAN", "",
                  "Created by Gleb",
                  "Good luck c:"]
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    io = 'yellow'
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color(io))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 150
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)
        io = 'red'

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        elif event.type == pygame.KEYDOWN:
            if not event.key == pygame.K_ESCAPE:
                game_state = 2
            else:
                terminate()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            game_state = 2


def game_over_screen1():
    fon = pygame.transform.scale(load_image('wasted.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            time_finish = 50
            while time_finish > 0:
                time_finish -= 1
                clock.tick(FPS)
            terminate()


def game_over_screen():
    line = "You loss!"
    font = pygame.font.Font(None, 100)
    screen.fill((0, 0, 0))
    io = 'white'
    string_rendered = font.render(line, 1, pygame.Color(io))
    intro_rect = string_rendered.get_rect()
    intro_rect.top = HEIGHT / 2 - intro_rect.height / 2
    intro_rect.x = WIDTH / 2 - intro_rect.width / 2
    screen.blit(string_rendered, intro_rect)

    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            start_screen()


def game_win_screen():
    line = "You win!"
    font = pygame.font.Font(None, 100)
    screen.fill((0, 0, 0))
    io = 'white'
    string_rendered = font.render(line, 1, pygame.Color(io))
    intro_rect = string_rendered.get_rect()
    intro_rect.top = HEIGHT / 2 - intro_rect.height / 2
    intro_rect.x = WIDTH / 2 - intro_rect.width / 2
    screen.blit(string_rendered, intro_rect)

    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            terminate()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_y, tile_height * pos_x)
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = self.image
        self.sprite.rect = self.rect
        all_sprites.add(self.sprite)
        tiles_group.add(self.sprite)
        all_sprites.remove(list(all_sprites)[-1])
        tiles_group.remove(list(tiles_group)[-1])


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.frames = []
        self.cut_sheet(player_image, 3, 1)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.img_right = self.frames
        self.img_left = [pygame.transform.flip(image, True, False) for image in self.img_right]
        self.img_up = [pygame.transform.rotate(image, 90) for image in self.img_right]
        self.img_down = [pygame.transform.flip(image, False, True) for image in self.img_up]
        self.rect = self.rect.move(tile_width * pos_y + 5, tile_height * pos_x + 4)
        self.pos = [pos_y, pos_x]
        self.d_pos = [0, 0]
        self.dir = [0, 0]
        self.current_time = 0
        self.anim_time = 1

        sprite = pygame.sprite.Sprite()
        sprite.image = self.image
        colorkey = self.image.get_at((0, 0))
        self.image.set_colorkey(colorkey)
        sprite.rect = self.rect
        all_sprites.add(sprite)
        player_group.add(sprite)
        player_group.remove(list(player_group)[-1])
        all_sprites.remove(list(all_sprites)[-1])

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def go(self, event):
        global eat_cnt
        p_x, p_y = self.pos
        self.d_pos = [0, 0]
        ch = None
        if event.key == pygame.K_UP:  # up
            ch = get_ch(p_x, p_y - 1)
            if ch in '.-':
                self.d_pos[1] -= 1
        elif event.key == pygame.K_DOWN:  # down
            ch = get_ch(p_x, p_y + 1)
            if ch in '.-':
                self.d_pos[1] += 1
        elif event.key == pygame.K_RIGHT:  # right
            ch = get_ch(p_x + 1, p_y)
            if ch in '.-':
                self.d_pos[0] += 1
        elif event.key == pygame.K_LEFT:  # left
            ch = get_ch(p_x - 1, p_y)
            if ch in '.-':
                self.d_pos[0] -= 1
        if ch is not None and self.d_pos != [0, 0]:
            if ch == '.':
                eat_cnt -= 1
                xx, yy = (p_x + player.d_pos[0]) % level_x, (p_y + player.d_pos[1]) % level_y
                all_sprites.remove(game_spr_map[xx][yy].sprite)
                tiles_group.remove(game_spr_map[xx][yy].sprite)
                game_spr_map[xx][yy].kill()
                game_spr_map[xx][yy] = Tile('empty', yy, xx)
            change_ch(p_x, p_y, '-')
            change_ch(p_x + self.d_pos[0], p_y + self.d_pos[1], '@')
        self.dir = self.d_pos

    def update(self, dt):
            if self.d_pos[0] > 0:
                self.frames = self.img_right
            elif self.d_pos[0] < 0:
                self.frames = self.img_left
            elif self.d_pos[1] > 0:
                self.frames = self.img_down
            elif self.d_pos[1] < 0:
                self.frames = self.img_up

            dy, dx = 0, 0

            self.pos[0] += self.d_pos[0]
            self.pos[1] += self.d_pos[1]

            if self.pos[0] < 0:
                self.pos[0] = level_x - 1
                dx = level_x * tile_width
            if self.pos[1] < 0:
                self.pos[1] = level_y - 1
                dy = level_y * tile_height
            if self.pos[0] >= level_x:
                self.pos[0] = 0
                dx = -level_x * tile_width
            if self.pos[1] >= level_y:
                self.pos[1] = 0
                dy = level_y * tile_height

            self.rect.move_ip(self.d_pos[0] * tile_width + dx, self.d_pos[1] * tile_height + dy)

            self.d_pos = [0, 0]
            self.current_time += dt
            if self.current_time >= self.anim_time:
                self.current_time = 0
                self.cur_frame = (self.cur_frame + 1) % len(self.frames)

            self.image = self.frames[self.cur_frame]


class Spirit(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, color, ind):
        global speedy_ind
        super().__init__(player_group, all_sprites)
        self.frames = []
        image = load_image('sprt.png')
        self.cut_sheet(image, 8, 4, color)
        self.color = color
        self.image = self.frames[0]
        self.img_right = self.frames[0]
        self.img_left = self.frames[2]
        self.img_up = self.frames[4]
        self.img_down = self.frames[6]
        self.rect = self.rect.move(tile_width * pos_y + 5, tile_height * pos_x + 4)
        self.pos = [pos_y, pos_x]
        self.prev_pos = [-1, -1]
        self.is_active = False
        self.d_pos = [0, 0]
        self.current_time = 0
        self.anim_time = 2.5

        if color % 4 == 0:
            self.select_point = self.point_to0
            self.run_up = [20, -1]
            speedy_ind = ind
            self.is_active = True
        elif color % 4 == 1:
            self.select_point = self.point_to1
            self.run_up = [-1, -1]
            self.is_active = True
        elif color % 4 == 2:
            self.select_point = self.point_to2
            self.run_up = [20, 20]
        elif color % 4 == 3:
            self.select_point = self.point_to3
            self.run_up = [-1, 20]
        self.point_to = self.run_up

        sprite = pygame.sprite.Sprite()
        sprite.image = self.image
        colorkey = self.image.get_at((0, 0))
        self.image.set_colorkey(colorkey)
        sprite.rect = self.rect
        all_sprites.add(sprite)
        player_group.add(sprite)
        player_group.remove(list(player_group)[-1])
        all_sprites.remove(list(all_sprites)[-1])

    def cut_sheet(self, sheet, columns, rows, color):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for i in range(columns):
            frame_location = (self.rect.w * i, self.rect.h * color)
            self.frames.append(sheet.subsurface(pygame.Rect(
                frame_location, self.rect.size)))

    def update(self, dt):
        if not self.is_active:
            return

        global game_state
        self.current_time += dt
        if self.current_time >= self.anim_time:
            self.current_time = 0
            self.go()
            self.prev_pos[0] = self.pos[0]
            self.prev_pos[1] = self.pos[1]
            self.pos[0] += self.d_pos[0]
            self.pos[1] += self.d_pos[1]

            if get_ch(*self.pos) == '@':
                game_state = 3

            if self.d_pos[0] > 0:
                self.image = self.img_right
            elif self.d_pos[0] < 0:
                self.image = self.img_left
            elif self.d_pos[1] > 0:
                self.image = self.img_down
            elif self.d_pos[1] < 0:
                self.image = self.img_up

            dx, dy = 0, 0
            if self.pos[0] < 0:
                self.pos[0] = level_x - 1
                dx = level_x * tile_width
            if self.pos[1] < 0:
                self.pos[1] = level_y - 1
                dy = level_y * tile_height
            if self.pos[0] >= level_x:
                self.pos[0] = 0
                dx = -level_x * tile_width
            if self.pos[1] >= level_y:
                self.pos[1] = 0
                dy = level_y * tile_height
            self.rect.move_ip(self.d_pos[0] * tile_width + dx, self.d_pos[1] * tile_height + dy)
            self.d_pos = [0, 0]

    def go(self):
        if get_ch(*self.pos) in list('0123'):
            self.point_to = [7, 8]
        goes = [(self.pos[0] - 1, self.pos[1]), (self.pos[0] + 1, self.pos[1]), (self.pos[0], self.pos[1] - 1), (self.pos[0], self.pos[1] + 1)]
        invalid = set()
        invalid.add((self.prev_pos[0], self.prev_pos[1]))
        for i in goes:
            if not valid_coord(*i):
                invalid.add(i)
        cc = list(set(goes) - invalid)
        cc_len = 10000
        pos_to = None
        for i in cc:
            k = (i[0] - self.point_to[0]) ** 2 + (i[1] - self.point_to[1]) ** 2
            if k < cc_len:
                cc_len = k
                pos_to = i
        if pos_to is not None:
            self.d_pos = [pos_to[j] - self.pos[j] for j in range(2)]

    def point_to0(self):
        return player.pos

    def point_to1(self):
        return [player.pos[i] + player.dir[i] * 4 for i in range(2)]

    def point_to2(self):
        return [(spirits[spirits_ind[0]].pos[i] + player.pos[i] + player.dir[i] * 2) * 2 for i in range(2)]

    def point_to3(self):
        if (self.pos[0] - player.pos[0]) ** 2 + (self.pos[1] - player.pos[1]) ** 2 < 16:
            return player.pos
        return self.run_up


def spirits_control(dt):
    if max_eat - eat_cnt > 30 and not spirits[spirits_ind[2]].is_active:
        spirits[spirits_ind[2]].is_active = True
    if eat_cnt < max_eat * 2 / 3 and not spirits[spirits_ind[3]].is_active:
        spirits[spirits_ind[3]].is_active = True
        spirits[spirits_ind[3]].point_to = spirits[spirits_ind[3]].run_up
        spirits[spirits_ind[3]].update(dt)
    tt = pygame.time.get_ticks() - time_start
    if tt < 7000 or 2700 < tt < 34000 or 54000 < tt < 59000 or 79000 < tt < 83000:
        for sp in spirits:
            sp.point_to = sp.run_up
            sp.update(dt)
    else:
      
        for sp in spirits:
            sp.point_to = sp.select_point()
            sp.update(dt)


def generate_level(level):
    global all_sprites, tiles_group, player_group, eat_cnt
    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    new_player, x, y = None, None, None
    mm = []
    ss = []
    ss1 = dict()
    for y in range(len(level)):
        mm1 = []
        for x in range(len(level[y])):
            if level[x][y] in '.+':
                mm1 += [Tile('dot', x, y)]
                level[x][y] = '.'
                eat_cnt += 1
            elif level[x][y] == '#':
                mm1 += [Tile('wall', x, y)]
            elif level[x][y] == '@':
                mm1 += [Tile('empty', x, y)]
                new_player = Player(x, y)
            elif level[x][y] in '0123':
                mm1 += [Tile('empty', x, y)]
                eat_cnt += 1
                ss1[int(level[x][y]) % 4] = len(ss)
                ss += [Spirit(x, y, int(level[x][y]) % 4, len(ss))]
        mm += [mm1]
    all_sprites.draw(screen)
    return new_player, x + 1, y + 1, mm, ss, ss1


def game_step(dt):
    global player, game_map, game_spr_map, all_sprites, tiles_group, eat_cnt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                terminate()
            else:
                player.go(event)

    player.update(dt)
    screen.fill((0, 0, 0))
    tiles_group.draw(screen)
    player_group.draw(screen)
    line = "Eat left: " + str(eat_cnt)
    font = pygame.font.Font(None, 30)
    io = 'white'
    string_rendered = font.render(line, 1, pygame.Color(io))
    intro_rect = string_rendered.get_rect()
    intro_rect.top = HEIGHT - intro_rect.height
    intro_rect.x = 0
    screen.blit(string_rendered, intro_rect)


all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
tile_images = {'wall': load_image('box.png'), 'empty': load_image('grass.png'), 'dot': load_image('dot.png')}
player_image = load_image('pac.png')
tile_width = tile_height = 25
game_state = 1
eat_cnt = 0
game_map = load_level('map.txt')    # y x
player, level_x, level_y, game_spr_map, spirits, spirits_ind = generate_level(game_map)
max_eat = eat_cnt
time_start = 0

while True:
    dt = clock.tick(FPS) / 100
    if game_state == 1:
        start_screen()
        time_start = pygame.time.get_ticks()
    elif game_state == 2:
        game_step(dt)
        spirits_control(dt)
    elif game_state == 3:
        game_over_screen()  # game_over_screen1()
    if eat_cnt == 0:
        game_win_screen()

    pygame.display.flip()
    clock.tick(FPS)
