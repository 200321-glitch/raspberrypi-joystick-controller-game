from ursina import *
import random
from smbus2 import SMBus  # For I2C
from ursina.shaders import unlit_shader

# ========= CONFIG =========
PCF8591_ADDR = 0x48       # check with `i2cdetect -y 1`
USE_APPLE_SPRITE = False  # True => flat sprite; False => textured cube
APPLE_TEXTURE_PATH = 'apple.png'  # put apple.png in same folder
# =========================

# ---------- PCF8591 helper ----------
class PCF8591:
    def __init__(self, addr=0x48, bus_num=1):
        self.addr = addr
        self.bus = SMBus(bus_num)
        self.ctrl = 0x40  # analog input enable

    def read_ain(self, ch: int) -> int:
        if not 0 <= ch <= 3:
            raise ValueError("Channel must be 0..3")
        self.bus.write_byte(self.addr, self.ctrl | ch)
        self.bus.read_byte(self.addr)  # dummy
        return self.bus.read_byte(self.addr)

    def close(self):
        self.bus.close()

def map_unit_255(v: int) -> float:
    """Map 0..255 to -1..+1"""
    return (v - 128) / 127.0

# ---------- Game setup ----------
app = Ursina()
Entity.default_shader = unlit_shader

background = Entity(
    parent=scene,
    model='quad',
    texture='background4_0.png',  # your background
    rotation_x=90,
    scale=(20, 12),
    y=-0.01
)

# Bounds & motion
BOUND_X = 8
BOUND_Z = 4.5
BASE_SPEED = 0.12
GAIN_J1 = 1.6
GAIN_J2 = 1.6
DEADZONE = 0.15

# Load textures
def try_load(path):
    try:
        return load_texture(path)
    except Exception:
        return None

p1_tex = try_load('p11')
p2_tex = try_load('p22')
apple_tex = try_load(APPLE_TEXTURE_PATH)

# ---------- PCF8591 joystick ----------
adc = PCF8591(addr=PCF8591_ADDR)

INVERT_Y_J1 = True
INVERT_Y_J2 = True

def read_joystick_pair():
    # J1: AIN0=X, AIN1=Y
    j1x_raw = adc.read_ain(0)
    j1y_raw = adc.read_ain(1)
    j1x = map_unit_255(j1x_raw)
    j1y = map_unit_255(j1y_raw)
    if INVERT_Y_J1: j1y = -j1y
    if abs(j1x) < DEADZONE: j1x = 0.0
    if abs(j1y) < DEADZONE: j1y = 0.0

    # J2: AIN2=X, AIN3=Y
    j2x_raw = adc.read_ain(2)
    j2y_raw = adc.read_ain(3)
    j2x = map_unit_255(j2x_raw)
    j2y = map_unit_255(j2y_raw)
    if INVERT_Y_J2: j2y = -j2y
    if abs(j2x) < DEADZONE: j2x = 0.0
    if abs(j2y) < DEADZONE: j2y = 0.0

    return (j1x, j1y), (j2x, j2y)

# ---------- UI / pre-game ----------
input_panel = Entity(parent=camera.ui, enabled=True)
title = Text("Enter Player Names", y=.4, scale=2, parent=input_panel)

p1_label_t = Text("Player 1:", x=-.3, y=.2, parent=input_panel)
p1_input = InputField(default_value="Player 1", x=0.1, y=.2,
                      limit_content_to="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ",
                      parent=input_panel)

p2_label_t = Text("Player 2:", x=-.3, y=.0, parent=input_panel)
p2_input = InputField(default_value="Player 2", x=0.1, y=.0,
                      limit_content_to="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ",
                      parent=input_panel)

start_btn = Button(text="Start Game", y=-.3, scale=(.3,.1), parent=input_panel)

# ---------- Game entities ----------
game_entities = []

player1 = Entity(model='cube', position=(-2,0,0), collider='box', enabled=False,
                 texture=p1_tex if p1_tex else None, texture_rotation=90)
label1  = Text(text='', origin=(0,0), scale=1.5, enabled=False)

player2 = Entity(model='cube', position=(2,0,0), collider='box', enabled=False,
                 texture=p2_tex if p2_tex else None, texture_rotation=90)
label2  = Text(text='', origin=(0,0), scale=1.5, enabled=False)

game_entities += [player1, label1, player2, label2]

camera.position = (0, 20, -0.1)
camera.rotation_x = 90

# UI
game_over_text = Text(text='Game Over! Press R to Restart', origin=(0,0), scale=2, color=color.red,
                      visible=False, enabled=False)
timer_text = Text(text='60', position=(0.85, 0.45), scale=2, color=color.black, enabled=False)
score_text = Text(text='', position=(0, 0.45), origin=(0,0), scale=2, color=color.black, enabled=False)
game_entities += [game_over_text, timer_text, score_text]

# Game vars
game_time = 60
score1 = 0
score2 = 0
apples = []
APPLE_COUNT = 2

def spawn_apple():
    x = random.uniform(-BOUND_X + 0.5, BOUND_X - 0.5)
    z = random.uniform(-BOUND_Z + 0.5, BOUND_Z - 0.5)
    if apple_tex:
        apple = Entity(model='sphere', texture=apple_tex,
                       position=(x, 0, z),
                       scale=0.5, collider='box')
    else:
        apple = Entity(model='sphere', color=color.red,
                       position=(x, 0, z), scale=0.4, collider='box')
    apples.append(apple)
    game_entities.append(apple)

def spawn_initial_apples():
    for a in apples:
        destroy(a)
    apples.clear()
    for _ in range(APPLE_COUNT):
        spawn_apple()

def restart_game():
    global game_time, score1, score2
    player1.position = (-2, 0, 0)
    player2.position = (2, 0, 0)
    game_time = 60
    score1 = 0
    score2 = 0
    spawn_initial_apples()
    update_score_text()
    timer_text.text = str(int(game_time))
    game_over_text.visible = False

def keep_inside_bounds(entity):
    entity.x = max(-BOUND_X, min(BOUND_X, entity.x))
    entity.z = max(-BOUND_Z, min(BOUND_Z, entity.z))

def update_score_text():
    score_text.text = f"{label1.text}: {score1}   {label2.text}: {score2}"

# ---------- Game loop ----------
def update():
    global game_time, score1, score2
    if not player1.enabled:
        return

    label1.position = (player1.x, player1.y + 1.5, player1.z)
    label2.position = (player2.x, player2.y + 1.5, player2.z)

    if game_over_text.visible:
        if held_keys['r']:
            restart_game()
        return

    game_time -= time.dt
    timer_text.text = str(int(game_time))
    if game_time <= 0:
        game_over_text.text = 'Time Up! Press R to Restart'
        game_over_text.visible = True
        return

    (j1x, j1y), (j2x, j2y) = read_joystick_pair()
    player1.x += j1x * BASE_SPEED * GAIN_J1
    player1.z += j1y * BASE_SPEED * GAIN_J1
    player2.x += j2x * BASE_SPEED * GAIN_J2
    player2.z += j2y * BASE_SPEED * GAIN_J2

    keep_inside_bounds(player1)
    keep_inside_bounds(player2)

    for apple in apples[:]:
        if player1.intersects(apple).hit:
            score1 += 1
            update_score_text()
            apples.remove(apple); destroy(apple); spawn_apple()
        elif player2.intersects(apple).hit:
            score2 += 1
            update_score_text()
            apples.remove(apple); destroy(apple); spawn_apple()

    if player1.intersects(player2).hit:
        game_over_text.text = 'Game Over! Press R to Restart'
        game_over_text.visible = True

def start_game():
    input_panel.enabled = False
    for e in game_entities:
        e.enabled = True

    p1_name = p1_input.text.strip() or "Player 1"
    p2_name = p2_input.text.strip() or "Player 2"
    label1.text = p1_name
    label2.text = p2_name

    global score1, score2, game_time
    score1 = 0
    score2 = 0
    game_time = 60
    timer_text.enabled = True
    score_text.enabled = True
    game_over_text.enabled = True

    update_score_text()
    spawn_initial_apples()

start_btn.on_click = start_game

def input(key):
    if key == 'r' and player1.enabled:
        restart_game()

def on_application_quit():
    try:
        adc.close()
    except:
        pass

app.run()
