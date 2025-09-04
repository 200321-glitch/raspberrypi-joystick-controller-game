from ursina import *
import random
import os, glob
from smbus2 import SMBus   # pip install smbus2

# ========= CONFIG =========
PCF8591_ADDR = 0x48       # change if i2cdetect shows e.g. 0x49
USE_APPLE_SPRITE = False  # True => flat sprite; False => textured cube
DOWNLOADS_DIR = '/home/sahisa/Downloads'
# =========================

# ------------ PCF8591 helper ------------
class PCF8591:
    def __init__(self, addr=0x48, bus_num=1):
        self.addr = addr
        self.bus = SMBus(bus_num)
        self.ctrl = 0x40  # analog input enable

    def read_ain(self, ch: int) -> int:
        """Read channel 0..3, returns 0..255"""
        if not 0 <= ch <= 3:
            raise ValueError("PCF8591 channel must be 0..3")
        self.bus.write_byte(self.addr, self.ctrl | ch)
        self.bus.read_byte(self.addr)          # dummy after channel change
        return self.bus.read_byte(self.addr)   # real value

    def close(self):
        self.bus.close()

def map_unit_255(v: int) -> float:
    """Map 0..255 to -1..+1"""
    return (v - 128) / 127.0

# ------------ helpers ------------
def find_apple_texture_path() -> str | None:
    """Look in ~/Downloads for any image named apple.* or *apple*.*"""
    patterns = [
        os.path.join(DOWNLOADS_DIR, 'apple.*'),
        os.path.join(DOWNLOADS_DIR, '*apple*.*'),
        os.path.join(DOWNLOADS_DIR, '*Apple*.*'),
    ]
    candidates = []
    for pat in patterns:
        candidates.extend(glob.glob(pat))
    # filter by common image extensions and pick the first
    for p in sorted(candidates):
        if p.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.webp')):
            return p
    return None

def try_load(path):
    if not path:
        return None
    try:
        return load_texture(path)
    except Exception:
        return None

# ------------ Game setup ------------
app = Ursina()
window.color = color.green

# Bounds & motion
BOUND_X = 8
BOUND_Z = 4.5
BASE_SPEED = 0.12
GAIN_J1 = 1.6
GAIN_J2 = 1.6
DEADZONE = 0.15

# Optional player textures (keep as before; remove or change if needed)
p1_tex = try_load('IMG_5032.png')  # optional
p2_tex = try_load('IMG_7939.png')  # optional

# Find & load apple texture from Downloads
APPLE_TEXTURE_PATH = find_apple_texture_path()
apple_tex = try_load(APPLE_TEXTURE_PATH)

if apple_tex:
    print(f'[INFO] Using apple texture: {APPLE_TEXTURE_PATH}')
else:
    print('[INFO] No apple image found in /home/sahisa/Downloads (falling back to red cube)')

# ADC instance
adc = PCF8591(addr=PCF8591_ADDR)

# --- Pre-game name input UI ---
input_panel = Entity(parent=camera.ui, enabled=True)
title = Text("Enter Player Names", y=.4, scale=2, parent=input_panel)

p1_label_t = Text("Player 1:", x=-.3, y=.2, parent=input_panel)
p1_input = InputField(
    default_value="Player 1",
    x=0.1, y=.2,
    limit_content_to="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ",
    parent=input_panel
)

p2_label_t = Text("Player 2:", x=-.3, y=.0, parent=input_panel)
p2_input = InputField(
    default_value="Player 2",
    x=0.1, y=.0,
    limit_content_to="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ",
    parent=input_panel
)

start_btn = Button(text="Start Game", y=-.3, scale=(.3,.1), parent=input_panel)

# --- Game entities (hidden until start) ---
game_entities = []

player1 = Entity(model='cube', position=(-2,0,0), collider='box', enabled=False,
                 texture=p1_tex if p1_tex else None, texture_rotation=90)
label1  = Text(text='', origin=(0,0), scale=1.5, enabled=False)

player2 = Entity(model='cube', position=( 2,0,0), collider='box', enabled=False,
                 texture=p2_tex if p2_tex else None, texture_rotation=90)
label2  = Text(text='', origin=(0,0), scale=1.5, enabled=False)

game_entities += [player1, label1, player2, label2]

# Camera
camera.position = (0, 20, -0.1)
camera.rotation_x = 90

# UI
game_over_text = Text(text='Game Over! Press R to Restart',
                      origin=(0,0), scale=2, color=color.red,
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

INVERT_Y_J1 = True
INVERT_Y_J2 = True

def spawn_apple():
    x = random.uniform(-BOUND_X + 0.5, BOUND_X - 0.5)
    z = random.uniform(-BOUND_Z + 0.5, BOUND_Z - 0.5)

    if apple_tex:
        if USE_APPLE_SPRITE:
            apple = Entity(
                model='quad', texture=apple_tex,
                position=(x, 0, z),
                scale=0.8,
                collider='box',
                double_sided=True
            )
        else:
            apple = Entity(
                model='cube', texture=apple_tex,
                position=(x, 0, z),
                scale=0.5,
                collider='box'
            )
    else:
        # Fallback if texture missing
        apple = Entity(
            model='cube', color=color.red,
            position=(x, 0, z),
            scale=0.4,
            collider='box'
        )
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
    player2.position = ( 2, 0, 0)
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

def update():
    global game_time, score1, score2
    if not player1.enabled:  # game not started yet
        return

    # labels follow players
    label1.position = (player1.x, player1.y + 1.5, player1.z)
    label2.position = (player2.x, player2.y + 1.5, player2.z)

    if game_over_text.visible:
        if held_keys['r']:
            restart_game()
        return

    # timer
    game_time -= time.dt
    timer_text.text = str(int(game_time))
    if game_time <= 0:
        game_over_text.text = 'Time Up! Press R to Restart'
        game_over_text.visible = True
        return

    # ----- Both players via two joysticks on one PCF8591 -----
    (j1x, j1y), (j2x, j2y) = read_joystick_pair()
    player1.x += j1x * BASE_SPEED * GAIN_J1
    player1.z += j1y * BASE_SPEED * GAIN_J1
    player2.x += j2x * BASE_SPEED * GAIN_J2
    player2.z += j2y * BASE_SPEED * GAIN_J2

    keep_inside_bounds(player1)
    keep_inside_bounds(player2)

    # apples
    for apple in apples[:]:
        if player1.intersects(apple).hit:
            score1 += 1
            update_score_text()
            apples.remove(apple); destroy(apple); spawn_apple()
        elif player2.intersects(apple).hit:
            score2 += 1
            update_score_text()
            apples.remove(apple); destroy(apple); spawn_apple()

    # collision
    if player1.intersects(player2).hit:
        game_over_text.text = 'Game Over! Press R to Restart'
        game_over_text.visible = True

def start_game():
    # Hide input panel, show game
    input_panel.enabled = False
    for e in game_entities:
        e.enabled = True

    # Names
    p1_name = p1_input.text.strip() or "Player 1"
    p2_name = p2_input.text.strip() or "Player 2"
    label1.text = p1_name
    label2.text = p2_name

    # Reset game state
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
    except Exception:
        pass

app.run()
